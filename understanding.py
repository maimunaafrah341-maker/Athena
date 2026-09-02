import re

from sklearn.metrics.pairwise import cosine_similarity

from embedding_model import model


# ============================================================
# ATHENA — INCIDENT UNDERSTANDING
# ============================================================

"""
Convert a user's incident report into a structured,
language-independent representation.

Supported demo languages:
- English
- Hindi
- Telugu
"""


# ============================================================
# CONFIGURATION
# ============================================================
#
# Reuses embedding_model.model instead of loading its own second
# copy of the same intfloat/multilingual-e5-small weights -- this
# was loading identical model weights twice at process startup
# (once here, once in embedding_model.py for retrieval.py), which is
# exactly what pushed a Render free-tier deploy (512MB) into an OOM
# crash loop. Same model, same weights, now one instance shared
# between incident understanding and RAG retrieval.

# ============================================================
# NEUTRAL / OUT-OF-DOMAIN BASELINE
# ============================================================
#
# multilingual-e5-small (like most short-text sentence embeddings)
# packs unrelated short sentences into a narrow cosine-similarity
# range, so an absolute similarity threshold alone can't tell
# "this text resembles a danger signal" apart from "this is
# generic small talk that happens to embed nearby." Off-topic
# and gibberish text was regularly clearing a 0.72 absolute
# threshold and getting flagged as Critical/immediate danger.
#
# Fix: compare every candidate match against how well the same
# query matches a bank of ordinary, non-incident sentences. Only
# trust a signal/classification when it beats that neutral
# baseline by a margin — not just an absolute score.

NEUTRAL_EXAMPLES = [
    "I had a normal day today.",
    "Can you recommend a movie to watch tonight?",
    "I'm trying to decide what to cook for dinner.",
    "I feel a bit tired but nothing serious.",
    "Just wanted to say hello.",
    "I'm bored and don't know what to do.",
    "The traffic was bad this morning.",
    "I'm thinking about switching jobs.",
    "आज मौसम बहुत अच्छा है।",
    "मुझे समझ नहीं आ रहा कि क्या करूं।",
    "मैं बस हालचाल पूछ रहा था।",
    "आज का दिन सामान्य रहा।",
    "ఈ రోజు వాతావరణం చాలా బాగుంది.",
    "నాకు ఏమి చేయాలో అర్థం కావడం లేదు.",
    "నేను కేవలం యోగక్షేమం అడుగుతున్నాను.",
]

print("Preparing neutral baseline examples...")

neutral_embeddings = model.encode(
    ["query: " + example for example in NEUTRAL_EXAMPLES],
    normalize_embeddings=True
)

# Minimum lead a real match needs over the neutral baseline before
# it's trusted. Calibrated against real incident reports (margin
# 0.07-0.17) vs. off-topic/ambiguous/gibberish text (margin -0.09
# to +0.02) across en/hi/te.
NEUTRAL_MARGIN = 0.04


def neutral_ceiling(query_embedding):
    """
    How well this query matches ordinary, non-incident text.
    Used as the rejection baseline for signal/classification checks.
    """

    similarities = query_embedding @ neutral_embeddings.T

    return float(similarities.max())


def calibrate_confidence(raw_similarity, query_embedding, ceiling=None):
    """
    Convert a raw cosine similarity into a calibrated 0-1 confidence,
    the same way for every detector (incident type, each signal,
    relationship, location) so they're actually comparable to each
    other -- a margin of NEUTRAL_MARGIN over the rejection ceiling
    maps to 100%, a margin of 0 (this text matches the category no
    better than it matches the ceiling) maps to 0%.

    Shared by every detector below instead of each one inlining its
    own copy of this formula, so a per-field confidence_breakdown
    means the same thing in every field rather than mixing raw
    similarity scores with calibrated ones.

    `ceiling` lets a caller pass an already-computed rejection ceiling
    (e.g. detect_signal()'s hard-negative-aware one) instead of the
    plain neutral baseline, so the reported confidence agrees with
    whatever ceiling actually decided present/absent -- otherwise a
    signal correctly rejected via a hard negative could still report a
    misleadingly high confidence computed against the weaker neutral-
    only baseline.
    """

    if ceiling is None:
        ceiling = neutral_ceiling(query_embedding)

    margin = raw_similarity - ceiling

    return max(0.0, min(1.0, margin / (NEUTRAL_MARGIN * 2.5)))


# ============================================================
# LANGUAGE DETECTION
# ============================================================

LANGUAGE_EXAMPLES = {
    "en": [
        "This is an English incident report about a woman facing violence.",
        "I am in danger and I need help.",
        "Someone is threatening me.",
    ],

    "hi": [
        "यह हिंदी में महिला हिंसा से संबंधित घटना की रिपोर्ट है।",
        "मैं खतरे में हूँ और मुझे मदद चाहिए।",
        "कोई मुझे धमकी दे रहा है।",

        # Romanized Hindi
        "Yeh Hindi mein mahila hinsa se sambandhit ghatna ki report hai.",
        "Main khatre mein hoon aur mujhe madad chahiye.",
        "Koi mujhe dhamki de raha hai.",

        # Wider romanized coverage. The three anchors above were all
        # short and structurally alike, so a longer real sentence with
        # different vocabulary could land closer to the Telugu bank than
        # to these. Found live 2026-09-02: "Mujhe meri jaati ke naam par
        # dhamki di ja rahi hai aur ghar ke bahar bheed khadi hai" --
        # unambiguous romanized Hindi -- was detected as Telugu and
        # answered in Telugu.
        #
        # These lean on the function words that actually separate
        # romanized Hindi from romanized Telugu (hai/hain, raha-rahi-rahe,
        # mujhe/meri, ke-ki-ka, aur, nahi) rather than on topic words,
        # which the two share freely.
        "Mujhe meri jaati ke naam par dhamki di ja rahi hai.",
        "Ghar ke bahar bheed khadi hai aur woh log andar aane ki koshish kar rahe hain.",
        "Mere pati mujhe roz maarte hain aur main kuch nahi kar sakti.",
        "Woh log mujhe school jaane nahi de rahe hain.",
        "Mujhe samajh nahi aa raha hai ki main kya karoon, bahut dar lag raha hai.",
        "Mere saath jo hua hai uske baare mein main kisi se baat nahi kar payi.",
    ],

    "te": [
        "ఇది మహిళపై హింసకు సంబంధించిన తెలుగు ఘటన నివేదిక.",
        "నేను ప్రమాదంలో ఉన్నాను మరియు నాకు సహాయం కావాలి.",
        "ఎవరో నన్ను బెదిరిస్తున్నారు.",

        # Romanized Telugu
        "Idi mahilapai hinsaku sambandhinchina Telugu ghatana nivedika.",
        "Nenu pramadamlo unnanu mariyu naaku sahayam kavali.",
        "Evaro nannu bediristunnaru.",

        # Widened alongside the Hindi bank above, and for the same
        # reason -- adding anchors to only one side would just move the
        # boundary rather than sharpen it, trading Hindi misses for
        # Telugu ones. These lean on the endings that actually mark
        # romanized Telugu (undi, unnanu, unnaru, unnaru, naaku, naa,
        # mariyu, ledu, cheyyandi) rather than on shared topic words.
        "Naa kulam peruto nannu bedirinchutunnaru.",
        "Maa intiki bayata janalu gumigudi unnaru.",
        "Naa bharta rojoo nannu kodutunnadu, nenu emi cheyaleka unnanu.",
        "Vaallu nannu badiki vellanivvatam ledu.",
        "Naaku em cheyalo ardham kavatam ledu, chala bhayam ga undi.",
        "Naaku jarigina daani gurinchi nenu evvarito matladalekapoyanu.",
    ],

    "ur": [
        "یہ ایک اردو رپورٹ ہے جو ایک عورت پر تشدد کے بارے میں ہے۔",
        "میں خطرے میں ہوں اور مجھے مدد چاہیے۔",
        "کوئی مجھے دھمکی دے رہا ہے۔",

        # Romanized Urdu -- linguistically very close to romanized
        # Hindi (same spoken Hindustani base), which is exactly why
        # this LANGUAGE_EXAMPLES bank matters for it: without its own
        # anchors here, romanized Urdu text would very plausibly get
        # semantically pulled toward "hi" instead by the fallback
        # below. Native-script Urdu never reaches this fallback at all
        # (see detect_language()'s script-count branch above) -- these
        # anchors are purely for Latin-script Urdu typing.
        "Yeh Urdu mein aik report hai jo aurat par tashaddud ke baare mein hai.",
        "Main khatre mein hoon aur mujhe madad chahiye.",
        "Koi mujhe dhamki de raha hai.",
    ],

    "bn": [
        "এটি একজন নারীর উপর সহিংসতা সম্পর্কিত একটি বাংলা প্রতিবেদন।",
        "আমি বিপদে আছি এবং আমার সাহায্য দরকার।",
        "কেউ আমাকে হুমকি দিচ্ছে।",

        # Romanized Bengali (Banglish) -- native-script Bengali never
        # reaches this fallback (own script-count branch above); these
        # anchors are for Latin-script Bengali typing.
        "Eta ekjon narir upor sohingshotar bapare ekti bangla report.",
        "Ami bipode achi ebong amar sahajyo dorkar.",
        "Keu amake humki dicche.",
    ],
}


