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

    best_language = "en"
    best_similarity = -1

    for language, embeddings in language_embeddings.items():

        similarities = query_embedding @ embeddings.T

        similarity = float(similarities.max())

        if similarity > best_similarity:
            best_similarity = similarity
            best_language = language

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
        "నా కుటుంబ సభ్యుడు నన్ను ఇంట్లో వేధిస్తున్నాడు."
    ],

    "sexual_violence": [
        "Someone sexually assaulted me.",
        "I was sexually abused.",
        "Someone forced me into sexual activity.",
        "मेरे साथ यौन हिंसा हुई है।",
        "मेरे साथ यौन दुर्व्यवहार किया गया।",
        "నాపై లైంగిక దాడి జరిగింది.",
        "నన్ను లైంగికంగా వేధించారు."
    ],

    "harassment": [
        "Someone is constantly harassing me.",
        "I am being verbally abused.",
        "Someone keeps insulting and threatening me.",
        "कोई मुझे लगातार परेशान कर रहा है।",
        "कोई मुझे बार-बार धमका रहा है।",
        "ఎవరైనా నన్ను నిరంతరం వేధిస్తున్నారు.",
        "ఎవరైనా నన్ను పదే పదే బెదిరిస్తున్నారు."
    ],

    "stalking": [
        "Someone is following me everywhere.",
        "Someone keeps following me.",
        "Someone is watching me and following me.",
        "कोई मेरा पीछा कर रहा है।",
        "कोई मेरा लगातार पीछा कर रहा है।",
        "ఎవరైనా నన్ను వెంబడిస్తున్నారు.",
        "ఎవరైనా నన్ను నిరంతరం అనుసరిస్తున్నారు."
    ],

    "trafficking": [
        "I am being trafficked.",
        "Someone is forcing women into trafficking.",
        "I was taken somewhere against my will for exploitation.",
        "मुझे जबरन तस्करी के लिए ले जाया गया।",
        "मुझे शोषण के लिए जबरदस्ती ले जाया गया।",
        "నన్ను అక్రమ రవాణా కోసం బలవంతంగా తీసుకెళ్లారు.",
        "నన్ను దోపిడీ కోసం బలవంతంగా తీసుకెళ్లారు."
    ],

    "cyber_harassment": [
        "Someone is threatening me online.",
        "Someone is harassing me through social media.",
        "Someone is sharing my private photos online.",
        "कोई मुझे ऑनलाइन धमका रहा है।",
        "कोई सोशल मीडिया पर मुझे परेशान कर रहा है।",
        "ఎవరైనా నన్ను ఆన్‌లైన్‌లో బెదిరిస్తున్నారు.",
        "ఎవరైనా సోషల్ మీడియాలో నన్ను వేధిస్తున్నారు."
    ],

    "missing_person": [
        "My daughter is missing.",
        "My sister has disappeared.",
        "I cannot find my family member.",
        "मेरी बेटी लापता है।",
        "मेरी बहन गायब हो गई है।",
        "నా కుమార్తె కనిపించడం లేదు.",
        "నా సోదరి కనిపించడం లేదు."
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
    confidence = float(similarities[best_index])

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
        "అతను నన్ను బెదిరిస్తున్నాడు."
    ],

    "injury_present": [
        "I have been physically hurt.",
        "Someone is beating me.",
        "I have injuries.",
        "मुझे शारीरिक चोट लगी है।",
        "मुझे मारा जा रहा है।",
        "నాకు శారీరక గాయాలు అయ్యాయి.",
        "నన్ను కొడుతున్నారు."
    ],

    "immediate_danger": [
        "I am in immediate danger.",
        "I am afraid I will be hurt right now.",
        "He is attacking me right now.",
        "मुझे अभी खतरा है।",
        "वह अभी मुझ पर हमला कर रहा है।",
        "నాకు ఇప్పుడు ప్రమాదం ఉంది.",
        "అతను ఇప్పుడు నాపై దాడి చేస్తున్నాడు."
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

    return best_similarity >= threshold, best_similarity


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
        "నా భర్త నన్ను బెదిరిస్తున్నాడు."
    ],

    "family_member": [
        "A family member is hurting me.",
        "Someone in my family is abusing me.",
        "मेरे परिवार का सदस्य मुझे चोट पहुँचा रहा है।",
        "मेरे परिवार का कोई व्यक्ति मुझे परेशान कर रहा है।",
        "నా కుటుంబ సభ్యుడు నన్ను హింసిస్తున్నాడు."
    ],

    "stranger": [
        "A stranger is attacking me.",
        "Someone I don't know is threatening me.",
        "एक अजनबी मुझ पर हमला कर रहा है।",
        "कोई अनजान व्यक्ति मुझे धमका रहा है।",
        "ఒక అపరిచితుడు నాపై దాడి చేస్తున్నాడు."
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

    if best_similarity < threshold:
        return None, best_similarity

    return (
        relationship_labels[best_index],
        best_similarity
    )


# ============================================================
# UNDERSTAND INCIDENT
# ============================================================

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
        "incident_type": incident_type,
        "violence_types": violence_types,
        "immediate_danger": immediate_danger,
        "threat_present": threat_present,
        "injury_present": injury_present,
        "relationship": relationship,
        "location": None,
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