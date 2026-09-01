# ============================================================
# ATHENA — COUNSELLOR-FACING TRANSLATION
# ============================================================

"""
English rendering of a report that was filed in another language, so a
counsellor can read a case they'd otherwise have to hand to someone
else -- or worse, act on without really understanding.

This is a READING AID, not a replacement for the reporter's own words.
Two rules follow from that, and both are enforced by callers rather
than assumed:

  1. The original text is always kept and always shown. Nothing here
     overwrites original_text; the translation is stored in its own
     column alongside it.
  2. Anything produced here is labelled as machine translation
     wherever it appears. A counsellor deciding how serious a case is
     needs to know which words are the reporter's and which are a
     model's paraphrase of them -- the same reasoning behind the
     "suggested, not final" labelling on the AI sections of the case
     brief.

Reuses response_engine.generate_response(), so translation inherits
the same Groq -> Gemini -> OpenRouter fallback chain as everything
else. One provider being down or unfunded degrades translation the
same way it degrades generation, and there's no second set of keys to
keep alive.

Deliberately NOT run at report time: it would add a second model call
to the wait of somebody in distress, for output only a counsellor
ever reads. It runs the first time a case brief is actually opened,
and the result is cached on the case so it only ever happens once.
"""

from response_engine import generate_response

# Reports already in English need no translation, and neither does an
# empty/failed transcript. Kept as a set so the check reads the same
# way at both call sites.
SKIP_LANGUAGES = {"en", "eng", "english"}


def _build_translation_prompt(text, source_language=None):
    """
    A deliberately narrow instruction. The model is being asked to
    translate a distress report, not to interpret, summarise, soften,
    or advise on it -- Athena already has a separate, grounded path
    for anything resembling advice, and a translation that quietly
    "cleans up" what someone said in crisis destroys exactly the
    detail a counsellor is reading for.
    """

    language_hint = (
        f"The text is written in {source_language}. "
        if source_language else ""
    )

    return (
        "You are translating a report made to a helpline into English "
        "for a counsellor who does not read the original language.\n\n"
        f"{language_hint}"
        "Rules:\n"
        "- Translate as literally as the language allows. Keep the "
        "speaker's own tone, hesitation, and word choice.\n"
        "- Do NOT soften, summarise, censor, or tidy the content. "
        "Distress, anger, and explicit detail must survive translation "
        "intact -- a counsellor is reading this to judge severity.\n"
        "- Do NOT add commentary, interpretation, warnings, or advice.\n"
        "- Do NOT guess at anything the text does not say. If part of "
        "it is unclear or untranscribable, render it as [unclear] "
        "rather than inventing a plausible reading.\n"
        "- Output the English translation and nothing else.\n\n"
        "Report:\n"
        f"{text}"
    )


def translate_to_english(text, source_language=None):
    """
    Returns an English translation of `text`, or None.

    None is returned for anything not worth translating (empty text,
    a report already in English) and for a genuine provider failure.
    None specifically means "no translation available" -- callers must
    fall back to showing the original alone, never to showing an
    untranslated string labelled as a translation.

    Never raises: a translation that failed must not be able to take
    down the case brief a counsellor is trying to open. A failure here
    costs a convenience, and the original text -- the authoritative
    version -- is right there either way.
    """

    if not text or not text.strip():
        return None

    if source_language and source_language.strip().lower() in SKIP_LANGUAGES:
        return None

    try:
        translated = generate_response(
            _build_translation_prompt(text, source_language)
        )

    except Exception as e:
        print(f"[translation] failed: {type(e).__name__}: {e}")
        return None

    if not translated or not translated.strip():
        return None

    return translated.strip()
