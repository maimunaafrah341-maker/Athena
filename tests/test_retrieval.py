import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from retrieval import retrieve


# ============================================================
# ATHENA RETRIEVAL EVALUATION SET
# ============================================================

TEST_QUERIES = [
    {
        "topic": "One Stop Centre services",
        "language": "English",
        "query": "What services are available at a One Stop Centre?",
    },
    {
        "topic": "One Stop Centre services",
        "language": "Hindi",
        "query": "वन स्टॉप सेंटर में कौन सी सेवाएं उपलब्ध हैं?",
    },
    {
        "topic": "One Stop Centre services",
        "language": "Telugu",
        "query": "వన్ స్టాప్ సెంటర్‌లో ఏ సేవలు అందుబాటులో ఉన్నాయి?",
    },

    {
        "topic": "Women Helpline",
        "language": "English",
        "query": "What help can a woman get through the Women Helpline?",
    },
    {
        "topic": "Women Helpline",
        "language": "Hindi",
        "query": "महिला हेल्पलाइन से महिला को किस तरह की सहायता मिल सकती है?",
    },
    {
        "topic": "Women Helpline",
        "language": "Telugu",
        "query": "మహిళా హెల్ప్‌లైన్ ద్వారా మహిళకు ఎలాంటి సహాయం లభిస్తుంది?",
    },

    {
        "topic": "Emergency assistance",
        "language": "English",
        "query": "What emergency assistance is available to women facing violence?",
    },
    {
        "topic": "Emergency assistance",
        "language": "Hindi",
        "query": "हिंसा का सामना करने वाली महिलाओं के लिए कौन सी आपातकालीन सहायता उपलब्ध है?",
    },
    {
        "topic": "Emergency assistance",
        "language": "Telugu",
        "query": "హింసను ఎదుర్కొంటున్న మహిళలకు ఏ అత్యవసర సహాయం అందుబాటులో ఉంది?",
    },

    {
        "topic": "Legal aid",
        "language": "English",
        "query": "Can a woman facing violence receive legal assistance?",
    },
    {
        "topic": "Legal aid",
        "language": "Hindi",
        "query": "क्या हिंसा का सामना करने वाली महिला को कानूनी सहायता मिल सकती है?",
    },
    {
        "topic": "Legal aid",
        "language": "Telugu",
        "query": "హింసను ఎదుర్కొంటున్న మహిళకు న్యాయ సహాయం లభిస్తుందా?",
    },

    {
        "topic": "Temporary shelter",
        "language": "English",
        "query": "Can a woman facing violence get temporary shelter?",
    },
    {
        "topic": "Temporary shelter",
        "language": "Hindi",
        "query": "क्या हिंसा का सामना करने वाली महिला को अस्थायी आश्रय मिल सकता है?",
    },
    {
        "topic": "Temporary shelter",
        "language": "Telugu",
        "query": "హింసను ఎదుర్కొంటున్న మహిళకు తాత్కాలిక ఆశ్రయం లభిస్తుందా?",
    },

    {
        "topic": "Police assistance",
        "language": "English",
        "query": "Can women affected by violence receive police assistance?",
    },
    {
        "topic": "Police assistance",
        "language": "Hindi",
        "query": "क्या हिंसा से प्रभावित महिलाओं को पुलिस सहायता मिल सकती है?",
    },
    {
        "topic": "Police assistance",
        "language": "Telugu",
        "query": "హింసకు గురైన మహిళలకు పోలీసు సహాయం లభిస్తుందా?",
    },

    {
        "topic": "Protection Officer",
        "language": "English",
        "query": "What role does a Protection Officer have in supporting women?",
    },
    {
        "topic": "Protection Officer",
        "language": "Hindi",
        "query": "महिलाओं की सहायता में संरक्षण अधिकारी की क्या भूमिका है?",
    },
    {
        "topic": "Protection Officer",
        "language": "Telugu",
        "query": "మహిళలకు సహాయం చేయడంలో రక్షణ అధికారి పాత్ర ఏమిటి?",
    },

    {
        "topic": "Domestic violence",
        "language": "English",
        "query": "What types of abuse are covered under domestic violence law?",
    },
    {
        "topic": "Domestic violence",
        "language": "Hindi",
        "query": "घरेलू हिंसा कानून में किस प्रकार के दुर्व्यवहार शामिल हैं?",
    },
    {
        "topic": "Domestic violence",
        "language": "Telugu",
        "query": "గృహ హింస చట్టం కింద ఏ రకాల వేధింపులు ఉన్నాయి?",
    },
]


# ============================================================
# RUN TESTS
# ============================================================

def run_tests():

    print("=" * 80)
    print("ATHENA RETRIEVAL EVALUATION")
    print("=" * 80)

    total = len(TEST_QUERIES)

    print(f"\nTotal test queries: {total}")

    for index, test in enumerate(TEST_QUERIES, start=1):

        results = retrieve(test["query"], top_k=3)

        print("\n" + "=" * 80)
        print(f"TEST {index}/{total}")
        print("=" * 80)

        print(f"Topic:    {test['topic']}")
        print(f"Language: {test['language']}")
        print(f"Query:    {test['query']}")

        print("\nTop 3 Retrieved Results:")

        for rank, result in enumerate(results, start=1):

            print(
                f"\n  #{rank} "
                f"{result['similarity']:.4f} | "
                f"{result['source']} | "
                f"Page {result['page']}"
            )

            # Print only a short preview
            preview = result["text"].replace("\n", " ")

            if len(preview) > 250:
                preview = preview[:250] + "..."

            print(f"     {preview}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    run_tests()