#!/usr/bin/env python3

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import objc
import Vision
from PIL import Image


@dataclass
class OcrResult:
    text: str
    confidence: float
    bbox: tuple[float, float, float, float]


def pil_to_bytes(pil_image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()


def load_image(image: str | Path | Image.Image) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    return Image.open(image)


def vision_bbox_to_pixels(
    bbox: tuple[float, float, float, float], image_width: int, image_height: int
) -> tuple[int, int, int, int]:
    x, y, w, h = bbox
    x1 = x * image_width
    y2 = (1 - y) * image_height
    x2 = x1 + w * image_width
    y1 = y2 - h * image_height
    return round(x1), round(y1), round(x2), round(y2)


def text_from_image(
    image: str | Path | Image.Image,
    recognition_level: str = "accurate",
    confidence_threshold: float = 0.0,
    language_preference: Optional[list[str]] = None,
) -> list[OcrResult]:
    pil_image = load_image(image)
    if recognition_level not in {"accurate", "fast"}:
        raise ValueError("recognition_level must be 'accurate' or 'fast'")

    if language_preference is not None and not isinstance(language_preference, list):
        raise ValueError("language_preference must be a list of language codes")

    with objc.autorelease_pool():
        request = Vision.VNRecognizeTextRequest.alloc().init()
        request.setRecognitionLevel_(0 if recognition_level == "accurate" else 1)

        if language_preference:
            available_languages = request.supportedRecognitionLanguagesAndReturnError_(None)[0]
            if not set(language_preference).issubset(set(available_languages)):
                raise ValueError(
                    f"language_preference must be a subset of {available_languages}"
                )
            request.setRecognitionLanguages_(language_preference)

        handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(
            pil_to_bytes(pil_image), None
        )

        ret = handler.performRequests_error_([request], None)
        if isinstance(ret, tuple):
            ok, err = ret
        else:
            ok, err = bool(ret), None

        if not ok or err is not None:
            return []

        results: list[OcrResult] = []
        for result in request.results():
            confidence = float(result.confidence())
            if confidence < confidence_threshold:
                continue
            bbox = result.boundingBox()
            results.append(
                OcrResult(
                    text=str(result.text()),
                    confidence=confidence,
                    bbox=(
                        float(bbox.origin.x),
                        float(bbox.origin.y),
                        float(bbox.size.width),
                        float(bbox.size.height),
                    ),
                )
            )
        return results
