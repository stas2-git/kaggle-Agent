---
name: extract-pdf-text
description: >
  Extract text from PDF documents using native text extraction (pdfplumber/pymupdf) and robust OCR fallback (pytesseract) with image preprocessing.
metadata:
  author: Kaggle Student
  license: MIT
  version: 1.0.0
  requires:
    bins:
      - tesseract
    python:
      - pdfplumber
      - pymupdf
      - pytesseract
      - Pillow
---

# Extract PDF Text Skill

This skill provides a robust, production-grade utility to extract text from PDF documents. It uses a tiered strategy to ensure maximum yield:
1. **Direct Native Extraction** using `pdfplumber` (fast, structured).
2. **Page-by-Page PyMuPDF Extraction** (`pymupdf`/`fitz`) as a secondary native parser.
3. **Advanced OCR Fallback** using `pytesseract` with 300 DPI page rendering and PIL image enhancement (grayscale conversion, contrast/sharpness boosting, and median noise filtering).

## Requirements

### System Dependencies (macOS)
Install Tesseract OCR via Homebrew:
```bash
brew install tesseract
```

### Python Dependencies
Install the required packages in your environment:
```bash
pip install pdfplumber pymupdf pytesseract Pillow
```

## How to Use

The script `extract_pdf_text.py` can process a single PDF or recursively scan a directory:

### Single PDF File
```bash
python scripts/extract_pdf_text.py --input path/to/document.pdf --output path/to/output.txt
```

### Directory of PDFs
```bash
python scripts/extract_pdf_text.py --input path/to/pdf_folder --output path/to/output_folder
```

### Command Options
- `--input`: Path to the input PDF file or directory.
- `--output`: Path to the output TXT file or directory.
- `--max-chars`: Maximum number of characters to extract (default: `15000` to fit context windows).
- `--min-chars`: Minimum number of characters required to save a result (default: `100`).
- `--timeout`: Maximum seconds allowed to process a single page (default: `30`).
- `--tesseract-path`: Explicit path to the `tesseract` binary (if not in system PATH).

## Extraction Logic

1. **Junk Filtering**: Skips documents matching common non-informative names (e.g., answer keys, candidates lists).
2. **Tiered Extraction**:
   * First, attempts document-wide native text extraction with `pdfplumber`.
   * If native extraction yields less than 200 characters, it switches to page-by-page processing with `PyMuPDF`.
   * If a page has native text (> 50 chars), it keeps it. Otherwise, it renders the page at 300 DPI, enhances contrast/sharpness, applies a median noise filter, and performs OCR.
3. **Smart Excerpting**: Truncates output to `--max-chars` but prioritizes structural sections (Abstract, Introduction, Methodology, Conclusion) by scoring lines and keeping them near the top.
