from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

MODEL_NAME = "intfloat/multilingual-e5-small"

model = SentenceTransformer(MODEL_NAME)

tests = [
    {
        "english": "Someone is following me and I feel unsafe.",
        "hindi": "कोई मेरा पीछा कर रहा है और मुझे असुरक्षित महसूस हो रहा है।",
        "telugu": "ఎవరో నన్ను వెంబడిస్తున్నారు మరియు నాకు అసురక్షితంగా అనిపిస్తోంది."
    },
    {
        "english": "I am in immediate danger and need help.",
        "hindi": "मैं तत्काल खतरे में हूँ और मुझे मदद की जरूरत है।",
        "telugu": "నేను తక్షణ ప్రమాదంలో ఉన్నాను మరియు నాకు సహాయం కావాలి."
    },
    {
        "english": "I want to report harassment.",
        "hindi": "मैं उत्पीड़न की शिकायत करना चाहती हूँ।",
        "telugu": "నేను వేధింపుల గురించి ఫిర్యాదు చేయాలనుకుంటున్నాను."
    },
    {
        "english": "Someone is threatening me.",
        "hindi": "कोई मुझे धमकी दे रहा है।",
        "telugu": "ఎవరో నన్ను బెదిరిస్తున్నారు."
    }
]

print("Model:", MODEL_NAME)
print("Embedding test: English / Hindi / Telugu")
print("=" * 70)

for i, test in enumerate(tests, start=1):

    english_embedding = model.encode(
        "query: " + test["english"]
    )

    hindi_embedding = model.encode(
        "passage: " + test["hindi"]
    )

    telugu_embedding = model.encode(
        "passage: " + test["telugu"]
    )

    english_hindi = float(
        cos_sim(english_embedding, hindi_embedding)
    )

    english_telugu = float(
        cos_sim(english_embedding, telugu_embedding)
    )

    hindi_telugu = float(
        cos_sim(hindi_embedding, telugu_embedding)
    )

    print(f"\nTest {i}")
    print("English:", test["english"])
    print("Hindi:", test["hindi"])
    print("Telugu:", test["telugu"])

    print("\nSimilarity:")
    print("English ↔ Hindi: ", round(english_hindi, 4))
    print("English ↔ Telugu:", round(english_telugu, 4))
    print("Hindi ↔ Telugu:  ", round(hindi_telugu, 4))

    print("-" * 70)

print("\nEmbedding model test completed.")