print("Preparing language detection examples...")

language_embeddings = {}

for language, examples in LANGUAGE_EXAMPLES.items():

    language_embeddings[language] = model.encode(
        ["query: " + example for example in examples],
        normalize_embeddings=True
    )

print("Language detection ready.")


# ============================================================
# SCRIPT-BASED LANGUAGE DETECTION
# ============================================================

def detect_language(text):
    """
    Detect whether the incident is English, Hindi, or Telugu.

    Native scripts are detected directly.
    Romanized Hindi/Telugu and English use multilingual
    semantic similarity as a fallback.
    """

    if not text or not text.strip():
        return "en"

    # --------------------------------------------------------
    # Count characters belonging to each script
    # --------------------------------------------------------

    devanagari_count = 0
    telugu_count = 0
    urdu_count = 0
    bengali_count = 0
    other_script_count = 0

    for char in text:

        code = ord(char)

        # Devanagari: U+0900 - U+097F, excluding U+0964/U+0965 (danda /
        # double danda). The danda is pan-Brahmic sentence-ending
        # punctuation reused by Bengali (and Gujarati, Gurmukhi, Odia)
        # -- counting it as "Devanagari" meant a pure-Bengali sentence
        # like "...দরকার।" registered one Devanagari character from its
        # own full stop and got returned as "hi" before bengali_count
        # was ever consulted, below. Found live 2026-08-29 testing
        # detect_language() against real Bengali sentences.
        if 0x0900 <= code <= 0x097F and code not in (0x0964, 0x0965):
            devanagari_count += 1

        # Telugu: U+0C00 - U+0C7F
        elif 0x0C00 <= code <= 0x0C7F:
            telugu_count += 1

        # Urdu (Perso-Arabic script): U+0600 - U+06FF (Arabic block,
        # which Urdu is written with) plus U+0750-U+077F (Arabic
        # Supplement) and U+FB50-U+FDFF/U+FE70-U+FEFF (Arabic
        # Presentation Forms), both used by Urdu-specific letterforms
        # (e.g. ں, ے) that don't appear in the base block. Known,
        # accepted limitation: standard Arabic text uses the same
        # codepoints and would also land here as "ur" -- same tradeoff
        # already made for Tamil/Kannada/etc. below (a script this
        # project doesn't have real support for shouldn't fall through
        # to the semantic fallback and get a confidently wrong native-
        # script label), and Arabic-script input from an Indian
        # national helpline's reporters is overwhelmingly more likely
        # to be Urdu than Arabic.
        elif (
            0x0600 <= code <= 0x06FF
            or 0x0750 <= code <= 0x077F
            or 0xFB50 <= code <= 0xFDFF
            or 0xFE70 <= code <= 0xFEFF
        ):
            urdu_count += 1

        # Bengali: U+0980 - U+09FF
        elif 0x0980 <= code <= 0x09FF:
            bengali_count += 1

        # Any other non-Latin script this project doesn't support
        # (Tamil, Kannada, Malayalam, Gurmukhi, Gujarati, Odia, etc.)
        # -- see the guard below for why this is checked separately
        # from the semantic fallback.
        elif (
            0x0B80 <= code <= 0x0BFF  # Tamil
            or 0x0C80 <= code <= 0x0CFF  # Kannada
            or 0x0D00 <= code <= 0x0D7F  # Malayalam
            or 0x0A00 <= code <= 0x0A7F  # Gurmukhi (Punjabi)
            or 0x0A80 <= code <= 0x0AFF  # Gujarati
            or 0x0B00 <= code <= 0x0B7F  # Odia
        ):
            other_script_count += 1

    # --------------------------------------------------------
    # Strong native-script detection
    # --------------------------------------------------------

    if devanagari_count > 0:
        return "hi"

    if telugu_count > 0:
        return "te"

    if urdu_count > 0:
        return "ur"

    if bengali_count > 0:
        return "bn"

    # A script this project definitively does not support (confirmed
    # by real character ranges, not a guess) must never reach the
    # semantic fallback below -- that fallback measures "which
    # language's distress-anchors sound semantically similar to this
    # text," not "what script is this," and those are different
    # questions. Live testing 2026-08-22 found it answers the first
    # question in a way that's actively misleading for the second:
    # native Tamil script text was confidently (100%) misdetected as
    # Hindi and the user got a romanized-Hindi response to Tamil
    # input -- a specific wrong language, not a safe default. Any
    # confirmed non-Latin/non-Devanagari/non-Telugu script skips
    # straight to the safe "en" default instead.
    if other_script_count > 0:
        return "en"

    # --------------------------------------------------------
    # Fallback to multilingual semantic detection -- only reachable
    # for Latin-script text now, where its actual job (English vs.
    # romanized Hindi vs. romanized Telugu) is well-posed.
    # --------------------------------------------------------

    query_embedding = model.encode(
        ["query: " + text],
        normalize_embeddings=True
    )

    scores = {}

    for language, embeddings in language_embeddings.items():

        similarities = query_embedding @ embeddings.T

        scores[language] = float(similarities.max())

    best_language = max(scores, key=scores.get)

    # Ambiguous/short/off-topic text can weakly resemble the hi/te
    # example sets too. Only override the English default when a
    # non-English match clearly leads the English score — otherwise
    # default to English rather than guessing.
    if best_language != "en" and (scores[best_language] - scores["en"]) < NEUTRAL_MARGIN:
        return "en"

    return best_language
# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ur": "Urdu",
    "bn": "Bengali",
}


# ============================================================
# INCIDENT TYPES
# ============================================================

INCIDENT_TYPES = [
    "domestic_violence",
    "sexual_violence",
    "harassment",
    "stalking",
    "trafficking",
    "cyber_harassment",
    "missing_person",
    "other",
]


# ============================================================
# SEMANTIC EXAMPLES
# ============================================================

