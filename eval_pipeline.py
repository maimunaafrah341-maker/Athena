# ============================================================
# ATHENA — EVAL PIPELINE
# ============================================================

"""
Systematic check of understanding.py's classification quality across
languages/scripts, instead of the ad-hoc one-off testing that found
tonight's romanized-Telugu confidence gap by hand. Free and local --
no Gemini/Groq call, just the same understand() function the real
pipeline uses.

Deliberately does NOT hard-assert an expected incident_type/signal
set per case and call it "pass/fail" -- that would require correctly
predicting understanding.py's exact output for ~26 hand-written
sentences in three languages ahead of time, and a wrong prediction
would silently encode a mistake in the eval set as a fake system
failure. Instead this reports what actually happens (confidence,
incident_type, which signals fired) and flags anything under the
same confidence floors risk.py/kg.py already use to decide whether to
trust a classification -- INCIDENT_TYPE_CONFIDENCE_FLOOR and
CASTE_MOTIVE_CONFIDENCE_FLOOR, not a new arbitrary bar invented here.

Cases include both known-good and known-weak examples surfaced during
tonight's testing (see CASES below, each tagged with why it's here)
so this eval set doubles as a regression check -- rerun after any
future change to understanding.py's examples/thresholds and compare.
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from understanding import understand
from risk import INCIDENT_TYPE_CONFIDENCE_FLOOR
from kg import CASTE_MOTIVE_CONFIDENCE_FLOOR


# Each case: id, text, language, script_label (how the text was
# actually written, for reporting -- independent of what
# understanding.py itself detects as "script"), and a short note on
# why it's in the set.
CASES = [
    # ---------------- English ----------------
    ("en_dv_threat_injury", "My husband hit me and threatened to hurt me again if I told anyone.", "en", "native",
     "baseline: clear domestic violence, explicit threat + injury"),
    ("en_sexual_violence", "A man forced himself on me at a party last night.", "en", "native",
     "baseline: clear sexual violence"),
    ("en_stalking", "A man from my college has been following me home every day this week.", "en", "native",
     "baseline: clear stalking, no violence"),
    ("en_caste_public", "Someone insulted and humiliated me in public because of my caste.", "en", "native",
     "exact training-anchor phrasing for caste_based_motive"),
    ("en_caste_novel", "My landlord refused to rent me the flat once he found out my caste, and told the neighbours to keep away from me.", "en", "native",
     "novel caste_based_motive phrasing, not anchor-matched"),
    ("en_ambiguous", "I don't know what's going on, everything feels off lately and I'm scared.", "en", "native",
     "known low-confidence case -- should trigger understanding_escalation"),

    # ---------------- Hindi, native script ----------------
    ("hi_dv_threat", "मेरे पति मुझे मारते हैं और मुझे जान से मारने की धमकी देते हैं।", "hi", "native",
     "domestic violence, threat + injury, native Hindi"),
    ("hi_stalking", "एक आदमी हर दिन कॉलेज से मेरा पीछा करता है।", "hi", "native",
     "stalking, native Hindi"),
    ("hi_caste_anchor", "मेरी जाति के कारण मुझे सार्वजनिक रूप से अपमानित किया गया।", "hi", "native",
     "exact training-anchor phrasing for caste_based_motive"),
    ("hi_caste_novel", "मेरे मकान मालिक ने मेरी जाति जानने के बाद मुझे घर किराए पर देने से मना कर दिया।", "hi", "native",
     "novel caste_based_motive phrasing, native Hindi"),
    ("hi_immediate_danger", "वह अभी मेरे घर के बाहर खड़ा है और अंदर आने की धमकी दे रहा है।", "hi", "native",
     "immediate_danger, native Hindi"),

    # ---------------- Hindi, romanized ----------------
    ("hi_rom_dv_threat", "Mera pati mujhe maarta hai aur jaan se maarne ki dhamki deta hai.", "hi", "romanized",
     "domestic violence, threat + injury, romanized Hindi"),
    ("hi_rom_stalking", "Ek aadmi roz college se mera peecha karta hai.", "hi", "romanized",
     "stalking, romanized Hindi"),
    ("hi_rom_caste_anchor", "Meri jaati ke karan mujhe sarvajanik roop se apmanit kiya gaya.", "hi", "romanized",
     "exact training-anchor phrasing, romanized Hindi"),
    ("hi_rom_caste_novel", "Mere makan malik ne meri jaati jaanne ke baad ghar kiraye par dene se mana kar diya.", "hi", "romanized",
     "novel caste_based_motive phrasing, romanized Hindi -- direct romanization of hi_caste_novel"),
    ("hi_rom_whatsapp_demo", "Meri jaati ke karan mujhe mandir mein ghusne nahi diya gaya aur sabke saamne apmaanit kiya gaya. Bheed abhi mujhe ghar ke bahar ghera kiye khadi hai.", "hi", "romanized",
     "already-live case from the WhatsApp demo -- known to score SVI Critical / SC-ST Act correctly"),

    # ---------------- Telugu, native script ----------------
    ("te_dv_threat", "నా భర్త నన్ను కొడతాడు మరియు చంపేస్తానని బెదిరిస్తాడు.", "te", "native",
     "domestic violence, threat + injury, native Telugu"),
    ("te_caste_anchor", "నా కులం కారణంగా నన్ను బహిరంగంగా అవమానించారు.", "te", "native",
     "exact training-anchor phrasing for caste_based_motive"),
    ("te_caste_temple", "నా కులం కారణంగా నన్ను గుడిలోకి రానివ్వలేదు మరియు నన్ను బహిరంగంగా అవమానించారు. ఇప్పుడు ఒక గుంపు నా ఇంటిని చుట్టుముట్టింది.", "te", "native",
     "the exact text typed live in the recorded demo footage (never submitted) -- regression case"),
    ("te_stalking", "ఒక వ్యక్తి ప్రతిరోజు కళాశాల నుండి నన్ను వెంబడిస్తున్నాడు.", "te", "native",
     "stalking, native Telugu"),

    # ---------------- Telugu, romanized ----------------
    ("te_rom_caste_anchor", "Naa kulam karananga nannu bahirangamga avamanincharu.", "te", "romanized",
     "exact training-anchor phrasing, romanized Telugu -- known to score 100%"),
    ("te_rom_caste_anchor_threat", "Naa kulam karananga nannu bahirangamga avamanincharu mariyu naa illu tagalabetta ani bedirinchadu.", "te", "romanized",
     "anchor phrasing extended with a threat clause -- known to score ~96%"),
    ("te_rom_novel_1", "Naa pakkinti vyakti naa kulam gurinchi naaku bahiranga avamanam chesadu, nenu Scheduled Caste nunchi vachanu ani cheppi naaku bedirimpu chesadu.", "te", "romanized",
     "KNOWN WEAK: free-form romanized Telugu, scored ~67% earlier tonight -- regression case"),
    ("te_rom_novel_2", "Namadhi eppudu jaringedhe, manuri paka intayanu randari mundu nannu kulam paru toti chala kevalanga thittaru. Nannu andari mundhu avamaninchi, a tharvatha thupakitho ledha chetholtho samputhanani bedirincharu.", "te", "romanized",
     "KNOWN WEAK: Gemini-generated romanized Telugu (accented), scored ~52% earlier tonight -- regression case"),
    ("te_rom_stalking", "Oka vyakti prati roju college nundi nannu venbadistunnadu.", "te", "romanized",
     "stalking, romanized Telugu"),

    # ---------------- Urdu (added 2026-08-29) ----------------
    # Native Perso-Arabic script only just got real detection (see
    # understanding.py's detect_language() -- previously any Arabic-
    # range text was forced to the "en" default). These are novel
    # phrasings, not anchor-set copies, so this measures genuine
    # generalization, same discipline as the te_rom_novel_* cases
    # above. Translation quality here has NOT had a native-speaker
    # review pass -- flagged honestly, same as any other unverified
    # claim in this codebase; recommended before relying on this in a
    # live judged demo.
    ("ur_dv_novel", "میرا شوہر روزانہ مجھ پر ہاتھ اٹھاتا ہے اور مجھے بہت ڈرا دھمکا کر رکھتا ہے۔", "ur", "native",
     "novel domestic_violence phrasing, native Urdu"),
    ("ur_stalking_novel", "ایک آدمی ہر روز اسکول کے باہر میرا انتظار کرتا ہے اور میرا پیچھا کرتا ہے۔", "ur", "native",
     "novel stalking phrasing, native Urdu -- initially misclassified as domestic_violence at 53.7% until a matching anchor was added"),
    ("ur_caste_novel", "میرے مالک مکان نے میری ذات جان کر مجھے کرایہ دینے سے انکار کر دیا۔", "ur", "native",
     "novel caste_based_motive phrasing, native Urdu"),
    ("ur_suicidal_indirect_novel", "مجھے لگتا ہے میں سب پر بوجھ بن گئی ہوں اور شاید سب کے لیے بہتر ہو اگر میں نہ ہوتی۔", "ur", "native",
     "novel indirect suicidal_ideation phrasing (burden framing), native Urdu -- safety-critical, confirmed True"),
    ("ur_hard_negative_novel", "آج دفتر میں بہت زیادہ کام تھا اور میں بہت تھک گئی ہوں، موڈ بھی خراب ہے۔", "ur", "native",
     "novel mundane-distress phrasing, native Urdu -- must NOT trigger suicidal_ideation, confirmed False"),

    # ---------------- Bengali (added 2026-08-29) ----------------
    # Native script also just got real detection. Found and fixed live
    # 2026-08-29: pure-Bengali text was misdetected as Hindi because
    # Bengali reuses the Devanagari danda (।) for its own full stop --
    # see detect_language()'s Devanagari branch for the fix. Same
    # translation-review caveat as the Urdu cases above.
    ("bn_dv_novel", "আমার স্বামী প্রতিদিন আমার গায়ে হাত তোলে এবং আমাকে হুমকি দিয়ে রাখে।", "bn", "native",
     "novel domestic_violence phrasing, native Bengali"),
    ("bn_stalking_novel", "একজন লোক প্রতিদিন স্কুলের বাইরে আমার জন্য অপেক্ষা করে এবং আমার পিছু নেয়।", "bn", "native",
     "novel stalking phrasing, native Bengali"),
    ("bn_caste_novel", "আমার বাড়িওয়ালা আমার জাত জানার পর আমাকে বাড়ি ভাড়া দিতে অস্বীকার করেছে।", "bn", "native",
     "novel caste_based_motive phrasing, native Bengali"),
    ("bn_suicidal_indirect_novel", "আমার মনে হচ্ছে আমি সবার বোঝা হয়ে গেছি, হয়তো আমি না থাকলেই সবার জন্য ভালো হতো।", "bn", "native",
     "novel indirect suicidal_ideation phrasing (burden framing), native Bengali -- safety-critical, confirmed True"),
    ("bn_hard_negative_novel", "আজ অফিসে অনেক কাজ ছিল এবং আমি খুব ক্লান্ত, মেজাজও খারাপ।", "bn", "native",
     "novel mundane-distress phrasing, native Bengali -- must NOT trigger suicidal_ideation, confirmed False"),
]


def _confidence_of(breakdown, key):
    return (breakdown or {}).get(key)


def run_eval():

    results = []

    for case_id, text, language, script_label, note in CASES:

        incident = understand(text, language=language)

        confidence = incident.get("confidence", 0.0)
        breakdown = incident.get("confidence_breakdown") or {}

        caste_flagged = bool(incident.get("caste_based_motive"))
        caste_confidence = _confidence_of(breakdown, "caste_based_motive")

        below_incident_floor = confidence < INCIDENT_TYPE_CONFIDENCE_FLOOR
        caste_flagged_but_untrusted = (
            caste_flagged
            and caste_confidence is not None
            and caste_confidence < CASTE_MOTIVE_CONFIDENCE_FLOOR
        )

        results.append({
            "id": case_id,
            "language": language,
            "script_label": script_label,
            "note": note,
            "incident_type": incident.get("incident_type"),
            "confidence": round(confidence, 1),
            "detected_script": incident.get("script"),
            "caste_based_motive": caste_flagged,
            "caste_confidence": caste_confidence,
            "immediate_danger": incident.get("immediate_danger"),
            "threat_present": incident.get("threat_present"),
            "injury_present": incident.get("injury_present"),
            "suicidal_ideation": incident.get("suicidal_ideation"),
            "below_incident_floor": below_incident_floor,
            "caste_flagged_but_untrusted": caste_flagged_but_untrusted,
        })

    return results


def print_report(results):

    print("=" * 100)
    print(f"{'ID':28} {'lang/script':14} {'incident_type':18} {'conf':>6}  {'caste':>6}  {'caste_conf':>10}  {'suicidal':>8}  flags")
    print("=" * 100)

    for r in results:

        flags = []
        if r["below_incident_floor"]:
            flags.append("BELOW_INCIDENT_FLOOR")
        if r["caste_flagged_but_untrusted"]:
            flags.append("CASTE_FLAGGED_BUT_UNTRUSTED")

        caste_conf_str = f"{r['caste_confidence']:.1f}" if r["caste_confidence"] is not None else "-"

        print(
            f"{r['id']:28} {r['language']+'/'+r['script_label']:14} "
            f"{str(r['incident_type']):18} {r['confidence']:6.1f}  "
            f"{str(r['caste_based_motive']):>6}  {caste_conf_str:>10}  "
            f"{str(r['suicidal_ideation']):>8}  "
            f"{', '.join(flags)}"
        )

    print("=" * 100)
    print("\nAGGREGATE BY LANGUAGE / SCRIPT\n")

    buckets = {}
    for r in results:
        key = (r["language"], r["script_label"])
        buckets.setdefault(key, []).append(r["confidence"])

    print(f"{'language/script':18} {'n':>4} {'avg_conf':>10} {'min_conf':>10} {'below_floor':>12}")
    for (lang, script), confs in sorted(buckets.items()):
        below = sum(1 for r in results if r["language"] == lang and r["script_label"] == script and r["below_incident_floor"])
        print(f"{lang+'/'+script:18} {len(confs):4d} {sum(confs)/len(confs):10.1f} {min(confs):10.1f} {below:12d}")

    print("\nCASES FLAGGED (below incident-confidence floor, or caste_based_motive detected but not trusted):\n")
    flagged = [r for r in results if r["below_incident_floor"] or r["caste_flagged_but_untrusted"]]
    if not flagged:
        print("  (none)")
    for r in flagged:
        print(f"  - {r['id']} ({r['language']}/{r['script_label']}): {r['note']}")


if __name__ == "__main__":
    results = run_eval()
    print_report(results)
