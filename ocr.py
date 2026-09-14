# ============================================================
# ATHENA — EVIDENCE OCR
# ============================================================

"""
Extracts text from an uploaded screenshot (e.g. threatening
WhatsApp/SMS messages) so it can be run through the exact same
pipeline as a typed report.

EasyOCR readers are lazily created on first use, so we only pay for
the language actually requested instead of all five at startup, and
only the most recent one is kept loaded (see _get_reader).

EasyOCR generally can't mix two non-Latin scripts in one reader,
so each Indian language gets paired with English instead of with
another -- screenshots are usually one script plus incidental
Latin (emoji labels, timestamps, app UI text, etc.) anyway. Urdu
is read by EasyOCR's Arabic-script model, which covers Urdu.
"""

import easyocr

_READERS = {}

# One entry per language in understanding.SUPPORTED_LANGUAGES
# (tests/test_ocr.py holds the two in step). A language missing here
# silently falls back to the English reader, which returns nothing
# useful for a non-Latin screenshot.
_READER_LANGUAGES = {
    "en": ["en"],
    "hi": ["hi", "en"],
    "te": ["te", "en"],
    "ur": ["ur", "en"],
    "bn": ["bn", "en"],
}


def _get_reader(language):

    language = language if language in _READER_LANGUAGES else "en"

    if language not in _READERS:
        # One reader loaded at a time. Each carries its own copy of the
        # text detector (~80MB) plus a recogniser (the Arabic-script one
        # Urdu uses is ~215MB), and the hosted container is memory-
        # capped: five cached readers is enough to get it killed, the
        # same way voice features were. Switching language costs a
        # reload from disk, not a crash.
        _READERS.clear()
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