INCIDENT_EXAMPLES = {

    "domestic_violence": [
        "My husband is beating me.",
        "My husband is physically hurting me.",
        "My husband threatens and abuses me.",
        "My family member is hurting me at home.",
        "मेरे पति मुझे मार रहे हैं।",
        "मेरे पति मुझे धमकी दे रहे हैं और चोट पहुँचा रहे हैं।",
        "मेरे परिवार का सदस्य मुझे घर में परेशान कर रहा है।",
        "నా భర్త నన్ను కొడుతున్నాడు.",
        "నా భర్త నన్ను బెదిరిస్తున్నాడు మరియు హింసిస్తున్నాడు.",
        "నా కుటుంబ సభ్యుడు నన్ను ఇంట్లో వేధిస్తున్నాడు.",

        # Romanized Hindi
        "Mere pati mujhe maar rahe hain.",
        "Mere pati mujhe dhamki de rahe hain aur chot pahuncha rahe hain.",
        "Mere parivar ka sadasya mujhe ghar mein pareshan kar raha hai.",

        # Romanized Telugu
        "Naa bharta nannu kodutunnadu.",
        "Naa bharta nannu bediristunnadu mariyu himsistunnadu.",
        "Naa kutumba sabhyudu nannu intlo vedhistunnadu.",

        "میرا شوہر مجھے مارتا ہے۔",
        "میرا شوہر مجھے جسمانی طور پر تکلیف دیتا ہے۔",
        "میرا شوہر مجھے دھمکاتا ہے اور مارتا پیٹتا ہے۔",
        "میرے گھر کا فرد مجھے گھر میں تنگ کرتا ہے۔",

        # Romanized Urdu
        "Mera shohar mujhe maarta hai.",
        "Mera shohar mujhe dhamkata hai aur maarta peetta hai.",
        "Mere ghar ka fard mujhe ghar mein tang karta hai.",

        "আমার স্বামী আমাকে মারে।",
        "আমার স্বামী আমাকে শারীরিকভাবে আঘাত করে।",
        "আমার স্বামী আমাকে হুমকি দেয় এবং মারধর করে।",
        "আমার পরিবারের একজন সদস্য আমাকে বাড়িতে কষ্ট দেয়।",

        # Romanized Bengali
        "Amar shami amake mare.",
        "Amar shami amake humki dey ebong mardhor kore.",
        "Amar poribarer ekjon sodossho amake barite koshto dey."
    ],

    "sexual_violence": [
        "Someone sexually assaulted me.",
        "I was sexually abused.",
        "Someone forced me into sexual activity.",
        "मेरे साथ यौन हिंसा हुई है।",
        "मेरे साथ यौन दुर्व्यवहार किया गया।",
        "నాపై లైంగిక దాడి జరిగింది.",
        "నన్ను లైంగికంగా వేధించారు.",

        # Romanized Hindi
        "Mere saath yaun hinsa hui hai.",
        "Mere saath yaun durvyavahar kiya gaya.",

        # Romanized Telugu
        "Naapai laingika daadi jarigindi.",
        "Nannu laingikanga vedhincharu.",

        "کسی نے میرے ساتھ جنسی زیادتی کی۔",
        "میرے ساتھ جنسی زیادتی ہوئی۔",

        # Romanized Urdu
        "Kisi ne mere sath jinsi zyadti ki.",
        "Mere sath jinsi zyadti hui.",

        "কেউ আমার সাথে যৌন নির্যাতন করেছে।",
        "আমার সাথে যৌন নিপীড়ন হয়েছে।",

        # Romanized Bengali
        "Keu amar sathe joun nirjaton koreche.",
        "Amar sathe joun nipiron hoyeche."
    ],

    "harassment": [
        "Someone is constantly harassing me.",
        "I am being verbally abused.",
        "Someone keeps insulting and threatening me.",
        "कोई मुझे लगातार परेशान कर रहा है।",
        "कोई मुझे बार-बार धमका रहा है।",
        "ఎవరైనా నన్ను నిరంతరం వేధిస్తున్నారు.",
        "ఎవరైనా నన్ను పదే పదే బెదిరిస్తున్నారు.",

        # Romanized Hindi
        "Koi mujhe lagatar pareshan kar raha hai.",
        "Koi mujhe baar baar dhamka raha hai.",

        # Romanized Telugu
        "Evarina nannu nirantaram vedhistunnaru.",
        "Evarina nannu pade pade bedhiristunnaru.",

        "کوئی مجھے مسلسل تنگ کر رہا ہے۔",
        "میرے ساتھ زبانی بدسلوکی ہو رہی ہے۔",

        # Romanized Urdu
        "Koi mujhe musalsal tang kar raha hai.",
        "Koi mujhe baar baar be-izzat aur dhamki deta hai.",

        "কেউ আমাকে ক্রমাগত হয়রানি করছে।",
        "আমার সাথে মৌখিক নির্যাতন করা হচ্ছে।",

        # Romanized Bengali
        "Keu amake khromagoto hoyrani korche.",
        "Keu bar bar amake opoman ebong humki dey.",

        # Caste-based public insult/humiliation -- without these,
        # classify_incident() had no real anchor for this kind of
        # text at all and was picking essentially arbitrary incident
        # types for genuinely caste-motivated reports (confirmed via
        # live testing 2026-08-22: a temple-access-denial report came
        # back "domestic_violence", an eviction report came back
        # "trafficking"). This directly corrupts which SC/ST Act
        # section kg.py cites, since it keys off incident_type.
        "Someone publicly insulted and humiliated me because of my caste.",
        "I was denied entry to a place because of my caste.",
        "मेरी जाति के कारण मुझे सार्वजनिक रूप से अपमानित किया गया।",
        "నా కులం కారణంగా నన్ను బహిరంగంగా అవమానించారు.",

        # Romanized Hindi
        "Meri jaati ke karan mujhe sarvajanik roop se apmanit kiya gaya.",

        # Romanized Telugu
        "Naa kulam karananga nannu bahirangamga avamanincharu.",

        "کسی نے میری ذات کی وجہ سے مجھے سب کے سامنے بے عزت کیا۔",
        "مجھے میری ذات کی وجہ سے داخلے سے روکا گیا۔",

        # Romanized Urdu
        "Kisi ne meri zaat ki wajah se mujhe sab ke samne be-izzat kiya.",
        "Mujhe meri zaat ki wajah se dakhle se roka gaya.",

        "কেউ আমার জাতের কারণে জনসম্মুখে আমাকে অপমান করেছে।",
        "আমার জাতের কারণে আমাকে ঢুকতে দেওয়া হয়নি।",

        # Romanized Bengali
        "Keu amar jater karone jonoshommukhe amake opoman koreche.",
        "Amar jater karone amake dhukte deya hoyni."
    ],

    "stalking": [
        "Someone is following me everywhere.",
        "Someone keeps following me.",
        "Someone is watching me and following me.",
        "कोई मेरा पीछा कर रहा है।",
        "कोई मेरा लगातार पीछा कर रहा है।",
        "ఎవరైనా నన్ను వెంబడిస్తున్నారు.",
        "ఎవరైనా నన్ను నిరంతరం అనుసరిస్తున్నారు.",

        # Romanized Hindi
        "Koi mera peecha kar raha hai.",
        "Koi mera lagatar peecha kar raha hai.",

        # Romanized Telugu
        "Evarina nannu vembadistunnaru.",
        "Evarina nannu nirantaram anusaristunnaru.",

        "کوئی ہر جگہ میرا پیچھا کر رہا ہے۔",
        "کوئی مسلسل میرا پیچھا کرتا ہے۔",
        "ایک آدمی ہر روز باہر میرا انتظار کرتا ہے اور میرا پیچھا کرتا ہے۔",

        # Romanized Urdu
        "Koi har jagah mera peecha kar raha hai.",
        "Koi musalsal mera peecha karta hai.",
        "Aik aadmi har roz bahar mera intezar karta hai aur mera peecha karta hai.",

        "কেউ সবসময় আমাকে অনুসরণ করছে।",
        "কেউ আমার পিছু নিচ্ছে।",
        "একজন লোক প্রতিদিন বাইরে আমার জন্য অপেক্ষা করে এবং আমার পিছু নেয়।",

        # Romanized Bengali
        "Keu shobshomoy amake onushoron korche.",
        "Keu amar pichu nicche.",
        "Ekjon lok protidin baire amar jonno opekkha kore ebong amar pichu ney."
    ],

    "trafficking": [
        "I am being trafficked.",
        "Someone is forcing women into trafficking.",
        "I was taken somewhere against my will for exploitation.",
        "मुझे जबरन तस्करी के लिए ले जाया गया।",
        "मुझे शोषण के लिए जबरदस्ती ले जाया गया।",
        "నన్ను అక్రమ రవాణా కోసం బలవంతంగా తీసుకెళ్లారు.",
        "నన్ను దోపిడీ కోసం బలవంతంగా తీసుకెళ్లారు.",

        # Romanized Hindi
        "Mujhe jabran taskari ke liye le jaya gaya.",
        "Mujhe shoshan ke liye jabardasti le jaya gaya.",

        # Romanized Telugu
        "Nannu akrama ravana kosam balavantanga teesukellaru.",
        "Nannu dopidi kosam balavantanga teesukellaru.",

        "مجھے انسانی اسمگلنگ کا نشانہ بنایا جا رہا ہے۔",
        "کوئی عورتوں کو زبردستی اسمگلنگ میں دھکیل رہا ہے۔",

        # Romanized Urdu
        "Mujhe insaani smuggling ka nishana banaya ja raha hai.",
        "Koi aurton ko zabardasti smuggling mein dhakel raha hai.",

        "আমাকে পাচার করা হচ্ছে।",
        "কেউ জোর করে নারীদের পাচারে ঠেলে দিচ্ছে।",

        # Romanized Bengali
        "Amake pachar kora hocche.",
        "Keu jor kore narider pachare thele dicche."
    ],

    "cyber_harassment": [
        "Someone is threatening me online.",
        "Someone is harassing me through social media.",
        "Someone is sharing my private photos online.",
        "कोई मुझे ऑनलाइन धमका रहा है।",
        "कोई सोशल मीडिया पर मुझे परेशान कर रहा है।",
        "ఎవరైనా నన్ను ఆన్‌లైన్‌లో బెదిరిస్తున్నారు.",
        "ఎవరైనా సోషల్ మీడియాలో నన్ను వేధిస్తున్నారు.",

        # Romanized Hindi
        "Koi mujhe online dhamka raha hai.",
        "Koi social media par mujhe pareshan kar raha hai.",

        # Romanized Telugu
        "Evarina nannu online lo bedhiristunnaru.",
        "Evarina social media lo nannu vedhistunnaru.",

        "کوئی مجھے آن لائن دھمکی دے رہا ہے۔",
        "کوئی سوشل میڈیا پر مجھے تنگ کر رہا ہے۔",

        # Romanized Urdu
        "Koi mujhe online dhamki de raha hai.",
        "Koi social media par mujhe tang kar raha hai.",

        "কেউ আমাকে অনলাইনে হুমকি দিচ্ছে।",
        "কেউ সোশ্যাল মিডিয়ায় আমাকে হয়রানি করছে।",

        # Romanized Bengali
        "Keu amake online-e humki dicche.",
        "Keu social media-y amake hoyrani korche."
    ],

    "missing_person": [
        "My daughter is missing.",
        "My sister has disappeared.",
        "I cannot find my family member.",
        "मेरी बेटी लापता है।",
        "मेरी बहन गायब हो गई है।",
        "నా కుమార్తె కనిపించడం లేదు.",
        "నా సోదరి కనిపించడం లేదు.",

        # Romanized Hindi
        "Meri beti lapata hai.",
        "Meri behan gayab ho gayi hai.",

        # Romanized Telugu
        "Naa kumarthe kanipinchadam ledu.",
        "Naa sodari kanipinchadam ledu.",

        "میری بیٹی لاپتہ ہے۔",
        "میری بہن غائب ہو گئی ہے۔",

        # Romanized Urdu
        "Meri beti lapata hai.",
        "Meri behan ghayab ho gayi hai.",

        "আমার মেয়ে নিখোঁজ।",
        "আমার বোন হারিয়ে গেছে।",

        # Romanized Bengali
        "Amar meye nikhoj.",
        "Amar bon hariye geche."
    ],
}


