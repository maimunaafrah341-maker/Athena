import re

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


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

MODEL_NAME = "intfloat/multilingual-e5-small"

print("Loading multilingual understanding model...")

model = SentenceTransformer(MODEL_NAME)

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
    ],

    "te": [
        "ఇది మహిళపై హింసకు సంబంధించిన తెలుగు ఘటన నివేదిక.",
        "నేను ప్రమాదంలో ఉన్నాను మరియు నాకు సహాయం కావాలి.",
        "ఎవరో నన్ను బెదిరిస్తున్నారు.",

        # Romanized Telugu
        "Idi mahilapai hinsaku sambandhinchina Telugu ghatana nivedika.",
        "Nenu pramadamlo unnanu mariyu naaku sahayam kavali.",
        "Evaro nannu bediristunnaru.",
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

    for char in text:

        code = ord(char)

        # Devanagari: U+0900 - U+097F
        if 0x0900 <= code <= 0x097F:
            devanagari_count += 1

        # Telugu: U+0C00 - U+0C7F
        elif 0x0C00 <= code <= 0x0C7F:
            telugu_count += 1

    # --------------------------------------------------------
    # Strong native-script detection
    # --------------------------------------------------------

    if devanagari_count > 0:
        return "hi"

    if telugu_count > 0:
        return "te"

    # --------------------------------------------------------
    # Fallback to multilingual semantic detection
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
        "Naa kutumba sabhyudu nannu intlo vedhistunnadu."
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
        "Nannu laingikanga vedhincharu."
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
        "Evarina nannu pade pade bedhiristunnaru."
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
        "Evarina nannu nirantaram anusaristunnaru."
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
        "Nannu dopidi kosam balavantanga teesukellaru."
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
        "Evarina social media lo nannu vedhistunnaru."
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
        "Naa sodari kanipinchadam ledu."
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

    # Calibrate confidence against the neutral baseline instead of
    # trusting the raw cosine score: a margin of NEUTRAL_MARGIN over
    # neutral text maps to 100% confidence, a margin of 0 (i.e. this
    # text matches the incident category no better than it matches
    # ordinary small talk) maps to 0%.
    margin = raw_similarity - neutral_ceiling(query_embedding)
    confidence = max(0.0, min(1.0, margin / (NEUTRAL_MARGIN * 2.5)))

    return incident_type, confidence


# ============================================================
# SIGNAL DETECTION
# ============================================================

SIGNAL_EXAMPLES = {

    "threat_present": [
        "I am being threatened.",
        "Someone is threatening me.",
        "He threatened to hurt me.",
        "मुझे धमकी दी जा रही है।",
        "वह मुझे धमकी दे रहा है।",
        "నన్ను బెదిరిస్తున్నారు.",
        "అతను నన్ను బెదిరిస్తున్నాడు.",

        # Romanized Hindi
        "Mujhe dhamki di ja rahi hai.",
        "Woh mujhe dhamki de raha hai.",

        # Romanized Telugu
        "Nannu bedhiristunnaru.",
        "Atanu nannu bedhiristunnadu."
    ],

    "injury_present": [
        "I have been physically hurt.",
        "Someone is beating me.",
        "I have injuries.",
        "मुझे शारीरिक चोट लगी है।",
        "मुझे मारा जा रहा है।",
        "నాకు శారీరక గాయాలు అయ్యాయి.",
        "నన్ను కొడుతున్నారు.",

        # Romanized Hindi
        "Mujhe sharirik chot lagi hai.",
        "Mujhe mara ja raha hai.",

        # Romanized Telugu
        "Naaku shareerika gayalu ayyayi.",
        "Nannu kodutunnaru."
    ],

    "immediate_danger": [
        "I am in immediate danger.",
        "I am afraid I will be hurt right now.",
        "He is attacking me right now.",
        "मुझे अभी खतरा है।",
        "वह अभी मुझ पर हमला कर रहा है।",
        "నాకు ఇప్పుడు ప్రమాదం ఉంది.",
        "అతను ఇప్పుడు నాపై దాడి చేస్తున్నాడు.",

        # Romanized Hindi
        "Mujhe abhi khatra hai.",
        "Woh abhi mujh par hamla kar raha hai.",

        # Romanized Telugu
        "Naaku ippudu pramadam undi.",
        "Atanu ippudu naapai daadi chestunnadu."
    ],
}


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

def detect_signal(text, signal, threshold=0.72):
    """
    Detect whether a particular safety signal is present.

    Requires both an absolute similarity floor and a lead over the
    neutral baseline -- ordinary/off-topic text regularly clears a
    flat threshold on its own (see NEUTRAL_MARGIN above), which was
    causing signals like immediate_danger to fire on unrelated text.
    """

    query_embedding = model.encode(
        ["query: " + text],
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        query_embedding,
        signal_embeddings[signal]
    )[0]

    best_similarity = float(similarities.max())

    margin = best_similarity - neutral_ceiling(query_embedding)

    present = best_similarity >= threshold and margin >= NEUTRAL_MARGIN

    return present, best_similarity


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

    if best_similarity < threshold or margin < NEUTRAL_MARGIN:
        return None, best_similarity

    return (
        relationship_labels[best_index],
        best_similarity
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

    if best_similarity < threshold or margin < NEUTRAL_MARGIN:
        return None, best_similarity

    return (
        location_labels[best_index],
        best_similarity
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
        "confidence": confidence,
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