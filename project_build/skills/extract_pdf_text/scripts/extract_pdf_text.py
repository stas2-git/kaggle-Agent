#!/usr/bin/env python
"""
PDF Text Extraction Tool
Extracts text from PDF documents using a tiered approach:
1. Native pdfplumber extraction.
2. Page-by-page PyMuPDF (fitz) native text extraction.
3. Enhanced OCR fallback using pytesseract with image preprocessing.
"""

import os
import re
import io
import argparse
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

# ─── Settings and Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(message)s"
)
log = logging.getLogger(__name__)

# Files with these substrings are skipped (junk/answer keys)
JUNK_PATTERNS = [
    "Passing Candidates",
    "Answer Key",
    "and Answers",
    "and answers",
    "Final Answers",
]

# Section patterns for prioritizing key academic/actuarial sections
SECTION_PATTERNS = [
    r"(?i)^\s*(abstract)\s*$",
    r"(?i)^\s*\d*\.?\s*(introduction)\s*$",
    r"(?i)^\s*\d+\.?\s*(methodology|methods?|model|approach|framework)\s*$",
    r"(?i)^\s*\d+\.?\s*(proposed method|the model|mathematical framework)\s*$",
    r"(?i)^\s*\d+\.?\s*(conclusion|summary|discussion)\s*$",
]