# ============================================================
# BUILD EXAMPLE EMBEDDINGS
# ============================================================

print("Preparing multilingual incident examples...")

example_texts = []
example_labels = []

for incident_type, examples in INCIDENT_EXAMPLES.items():

    for example in examples:

        example_texts.append(
            "query: " + example
        )

        example_labels.append(
            incident_type
        )


example_embeddings = model.encode(
    example_texts,
    normalize_embeddings=True,
    show_progress_bar=False
)

print("Incident examples ready.")


# ============================================================
# INCIDENT CLASSIFICATION
# ============================================================

def classify_incident(text):
    """
    Classify the incident using multilingual semantic similarity.
    """

    query_embedding = model.encode(
        ["query: " + text],
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        query_embedding,
        example_embeddings
    )[0]

    # Get highest similarity
    best_index = similarities.argmax()

    incident_type = example_labels[best_index]
    raw_similarity = float(similarities[best_index])

    confidence = calibrate_confidence(raw_similarity, query_embedding)

    return incident_type, confidence


# ============================================================
# SIGNAL DETECTION
# ============================================================

SIGNAL_EXAMPLES = {

    "threat_present": [
        "I am being threatened.",
        "Someone is threatening me.",
        "He threatened to hurt me.",

        # Anonymous perpetrator + death threat. Found live 2026-09-02:
        # "Someone hit me and threatened to kill me" scored 19.6% on
        # this signal and 0% on immediate_danger, while the identical
        # event written as "My husband hit me and threatened to kill
        # me" scored 100% and Critical. The classifier was leaning on a
        # named relationship to recognise violence at all.
        #
        # The likely pull: this signal's hard-negative bank is entirely
        # "Someone is following me everywhere" stalking phrasing, so a
        # report that opens with "Someone" sits close to the negatives.
        # Plenty of real reports never name who did it -- because the
        # person doesn't know, or isn't ready to say -- and those
        # reports must not score lower for it.
        "Someone hit me and threatened to kill me.",
        "Someone threatened to kill me.",
        "They said they would kill me.",
        "I was threatened with death.",
        "किसी ने मुझे मारा और जान से मारने की धमकी दी।",
        "ఎవరో నన్ను కొట్టి చంపేస్తానని బెదిరించారు.",
        "Kisi ne mujhe mara aur jaan se maarne ki dhamki di.",
        "Evaro nannu kotti champestanani bedirincharu.",
        "मुझे धमकी दी जा रही है।",
        "वह मुझे धमकी दे रहा है।",
        "నన్ను బెదిరిస్తున్నారు.",
        "అతను నన్ను బెదిరిస్తున్నాడు.",

        # Romanized Hindi
        "Mujhe dhamki di ja rahi hai.",
        "Woh mujhe dhamki de raha hai.",

        # Romanized Telugu
        "Nannu bedhiristunnaru.",
        "Atanu nannu bedhiristunnadu.",

        # Compound husband-abuse phrasing (beating + threatening in one
        # sentence) -- residual gap documented 2026-08-22: only 2
        # romanized examples per category meant a genuine compound
        # report like "Naa bharta nannu kottutunnadu mariyu
        # bediristunnadu" (my husband is beating and threatening me)
        # scored too weakly on both threat_present and injury_present
        # to clear the neutral margin reliably. This got measurably
        # worse once the hard-negative check (see
        # SIGNAL_HARD_NEGATIVES below) shipped 2026-08-23 -- a thinly-
        # anchored signal is more fragile against a second rejection
        # check, not just the first. Broader anchor coverage is the
        # real fix for both, not a threshold tweak.
        "Mera pati mujhe maarta hai aur dhamki deta hai.",
        "Naa bharta nannu kottutunnadu mariyu bediristunnadu.",

        "مجھے دھمکی دی جا رہی ہے۔",
        "وہ مجھے دھمکی دے رہا ہے۔",
        "میرا شوہر مجھے مارتا ہے اور دھمکی دیتا ہے۔",

        # Romanized Urdu
        "Mujhe dhamki di ja rahi hai.",
        "Woh mujhe dhamki de raha hai.",
        "Mera shohar mujhe maarta hai aur dhamki deta hai.",

        "আমাকে হুমকি দেওয়া হচ্ছে।",
        "সে আমাকে হুমকি দিচ্ছে।",
        "আমার স্বামী আমাকে মারে এবং হুমকি দেয়।",

        # Romanized Bengali
        "Amake humki deya hocche.",
        "Se amake humki dicche.",
        "Amar shami amake mare ebong humki dey."
    ],

    "injury_present": [
        "I have been physically hurt.",
        "Someone is beating me.",
        "I have injuries.",

        # Anonymous perpetrator -- same gap as threat_present above.
        "Someone hit me.",
        "Someone hit me and I am hurt.",
        "I was beaten by someone I cannot name.",
        "किसी ने मुझे मारा और मुझे चोट आई है।",
        "ఎవరో నన్ను కొట్టారు, నాకు గాయాలు అయ్యాయి.",
        "Kisi ne mujhe mara aur mujhe chot aayi hai.",
        "मुझे शारीरिक चोट लगी है।",
        "मुझे मारा जा रहा है।",
        "నాకు శారీరక గాయాలు అయ్యాయి.",
        "నన్ను కొడుతున్నారు.",

        # Romanized Hindi
        "Mujhe sharirik chot lagi hai.",
        "Mujhe mara ja raha hai.",

        # Romanized Telugu
        "Naaku shareerika gayalu ayyayi.",
        "Nannu kodutunnaru.",

        # Compound husband-abuse phrasing (beating + threatening in one
        # sentence) -- same residual romanized-coverage gap as
        # threat_present above, same fix.
        "Mera pati mujhe maarta hai aur dhamki deta hai.",
        "Naa bharta nannu kottutunnadu mariyu bediristunnadu.",

        # Longer, multi-clause repeated-abuse phrasing (e.g. a parent
        # hitting a child regularly) -- without these, a genuine report
        # like "My father hits me. He beats me almost every day. I'm
        # scared." fell just short of the neutral margin (+0.0136 vs the
        # 0.04 floor) because its embedding sits further from the short,
        # punchy anchors above than a single-clause report would. Found
        # via live adversarial testing 2026-08-2x on the child-victim-
        # coverage case; see athena_known_issues.md.
        "My father hits me. He beats me almost every day.",
        "My parent hits me regularly and I am scared.",
        "मेरे पिता मुझे मारते हैं। वह लगभग रोज़ मुझे पीटते हैं।",
        "నా తండ్రి నన్ను కొడతాడు. అతను దాదాపు ప్రతిరోజూ నన్ను కొడతాడు.",

        # Romanized Hindi
        "Mere pita mujhe maarte hain. Woh lagbhag roz mujhe peetate hain.",

        # Romanized Telugu
        "Naa thandri nannu kodathadu. Atanu dadapu prathi roju nannu kodathadu.",

        "مجھے جسمانی طور پر تکلیف پہنچائی گئی ہے۔",
        "کوئی مجھے مار رہا ہے۔",
        "میرے والد مجھے مارتے ہیں۔ وہ تقریباً روز مجھے پیٹتے ہیں۔ مجھے ڈر لگتا ہے۔",

        # Romanized Urdu
        "Mujhe jismani taur par takleef pahunchai gayi hai.",
        "Koi mujhe maar raha hai.",
        "Mere walid mujhe maarte hain. Woh taqreeban roz mujhe peetate hain. Mujhe dar lagta hai.",

        "আমি শারীরিকভাবে আহত হয়েছি।",
        "কেউ আমাকে মারছে।",
        "আমার বাবা আমাকে মারে। সে প্রায় প্রতিদিন আমাকে পেটায়। আমি ভয় পাচ্ছি।",

        # Romanized Bengali
        "Ami sharirikvabe ahoto hoyechi.",
        "Keu amake marche.",
        "Amar baba amake mare. Se prai protidin amake petay. Ami bhoy pacchi."
    ],

    "immediate_danger": [
        "I am in immediate danger.",
        "I am afraid I will be hurt right now.",
        "He is attacking me right now.",

        # A death threat IS immediate danger, whoever made it. This
        # scored 0.0 on the live case that prompted these anchors --
        # not low, zero -- for a report that said someone had just hit
        # the person and threatened to kill them.
        "Someone hit me and threatened to kill me.",
        "I was just attacked and I am scared for my life.",
        "Someone threatened to kill me and I do not know what to do.",
        "किसी ने मुझे मारा और जान से मारने की धमकी दी, मुझे डर लग रहा है।",
        "ఎవరో నన్ను కొట్టారు, చంపేస్తానన్నారు, నాకు భయంగా ఉంది.",
        "Kisi ne mujhe mara aur jaan se maarne ki dhamki di, mujhe dar lag raha hai.",
        "मुझे अभी खतरा है।",
        "वह अभी मुझ पर हमला कर रहा है।",
        "నాకు ఇప్పుడు ప్రమాదం ఉంది.",
        "అతను ఇప్పుడు నాపై దాడి చేస్తున్నాడు.",

        # Romanized Hindi
        "Mujhe abhi khatra hai.",
        "Woh abhi mujh par hamla kar raha hai.",

        # Romanized Telugu
        "Naaku ippudu pramadam undi.",
        "Atanu ippudu naapai daadi chestunnadu.",

        "مجھے ابھی خطرہ ہے۔",
        "وہ ابھی مجھ پر حملہ کر رہا ہے۔",

        # Romanized Urdu -- "khatra"/"hamla" are shared Hindustani
        # vocabulary, so this reads close to the romanized Hindi
        # anchors above; kept as its own explicit "ur" example rather
        # than relying on the Hindi anchor to cover it, since native-
        # script Urdu is what actually needs this signal covered.
        "Mujhe is waqt khatra hai.",
        "Woh is waqt mujh par hamla kar raha hai.",

        "আমি এখনই বিপদে আছি।",
        "সে এখন আমার উপর আক্রমণ করছে।",

        # Romanized Bengali
        "Ami ekhoni bipode achi.",
        "Se ekhon amar upor akromon korche."
    ],

    # Examples grounded directly in the enumerated offences under the
    # Scheduled Castes and Scheduled Tribes (Prevention of Atrocities)
    # Act, 1989, Section 3(1) (public insult/humiliation because of
    # caste, denial of access, forced eviction) -- not a general
    # "harassment" paraphrase. Feeds kg.py's decision on whether to
    # surface SC/ST Act provisions. Kept advisory/confidence-gated
    # everywhere it's used -- see kg.py -- because misclassifying a
    # protected-characteristic motive (either direction) is a higher-
    # stakes error than the other signals here.
    "caste_based_motive": [
        "Someone insulted and humiliated me in public because of my caste.",
        "I was denied entry to a place because I belong to a Scheduled Caste.",
        "They used a casteist slur against me.",
        "मेरी जाति के कारण मुझे सार्वजनिक रूप से अपमानित किया गया।",
        "मुझे मेरी जाति के कारण प्रवेश से रोका गया।",
        "నా కులం కారణంగా నన్ను బహిరంగంగా అవమానించారు.",
        "నా కులం వల్ల నన్ను లోపలికి రానివ్వలేదు.",

        # Romanized Hindi
        "Meri jaati ke karan mujhe sarvajanik roop se apmanit kiya gaya.",
        "Mujhe meri jaati ke karan pravesh se roka gaya.",

        # Romanized Telugu
        "Naa kulam karananga nannu bahirangamga avamanincharu.",
        "Naa kulam valla nannu lopaliki ranivvaledu.",

        "کسی نے میری ذات کی وجہ سے سب کے سامنے مجھے بے عزت کیا۔",
        "مجھے میری ذات کی وجہ سے داخلے سے روکا گیا۔",

        # Romanized Urdu
        "Kisi ne meri zaat ki wajah se sab ke samne mujhe be-izzat kiya.",
        "Mujhe meri zaat ki wajah se dakhle se roka gaya.",

        "কেউ আমার জাতের কারণে জনসম্মুখে আমাকে অপমান করেছে।",
        "আমার জাতের কারণে আমাকে ঢুকতে দেওয়া হয়নি।",

        # Romanized Bengali
        "Keu amar jater karone jonoshommukhe amake opoman koreche.",
        "Amar jater karone amake dhukte deya hoyni."
    ],

    # Deliberately kept to direct, unambiguous statements of wanting
    # to die/end one's life -- not generic sadness/exhaustion phrases
    # ("I can't take this anymore"), which are common in genuinely
    # non-suicidal distress and would make this signal too broad to
    # trust. Semantic similarity still catches nearby real-world
    # phrasings of the same direct statement; the anchors don't need
    # to cover every euphemism, just be unambiguous positives. See
    # risk.py/svi.py for how this signal is escalated once detected --
    # deliberately weighted to guarantee Critical on its own, same
    # design decision as immediate_danger being the strongest single
    # scored signal, just larger given the stakes here are higher.
    "suicidal_ideation": [
        "I want to end my life.",
        "I don't want to live anymore.",
        "I've been thinking about killing myself.",
        "I feel like I should just die.",
        "I don't want to be alive anymore.",
        "I have been feeling so hopeless lately, I want to end my life and I don't know what else to do.",
        "Everything has gotten so bad that I keep thinking about ending it all.",

        # Indirect/euphemistic phrasings -- a very common real-world
        # pattern for expressing suicidal ideation, often appearing
        # before a more direct statement. Found live 2026-08-29: the
        # anchor set above (all direct statements) didn't generalize
        # to these at all, even though they're a well-documented
        # expression of the same thing.
        "Everyone would be better off without me.",
        "I just want to disappear forever.",
        "I can't see a way out of this, I just want it all to stop.",
        "I feel like a burden to everyone around me and it would be easier if I wasn't here.",
        "मुझे लगता है कि मेरे बिना सब बेहतर रहेंगे।",
        "నేను లేకపోతే అందరూ బాగుంటారు అనిపిస్తుంది.",
        "मैं अपनी जिंदगी खत्म करना चाहती हूं।",
        "मैं अब जीना नहीं चाहती।",
        "मुझे लगता है मुझे मर जाना चाहिए।",
        "నేను నా జీవితం ముగించాలని అనుకుంటున్నాను.",
        "నాకు ఇక బతకాలని అనిపించడం లేదు.",

        # Romanized Hindi
        "Main apni zindagi khatam karna chahti hoon.",
        "Main ab jeena nahi chahti.",
        "Mujhe lagta hai mujhe mar jaana chahiye.",

        # Romanized Telugu
        "Nenu naa jeevitham mugincha alani anukuntunnanu.",
        "Naaku ika bathakalani anipinchatledu.",

        # Urdu -- direct statements
        "میں اپنی زندگی ختم کرنا چاہتی ہوں۔",
        "میں اب زندہ نہیں رہنا چاہتی۔",
        "مجھے لگتا ہے مجھے مر جانا چاہیے۔",

        # Urdu -- indirect/euphemistic
        "مجھے لگتا ہے کہ میرے بغیر سب بہتر رہیں گے۔",
        "میں بس ہمیشہ کے لیے غائب ہو جانا چاہتی ہوں۔",

        # Romanized Urdu
        "Main apni zindagi khatam karna chahti hoon.",
        "Main ab zinda nahi rehna chahti.",
        "Mujhe lagta hai mujhe mar jana chahiye.",
        "Mujhe lagta hai ke mere bagair sab behtar rahenge.",

        # Bengali -- direct statements
        "আমি আমার জীবন শেষ করে দিতে চাই।",
        "আমি আর বাঁচতে চাই না।",
        "আমার মনে হয় আমার মরে যাওয়া উচিত।",

        # Bengali -- indirect/euphemistic
        "আমার মনে হয় আমাকে ছাড়া সবাই ভালো থাকবে।",
        "আমি শুধু চিরতরে হারিয়ে যেতে চাই।",

        # Romanized Bengali
        "Ami amar jibon shesh kore dite chai.",
        "Ami ar bachte chai na.",
        "Amar mone hoy amar more jawa uchit.",
        "Amar mone hoy amake chara shobai bhalo thakbe.",
    ],
}


