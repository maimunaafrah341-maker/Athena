"""
Photo evidence has to be readable in every language Athena supports.

A language missing from ocr._READER_LANGUAGES does not fail loudly: it
falls back to the English reader, which returns nothing useful for an
Urdu or Bengali screenshot, and the reporter is told no text was found.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module  # noqa: E402
import ocr  # noqa: E402
from understanding import SUPPORTED_LANGUAGES  # noqa: E402


@pytest.mark.parametrize("language", sorted(SUPPORTED_LANGUAGES))
def test_every_supported_language_has_an_ocr_reader(language):
    assert language in ocr._READER_LANGUAGES


@pytest.mark.parametrize("language", sorted(ocr._READER_LANGUAGES))
def test_each_reader_is_one_script_plus_english(language):
    # EasyOCR cannot mix two non-Latin scripts in one reader, and the
    # English half is what reads timestamps and app labels.
    reader_languages = ocr._READER_LANGUAGES[language]
    assert reader_languages[0] == language
    assert "en" in reader_languages
    assert len(reader_languages) <= 2


@pytest.mark.parametrize(
    "caption, expected",
    [
        ("", "en"),
        ("یہ پیغام دیکھیں", "ur"),
        ("এই মেসেজটা দেখুন", "bn"),
        ("यह मैसेज देखो", "hi"),
    ],
)
def test_whatsapp_photo_reads_the_script_of_its_caption(
    monkeypatch, tmp_path, caption, expected
):
    seen = {}

    def fake_extract_text(image_bytes, language="en"):
        seen["language"] = language
        return ""

    monkeypatch.setattr(app_module, "download_media", lambda url: (b"img", "image/jpeg"))
    monkeypatch.setattr(app_module, "EVIDENCE_DIR", str(tmp_path))
    monkeypatch.setattr(ocr, "extract_text", fake_extract_text)

    reply = app_module._handle_whatsapp_media("https://example.test/m", "image/jpeg", caption)

    assert seen["language"] == expected
    assert "couldn't read any text" in reply