def locate_tesseract():
    """Attempt to find the Tesseract binary automatically."""
    try:
        pytesseract.get_tesseract_version()
        return None  # Tesseract is already in the system PATH
    except Exception:
        pass

    # Common search paths
    paths = [
        "/opt/homebrew/bin/tesseract",  # macOS Homebrew (Apple Silicon)
        "/usr/local/bin/tesseract",  # macOS Homebrew (Intel)
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",  # Windows default
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _long_path(p: Path) -> str:
    """Return path string; uses extended prefix on Windows to bypass MAX_PATH."""
    resolved = str(p.resolve())
    if os.name == "nt" and not resolved.startswith("\\\\?\\"):
        return "\\\\?\\" + resolved
    return resolved


def _is_junk(filename: str) -> bool:
    """Check if the filename matches any junk patterns."""
    return any(pat in filename for pat in JUNK_PATTERNS)


def score_line(line: str) -> int:
    """Return priority score for a line — higher = keep near top."""
    for pat in SECTION_PATTERNS:
        if re.match(pat, line):
            return 10
    return 0


def smart_extract(pages_text: list[str], max_chars: int) -> str:
    """
    Given a list of per-page text strings, return a prioritized excerpt:
    - Prioritizes abstract, introduction, methodology, and conclusion.
    - Appends other text up to max_chars.
    """
    full_text = "\n".join(pages_text)

    # If short enough, keep everything
    if len(full_text) <= max_chars:
        return full_text.strip()

    # Try to grab key sections first
    lines = full_text.split("\n")
    priority_blocks: list[str] = []
    normal_blocks: list[str] = []

    in_priority = False
    buffer: list[str] = []

    for line in lines:
        if score_line(line) > 0:
            if buffer:
                (priority_blocks if in_priority else normal_blocks).append(
                    "\n".join(buffer)
                )
                buffer = []
            in_priority = True
            buffer.append(line)
        else:
            # End priority section after a blank line following content
            if in_priority and line.strip() == "" and len(buffer) > 3:
                priority_blocks.append("\n".join(buffer))
                buffer = []
                in_priority = False
            else:
                buffer.append(line)

    if buffer:
        (priority_blocks if in_priority else normal_blocks).append("\n".join(buffer))

    # Assemble: priority first, then fill up to max_chars with the rest
    result = "\n\n".join(priority_blocks)
    remaining = max_chars - len(result)
    if remaining > 500:
        leftover = "\n\n".join(normal_blocks)
        result += "\n\n" + leftover[:remaining]

    # If priority parsing found nothing useful, just take the head of the doc
    if len(result.strip()) < 500:
        result = full_text[:max_chars]

    return result.strip()


def _enhance_image(img: Image.Image) -> Image.Image:
    """Apply grayscale, contrast boost, sharpening, and median filtering for OCR."""
    img = img.convert("L")  # Grayscale
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img


def _extract_page_text(doc: fitz.Document, page_num: int) -> str:
    """Extract page text using PyMuPDF native extractor, falling back to enhanced OCR."""
    page = doc[page_num]

    # Try PyMuPDF native text first
    text = page.get_text("text").strip()
    if len(text) > 50:
        return text

    # Fallback: OCR at 300 DPI with image preprocessing
    mat = fitz.Matrix(300 / 72, 300 / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
    img: Image.Image = Image.open(io.BytesIO(pix.tobytes("png")))
    img = _enhance_image(img)
    ocr_text = pytesseract.image_to_string(img, lang="eng", config="--psm 3")
    return ocr_text.strip()


def _extract_page_with_timeout(
    doc: fitz.Document, page_num: int, timeout_sec: int
) -> str | None:
    """Extract a single page's text with a thread timeout."""
    ex = ThreadPoolExecutor(max_workers=1)
    try:
        future = ex.submit(_extract_page_text, doc, page_num)
        try:
            return future.result(timeout=timeout_sec)
        except FuturesTimeoutError:
            log.warning(
                f"    Page {page_num + 1} timed out ({timeout_sec}s), skipping page"
            )
            return None
        except Exception as e:
            log.warning(f"    Page {page_num + 1} error: {e}")
            return None
    finally:
        ex.shutdown(wait=False)


def extract_pdf_document(
    pdf_path: Path, max_chars: int, min_chars: int, timeout_sec: int
) -> str | None:
    """
    Extract text from a PDF document:
    1. Try whole-document native extraction using pdfplumber.
    2. If that fails (< 200 chars), fall back to page-by-page PyMuPDF/OCR.
    """
    pages_text = []

    # Strategy 1: pdfplumber native text extraction
    try:
        with pdfplumber.open(_long_path(pdf_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
    except Exception as e:
        log.debug(f"pdfplumber failed for {pdf_path.name}: {e}")

    # If pdfplumber succeeded in finding text, use it
    full_native = "".join(pages_text)
    if len(full_native) >= 200:
        return smart_extract(pages_text, max_chars)

    # Strategy 2: Page-by-page PyMuPDF / OCR fallback
    log.info(f"  Falling back to page-by-page PyMuPDF and OCR for {pdf_path.name}")
    try:
        doc = fitz.open(_long_path(pdf_path))
    except Exception as e:
        log.warning(f"  Cannot open PDF document {pdf_path.name}: {e}")
        return None

    accumulated: list[str] = []
    total_chars = 0

    for page_num in range(len(doc)):
        if total_chars >= max_chars:
            log.info(
                f"    Reached max character limit ({max_chars}) at page {page_num + 1}"
            )
            break

        page_text = _extract_page_with_timeout(doc, page_num, timeout_sec)
        if page_text and len(page_text) > 20:
            accumulated.append(page_text)
            total_chars += len(page_text)

    doc.close()

    if not accumulated:
        return None

    result = "\n\n".join(accumulated)
    if len(result) > max_chars:
        result = result[:max_chars]

    return result if len(result) >= min_chars else None


def process_file(
    input_file: Path,
    output_file: Path,
    max_chars: int,
    min_chars: int,
    timeout_sec: int,
):
    """Process a single PDF file and write output."""
    if _is_junk(input_file.name):
        log.info(f"Skipping junk file: {input_file.name}")
        return

    log.info(f"Processing: {input_file.name}")
    text = extract_pdf_document(input_file, max_chars, min_chars, timeout_sec)

    if text:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(text, encoding="utf-8")
        log.info(
            f"  Successfully extracted {len(text)} characters to {output_file.name}"
        )
    else:
        log.warning(f"  Failed to extract usable text from: {input_file.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract text from PDF documents using native and OCR fallbacks."
    )
    parser.add_argument(
        "--input", required=True, help="Input PDF file or folder containing PDFs"
    )
    parser.add_argument(
        "--output", required=True, help="Output TXT file or folder to save outputs"
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=15000,
        help="Max characters to extract per file",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=100,
        help="Min characters required to save output",
    )
    parser.add_argument(
        "--timeout", type=int, default=30, help="Per-page timeout limit in seconds"
    )
    parser.add_argument("--tesseract-path", help="Explicit path to tesseract binary")
    args = parser.parse_args()

    # Configure tesseract path
    if args.tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = args.tesseract_path
    else:
        auto_path = locate_tesseract()
        if auto_path:
            log.info(f"Auto-configured Tesseract binary: {auto_path}")
            pytesseract.pytesseract.tesseract_cmd = auto_path

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_file():
        # Single file execution
        if not output_path.suffix:
            output_file = output_path / input_path.with_suffix(".txt").name
        else:
            output_file = output_path
        process_file(
            input_path, output_file, args.max_chars, args.min_chars, args.timeout
        )
    elif input_path.is_dir():
        # Directory execution
        output_path.mkdir(parents=True, exist_ok=True)
        pdf_files = sorted(input_path.rglob("*.pdf"))
        log.info(f"Found {len(pdf_files)} PDFs in folder {input_path}")
        for pdf_file in pdf_files:
            rel = pdf_file.relative_to(input_path)
            out_file = output_path / rel.with_suffix(".txt")
            process_file(
                pdf_file, out_file, args.max_chars, args.min_chars, args.timeout
            )
    else:
        log.error(f"Input path does not exist: {args.input}")


if __name__ == "__main__":
    main()