# ============================================================
# SIGNAL HARD NEGATIVES
# ============================================================
#
# The shared NEUTRAL_EXAMPLES bank (generic small talk) rejects
# off-topic/gibberish text, but it can't reject a text that's genuinely
# safety-relevant while still being the WRONG signal -- confirmed live
# 2026-08-20 (teammate Yusra): "कोई मेरा पीछा कर रहा है।" (pure stalking,
# "someone is following me," no violence/threat mentioned) fired
# injury_present=true, and its Telugu equivalent fired both
# injury_present AND threat_present. Root cause: for short Hindi/Telugu
# phrases, multilingual-e5-small embeds "following/pursuing" close
# enough to "beating"/"threatening" that it clears the neutral margin
# on its own -- these anchor sets just aren't confusable with generic
# small talk, but they ARE confusable with each other.
#
# Fix: give the specific signals with a confirmed confusion pair their
# own hard-negative example set (real, topical, but NOT that signal),
# and require a genuine positive to beat that ceiling too, not just the
# generic neutral one. Only added where a real confusion was found and
# verified -- not applied speculatively to every signal.

SIGNAL_HARD_NEGATIVES = {

    # Confirmed live 2026-08-29: multilingual-e5-small puts almost any
    # first-person emotional-distress statement within 0.85-0.90+
    # cosine similarity of the suicidal_ideation anchors -- "I'm
    # stressed about exams" and "I want to end my life" read as
    # semantically close (both are emotional self-disclosure) even
    # though they're categorically different. The raw 0.72 threshold
    # provides essentially no separation here (everything clears it);
    # NEUTRAL_MARGIN alone wasn't enough either (a genuine crisis
    # statement scored a LOWER margin over the neutral baseline than
    # some of these hard negatives did). This set is what actually
    # does the discriminating work for this signal.
    "suicidal_ideation": [
        # A threat made against you is not a wish to die. Found live
        # 2026-09-02: "He hit me and said he will kill me tonight"
        # fired suicidal_ideation. Both sentences contain "kill me",
        # and the embedding does not by itself distinguish who is doing
        # the killing -- so the difference has to be taught here.
        #
        # Getting this wrong in this direction is not harmless even
        # though it escalates: it routes a physical-danger case down a
        # mental-health path, and it tells someone reporting a threat
        # on their life that the system heard them wanting to end it.
        "He said he will kill me tonight.",
        "He hit me and said he will kill me.",
        "They threatened to kill me.",
        "Someone threatened to kill me and I am scared.",
        "My husband said he would kill me if I told anyone.",
        "उसने कहा कि वह मुझे मार डालेगा।",
        "అతను నన్ను చంపేస్తానని అన్నాడు.",
        "Usne kaha ki woh mujhe maar dalega.",
        "Atanu nannu champestanani annadu.",

        "I had a really hard, exhausting day at work today and I am tired.",
        "I feel really down and stressed about my exams this week.",
        "My husband is very controlling and it makes me sad sometimes.",
        "I am so tired of everything going wrong lately.",
        "I feel hopeless about how things are going right now.",
        "मुझे आजकल बहुत थकान महसूस होती है और मेरा दिन बहुत खराब गया।",
        "నాకు ఈమధ్య చాలా అలసటగా ఉంది మరియు ఒత్తిడిగా అనిపిస్తుంది.",
        "آج میرا کام پر بہت مشکل اور تھکا دینے والا دن تھا اور میں تھکی ہوئی ہوں۔",
        "مجھے اس ہفتے اپنے امتحانوں کے بارے میں بہت پریشانی اور تناؤ محسوس ہو رہا ہے۔",
        "Aaj mera kaam par bahut mushkil aur thaka dene wala din tha aur main thaki hui hoon.",
        "আজ কাজে আমার খুব কঠিন এবং ক্লান্তিকর দিন গেছে এবং আমি ক্লান্ত।",
        "এই সপ্তাহে আমার পরীক্ষা নিয়ে খুব দুশ্চিন্তা এবং মানসিক চাপ অনুভব করছি।",
        "Aj kaje amar khub kothin ebong klanti-kor din geche ebong ami klanto.",
    ],

    "injury_present": [
        "Someone is following me everywhere.",
        "Someone keeps following me.",
        "Someone is watching me and following me.",
        "कोई मेरा पीछा कर रहा है।",
        "कोई मेरा लगातार पीछा कर रहा है।",
        "ఎవరైనా నన్ను వెంబడిస్తున్నారు.",
        "ఎవరైనా నన్ను నిరంతరం అనుసరిస్తున్నారు.",
        "Koi mera peecha kar raha hai.",
        "Evarina nannu vembadistunnaru.",
        "کوئی ہر جگہ میرا پیچھا کر رہا ہے۔",
        "کوئی مسلسل میرا پیچھا کرتا ہے۔",
        "Koi har jagah mera peecha kar raha hai.",
        "কেউ সবসময় আমাকে অনুসরণ করছে।",
        "কেউ আমার পিছু নিচ্ছে।",
        "Keu shobshomoy amake onushoron korche.",
    ],

    "threat_present": [
        "Someone is following me everywhere.",
        "Someone keeps following me.",
        "Someone is watching me and following me.",
        "कोई मेरा पीछा कर रहा है।",
        "कोई मेरा लगातार पीछा कर रहा है।",
        "ఎవరైనా నన్ను వెంబడిస్తున్నారు.",
        "ఎవరైనా నన్ను నిరంతరం అనుసరిస్తున్నారు.",
        "Koi mera peecha kar raha hai.",
        "Evarina nannu vembadistunnaru.",
        "کوئی ہر جگہ میرا پیچھا کر رہا ہے۔",
        "کوئی مسلسل میرا پیچھا کرتا ہے۔",
        "Koi har jagah mera peecha kar raha hai.",
        "কেউ সবসময় আমাকে অনুসরণ করছে।",
        "কেউ আমার পিছু নিচ্ছে।",
        "Keu shobshomoy amake onushoron korche.",
    ],

    # Confirmed live 2026-08-29 while extending this signal to Urdu/
    # Bengali (found via eval_pipeline.py's report, not introduced by
    # that work -- the underlying anchor set wasn't touched): plain
    # sexual_violence text with zero caste content scored 81% on
    # caste_based_motive -- ABOVE CASTE_MOTIVE_CONFIDENCE_FLOOR (80),
    # meaning kg.py attached five SC/ST Act citations to "A man forced
    # himself on me at a party last night." with no caste mention at
    # all. domestic_violence text showed the same pull at a lower,
    # already-gated 60%. Root cause not fully understood (no obvious
    # lexical overlap -- likely multilingual-e5-small placing
    # "dignity violation" framing close together in embedding space
    # regardless of cause), but the fix is the same pattern already
    # used for suicidal_ideation's mundane-distress confusion: give
    # caste_based_motive real, topical non-caste sexual_violence/
    # domestic_violence examples to discriminate against.
    "caste_based_motive": [
        "A man forced himself on me at a party last night.",
        "Someone sexually assaulted me.",
        "I was sexually abused.",
        "My husband is beating me.",
        "My husband threatens and abuses me.",
        "मेरे साथ यौन हिंसा हुई है।",
        "मेरे पति मुझे मार रहे हैं।",
        "నాపై లైంగిక దాడి జరిగింది.",
        "నా భర్త నన్ను కొడుతున్నాడు.",
        "کسی نے میرے ساتھ جنسی زیادتی کی۔",
        "میرا شوہر مجھے مارتا ہے۔",
        "কেউ আমার সাথে যৌন নির্যাতন করেছে।",
        "আমার স্বামী আমাকে মারে।",
    ],
}

