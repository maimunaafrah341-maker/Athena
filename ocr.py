# ============================================================
# ATHENA — EVIDENCE OCR
# ============================================================

"""
Extracts text from an uploaded screenshot (e.g. threatening
WhatsApp/SMS messages) so it can be run through the exact same
pipeline as a typed report.

EasyOCR readers are lazily created and cached per language --
each one loads real models on first use, so we only pay for the
language actually requested instead of all three at startup.

EasyOCR generally can't mix two non-Latin scripts in one reader,
so Hindi and Telugu each get paired with English instead of with
each other -- screenshots are usually one script plus incidental
Latin (emoji labels, timestamps, app UI text, etc.) anyway.
"""

import easyocr

_READERS = {}

_READER_LANGUAGES = {
    "en": ["en"],
    "hi": ["hi", "en"],
    "te": ["te", "en"],
}


def _get_reader(language):

    language = language if language in _READER_LANGUAGES else "en"

    if language not in _READERS:
        _READERS[language] = easyocr.Reader(
            _READER_LANGUAGES[language],
            gpu=False,
        )

    return _READERS[language]


def extract_text(image_bytes, language="en"):
    """
    Run OCR on raw image bytes and return the extracted text as one
    string (reading order, newline-joined). Empty string if nothing
    was recognized.
    """

    reader = _get_reader(language)

    results = reader.readtext(image_bytes, detail=0, paragraph=True)

    return "\n".join(results).strip()