hard_negative_embeddings = {}

for signal, examples in SIGNAL_HARD_NEGATIVES.items():

    hard_negative_embeddings[signal] = model.encode(
        ["query: " + example for example in examples],
        normalize_embeddings=True
    )


# How much a signal's own best match must beat its hard-negative
# category's best match by, before the signal is trusted over the
# more specific, documented confusion. Deliberately a separate,
# smaller constant from NEUTRAL_MARGIN rather than reusing it -- this
# check answers a different, easier question ("is this a better match
# for injury than for stalking?") than NEUTRAL_MARGIN's job ("is this
# meaningfully more than generic small talk?"). Reusing NEUTRAL_MARGIN
# here (i.e. requiring the full 0.04 lead over the hard negative too)
# was tried first and caused a real regression: a genuine Telugu
# domestic-violence threat only led its stalking hard-negative by
# 0.0352, just under 0.04, and got wrongly rejected. The four
# calibration cases (2 confirmed bugs, 2 genuine positives) show a
# clean sign flip at zero -- genuine positives beat their hard
# negative, the confirmed false positives lose to it -- so 0.02 (half
# of NEUTRAL_MARGIN, as a safety margin against float noise right at
# the boundary) separates them with room to spare in both directions.
HARD_NEGATIVE_MARGIN = 0.02


def hard_negative_ceiling(query_embedding, signal):
    """
    How well this query matches signal's documented confusion category,
    if it has one. Returns None for signals with no hard-negative set
    (most of them) so callers can skip the check entirely.
    """

    if signal not in hard_negative_embeddings:
        return None

    similarities = query_embedding @ hard_negative_embeddings[signal].T

    return float(similarities.max())


# ============================================================
# BUILD SIGNAL EMBEDDINGS
# ============================================================

signal_embeddings = {}

for signal, examples in SIGNAL_EXAMPLES.items():

    embeddings = model.encode(
        ["query: " + example for example in examples],
        normalize_embeddings=True
    )

    signal_embeddings[signal] = embeddings


# ============================================================
# DETECT SIGNAL
# ============================================================

def detect_signal(text, signal, threshold=0.72, neutral_margin=None):
    """
    Detect whether a particular safety signal is present.

    Requires both an absolute similarity floor and a lead over the
    neutral baseline -- ordinary/off-topic text regularly clears a
    flat threshold on its own (see NEUTRAL_MARGIN above), which was
    causing signals like immediate_danger to fire on unrelated text.

    neutral_margin overrides the shared NEUTRAL_MARGIN constant for
    this one call -- added for suicidal_ideation (see understand()'s
    call site), found live 2026-08-29: a real, longer-form suicidal-
    ideation report ("I have been feeling so hopeless lately. I want
    to end my life...") sat at 0.882 similarity to the signal but an
    even higher 0.888 to the neutral baseline (emotionally-loaded
    language broadly resembles NEUTRAL_EXAMPLES more than a terse
    anchor phrase does), failing NEUTRAL_MARGIN's required +0.04 lead
    even though the raw threshold cleared easily -- and because it
    silently didn't fire, the response fell through to normal RAG
    grounding, which surfaced and cited abetment-of-suicide *penalty*
    law to someone expressing suicidal ideation. For every other
    signal a missed detection degrades the response; for this one it
    can produce something actively harmful, so it gets its own,
    deliberately looser margin -- a false positive here just means
    offering crisis support to someone who didn't strictly need it,
    which is a low-cost error next to the alternative.
    """

    if neutral_margin is None:
        neutral_margin = NEUTRAL_MARGIN

    query_embedding = model.encode(
        ["query: " + text],
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        query_embedding,
        signal_embeddings[signal]
    )[0]

    best_similarity = float(similarities.max())

    neutral_ceil = neutral_ceiling(query_embedding)
    neutral_margin_ok = (best_similarity - neutral_ceil) >= neutral_margin

    hard_neg_ceil = hard_negative_ceiling(query_embedding, signal)
    hard_negative_margin_ok = (
        hard_neg_ceil is None
        or (best_similarity - hard_neg_ceil) >= HARD_NEGATIVE_MARGIN
    )

    present = (
        best_similarity >= threshold
        and neutral_margin_ok
        and hard_negative_margin_ok
    )

    if present:
        # Calibrate against the neutral baseline only, same formula
        # every other detector in this file uses -- the hard-negative
        # check already passed by the time we get here, so it
        # shouldn't compress a genuine positive's displayed confidence.
        confidence = calibrate_confidence(best_similarity, query_embedding, ceiling=neutral_ceil)
    else:
        # Rejected -- report confidence against whichever ceiling
        # actually rejected it (the higher of the two), so
        # confidence_breakdown never shows a misleadingly high number
        # for a signal the system decided is NOT present.
        effective_ceiling = neutral_ceil if hard_neg_ceil is None else max(neutral_ceil, hard_neg_ceil)
        confidence = calibrate_confidence(best_similarity, query_embedding, ceiling=effective_ceiling)

    return present, confidence


# ============================================================
# RELATIONSHIP DETECTION
# ============================================================

RELATIONSHIP_EXAMPLES = {

    "husband": [
        "My husband is hurting me.",
        "My husband is threatening me.",
        "मेरे पति मुझे मार रहे हैं।",
        "मेरे पति मुझे धमकी दे रहे हैं।",
        "నా భర్త నన్ను కొడుతున్నాడు.",
        "నా భర్త నన్ను బెదిరిస్తున్నాడు.",

        # Romanized Hindi
        "Mere pati mujhe maar rahe hain.",
        "Mere pati mujhe dhamki de rahe hain.",

        # Romanized Telugu
        "Naa bharta nannu kodutunnadu.",
        "Naa bharta nannu bedhiristunnadu."
    ],

    "parent": [
        "My father hits me.",
        "My father is threatening me.",
        "My mother hurts me.",
        "मेरे पिता मुझे मारते हैं।",
        "मेरे पिता मुझे धमकाते हैं।",
        "నా తండ్రి నన్ను కొడతాడు.",
        "నా తండ్రి నన్ను బెదిరిస్తాడు.",

        # Romanized Hindi
        "Mere pita mujhe maarte hain.",
        "Mere pita mujhe dhamkate hain.",

        # Romanized Telugu
        "Naa thandri nannu kodutadu.",
        "Naa thandri nannu bedhiristadu."
    ],

    "family_member": [
        "A family member is hurting me.",
        "Someone in my family is abusing me.",
        "मेरे परिवार का सदस्य मुझे चोट पहुँचा रहा है।",
        "मेरे परिवार का कोई व्यक्ति मुझे परेशान कर रहा है।",
        "నా కుటుంబ సభ్యుడు నన్ను హింసిస్తున్నాడు.",

        # Romanized Hindi
        "Mere parivar ka sadasya mujhe chot pahuncha raha hai.",
        "Mere parivar ka koi vyakti mujhe pareshan kar raha hai.",

        # Romanized Telugu
        "Naa kutumba sabhyudu nannu himsistunnadu."
    ],

    "stranger": [
        "A stranger is attacking me.",
        "Someone I don't know is threatening me.",
        "एक अजनबी मुझ पर हमला कर रहा है।",
        "कोई अनजान व्यक्ति मुझे धमका रहा है।",
        "ఒక అపరిచితుడు నాపై దాడి చేస్తున్నాడు.",

        # Romanized Hindi
        "Ek ajnabi mujh par hamla kar raha hai.",
        "Koi anjaan vyakti mujhe dhamka raha hai.",

        # Romanized Telugu
        "Oka aparichitudu naapai daadi chestunnadu."
    ],
}


relationship_texts = []
relationship_labels = []

for relationship, examples in RELATIONSHIP_EXAMPLES.items():

    for example in examples:

        relationship_texts.append(
            "query: " + example
        )

        relationship_labels.append(
            relationship
        )


relationship_embeddings = model.encode(
    relationship_texts,
    normalize_embeddings=True
)


# ============================================================
# DETECT RELATIONSHIP
# ============================================================

def detect_relationship(text, threshold=0.70):

    query_embedding = model.encode(
        ["query: " + text],
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        query_embedding,
        relationship_embeddings
    )[0]

    best_index = similarities.argmax()
    best_similarity = float(similarities[best_index])

    margin = best_similarity - neutral_ceiling(query_embedding)

    confidence = calibrate_confidence(best_similarity, query_embedding)

    if best_similarity < threshold or margin < NEUTRAL_MARGIN:
        return None, confidence

    return (
        relationship_labels[best_index],
        confidence
    )


# ============================================================
# LOCATION DETECTION
# ============================================================
#
# Real-world place types, not specific named cities/streets --
# "this happened at a bus stop" is directly actionable and doesn't
# require named-entity recognition, just the same semantic-
# similarity + neutral-margin pattern used everywhere else here.
# Most reports won't mention a location at all, so returning None
# for anything not confidently matched is the correct default, not
# a failure.

LOCATION_EXAMPLES = {

    "bus_stop": [
        "It happened at a bus stop.",
        "I was waiting at the bus stop when it happened.",
        "यह बस स्टॉप पर हुआ।",
        "ఇది బస్ స్టాప్ వద్ద జరిగింది.",

        # Romanized Hindi
        "Yeh bus stop par hua.",

        # Romanized Telugu
        "Idi bus stop daggara jarigindi."
    ],

    "railway_station": [
        "It happened at the railway station.",
        "I was at the train station when this happened.",
        "यह रेलवे स्टेशन पर हुआ।",
        "ఇది రైల్వే స్టేషన్‌లో జరిగింది.",

        # Romanized Hindi
        "Yeh railway station par hua.",

        # Romanized Telugu
        "Idi railway station lo jarigindi."
    ],

    "hostel": [
        "It happened in my hostel.",
        "This happened inside the hostel.",
        "यह मेरे छात्रावास में हुआ।",
        "ఇది నా వసతి గృహంలో జరిగింది.",

        # Romanized Hindi
        "Yeh mere hostel mein hua.",

        # Romanized Telugu
        "Idi naa hostel lo jarigindi."
    ],

    "home": [
        "This happened at my home.",
        "It happened inside the house.",
        "यह मेरे घर पर हुआ।",
        "ఇది నా ఇంట్లో జరిగింది.",

        # Romanized Hindi
        "Yeh mere ghar par hua.",

        # Romanized Telugu
        "Idi naa intlo jarigindi."
    ],

    "workplace": [
        "This happened at my workplace.",
        "It happened in the office.",
        "यह मेरे कार्यस्थल पर हुआ।",
        "ఇది నా పని స్థలంలో జరిగింది.",

        # Romanized Hindi
        "Yeh mere workplace par hua.",

        # Romanized Telugu
        "Idi naa work place lo jarigindi."
    ],

    "college_campus": [
        "It happened on campus.",
        "This happened at college.",
        "यह कॉलेज परिसर में हुआ।",
        "ఇది కళాశాల ప్రాంగణంలో జరిగింది.",

        # Romanized Hindi
        "Yeh college campus mein hua.",

        # Romanized Telugu
        "Idi college campus lo jarigindi."
    ],

    "market": [
        "It happened at the market.",
        "This happened while I was at the market.",
        "यह बाज़ार में हुआ।",
        "ఇది మార్కెట్‌లో జరిగింది.",

        # Romanized Hindi
        "Yeh bazaar mein hua.",

        # Romanized Telugu
        "Idi market lo jarigindi."
    ],

    "street": [
        "It happened on the street.",
        "This happened while I was walking on the road.",
        "यह सड़क पर हुआ।",
        "ఇది రోడ్డుపై జరిగింది.",

        # Romanized Hindi
        "Yeh sadak par hua.",

        # Romanized Telugu
        "Idi road meeda jarigindi."
    ],

    "police_station": [
        "It happened at the police station.",
        "This happened when I went to the police station.",
        "यह थाने में हुआ।",
        "ఇది పోలీస్ స్టేషన్‌లో జరిగింది.",

        # Romanized Hindi
        "Yeh thane mein hua.",

        # Romanized Telugu
        "Idi police station lo jarigindi."
    ],

    "hospital": [
        "It happened at the hospital.",
        "This happened while I was at the hospital.",
        "यह अस्पताल में हुआ।",
        "ఇది ఆసుపత్రిలో జరిగింది.",

        # Romanized Hindi
        "Yeh aspatal mein hua.",

        # Romanized Telugu
        "Idi hospital lo jarigindi."
    ],

    "park": [
        "It happened in the park.",
        "This happened while I was at the park.",
        "यह पार्क में हुआ।",
        "ఇది పార్క్‌లో జరిగింది.",

        # Romanized Hindi
        "Yeh park mein hua.",

        # Romanized Telugu
        "Idi park lo jarigindi."
    ],
}


location_texts = []
location_labels = []

for location, examples in LOCATION_EXAMPLES.items():

    for example in examples:

        location_texts.append(
            "query: " + example
        )

        location_labels.append(
            location
        )


location_embeddings = model.encode(
    location_texts,
    normalize_embeddings=True
)


# ============================================================
# DETECT LOCATION
# ============================================================

def detect_location(text, threshold=0.70):
    """
    Detect a real-world place type mentioned in the report, if any.
    Most reports won't mention a location -- returning None is the
    expected, correct outcome for those, not a detection failure.
    """

    query_embedding = model.encode(
        ["query: " + text],
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        query_embedding,
        location_embeddings
    )[0]

    best_index = similarities.argmax()
    best_similarity = float(similarities[best_index])

    margin = best_similarity - neutral_ceiling(query_embedding)

    confidence = calibrate_confidence(best_similarity, query_embedding)

    if best_similarity < threshold or margin < NEUTRAL_MARGIN:
        return None, confidence

    return (
        location_labels[best_index],
        confidence
    )


# ============================================================
# UNDERSTAND INCIDENT
# ============================================================

def detect_script(text, language):
    """
    Whether the text was written in the language's native script or
    romanized (Latin letters) -- independent of detect_language(),
    so this also works when the caller passes language explicitly
    instead of relying on auto-detection.

    This exists so Athena can reply in the same script the user
    wrote in: previously the response always switched to native
    Devanagari/Telugu script even for romanized input, which is
    backwards for anyone who speaks the language but only
    types/reads it in Latin letters (common on phone keyboards).
    """

    if language == "hi":
        has_native = any(0x0900 <= ord(char) <= 0x097F for char in text)
        return "native" if has_native else "romanized"

    if language == "te":
        has_native = any(0x0C00 <= ord(char) <= 0x0C7F for char in text)
        return "native" if has_native else "romanized"

    return "latin"


def understand(text, language=None):
    """
    Convert a multilingual incident report into
    a structured incident representation.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not text or not text.strip():
        raise ValueError("Incident text cannot be empty.")

    # --------------------------------------------------------
    # Automatically detect language when not supplied
    # --------------------------------------------------------

    if language is None:
        language = detect_language(text)

    script = detect_script(text, language)

    incident_type, incident_confidence = classify_incident(text)

    threat_present, threat_score = detect_signal(
        text,
        "threat_present"
    )

    injury_present, injury_score = detect_signal(
        text,
        "injury_present"
    )

    immediate_danger, danger_score = detect_signal(
        text,
        "immediate_danger"
    )

    caste_based_motive, caste_score = detect_signal(
        text,
        "caste_based_motive"
    )

    suicidal_ideation, suicidal_score = detect_signal(
        text,
        "suicidal_ideation",
    )

    relationship, relationship_score = detect_relationship(text)

    location, location_score = detect_location(text)

    violence_types = []

    if injury_present:
        violence_types.append("physical")

    if threat_present:
        violence_types.append("threat")

    if incident_type == "sexual_violence":
        violence_types.append("sexual")

    if incident_type == "cyber_harassment":
        violence_types.append("cyber")

    # --------------------------------------------------------
    # Conservative confidence
    # --------------------------------------------------------

    confidence = round(
        incident_confidence * 100,
        2
    )

    # Per-field breakdown of the same calibrated confidence, instead
    # of discarding threat_score/injury_score/danger_score/
    # relationship_score/location_score after they've already been
    # computed. Every field here is calibrated the same way as the
    # top-level confidence (see calibrate_confidence) -- comparable
    # to each other, not raw cosine similarity dressed up as a
    # percentage.
    confidence_breakdown = {
        "incident_type": confidence,
        "threat": round(threat_score * 100, 2),
        "injury": round(injury_score * 100, 2),
        "immediate_danger": round(danger_score * 100, 2),
        "relationship": round(relationship_score * 100, 2),
        "location": round(location_score * 100, 2),
        "caste_based_motive": round(caste_score * 100, 2),
        "suicidal_ideation": round(suicidal_score * 100, 2),
    }

    return {
        "original_text": text,
        "language": language,
        "script": script,
        "incident_type": incident_type,
        "violence_types": violence_types,
        "immediate_danger": immediate_danger,
        "threat_present": threat_present,
        "injury_present": injury_present,
        "relationship": relationship,
        "location": location,
        "caste_based_motive": caste_based_motive,
        "suicidal_ideation": suicidal_ideation,
        "confidence": confidence,
        "confidence_breakdown": confidence_breakdown,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_reports = [

        (
            "en",
            "My husband is threatening me and physically hurting me."
        ),

        (
            "hi",
            "मेरे पति मुझे धमकी दे रहे हैं और शारीरिक रूप से चोट पहुँचा रहे हैं।"
        ),

        (
            "te",
            "నా భర్త నన్ను బెదిరిస్తున్నాడు మరియు శారీరకంగా హింసిస్తున్నాడు."
        ),
    ]

    for language, report in test_reports:

        print("\n" + "=" * 80)
        print(SUPPORTED_LANGUAGES[language])
        print("=" * 80)

        result = understand(
            report,
            language=language
        )

        for key, value in result.items():

            print(
                f"{key:20}: {value}"
            )