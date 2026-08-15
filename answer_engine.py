import os

from dotenv import load_dotenv
from google import genai

from retrieval import retrieve


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

TOP_K = 5

# Minimum top-result similarity required before we trust retrieval
# enough to generate an answer. Below this, we do NOT call the model —
# we escalate instead. This is a placeholder value: tune it against
# real similarity scores from the 24-query eval set once you've
# logged what "good" vs "weak" retrievals actually score.
CONFIDENCE_THRESHOLD = 0.60


# ============================================================
# CONNECT TO GEMINI
# ============================================================

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# BUILD PROMPT
# ============================================================

def build_prompt(query, evidence):
    """
    Build a grounded prompt that forces the model to answer using
    ONLY the retrieved evidence, and to cite a source for every claim.
    """

    evidence_block = ""

    for i, chunk in enumerate(evidence, start=1):
        evidence_block += (
            f"\n[EVIDENCE {i}] Source: {chunk['source']}, "
            f"Page: {chunk['page']}\n"
            f"{chunk['text']}\n"
        )

    prompt = f"""You are Athena, an assistant that gives women verified, \
factual information about safety support services — helplines, One Stop \
Centres, legal protections, shelters, police assistance, and related \
procedures.

STRICT RULES:
1. Answer using ONLY the evidence provided below. Do not use outside knowledge.
2. Every claim you make must be traceable to one of the evidence chunks.
3. After each claim, cite it like this: [Source: <source>, Page: <page>].
4. If the evidence does not fully answer the question, say so plainly \
instead of guessing or filling gaps.
5. Keep the tone calm, clear, and supportive. The person reading this \
may be in distress.

EVIDENCE:
{evidence_block}

QUESTION:
{query}

ANSWER:"""

    return prompt


# ============================================================
# CALL GEMINI
# ============================================================

def call_gemini(prompt):
    """
    Send a prompt to Gemini and return the raw text response.

    Kept as its own function so the underlying model/provider (e.g.
    switching to Claude closer to the demo) can be swapped later
    without touching the rest of the answer engine.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(query, top_k=TOP_K):
    """
    Full answer-generation flow: retrieve evidence, check confidence,
    then either generate a grounded answer or escalate.

    Returns a dict (not raw text) so downstream stages — confidence
    scoring, case generation, human escalation — can consume the
    result directly without re-parsing model output.
    """

    evidence = retrieve(query, top_k=top_k)

    if not evidence:
        return {
            "query": query,
            "answer": None,
            "evidence": [],
            "top_similarity": 0.0,
            "escalate": True,
            "reason": "No matching evidence found in the knowledge base."
        }

    top_similarity = evidence[0]["similarity"]

    # Core safety principle: never guess when confidence is low.
    if top_similarity < CONFIDENCE_THRESHOLD:
        return {
            "query": query,
            "answer": None,
            "evidence": evidence,
            "top_similarity": top_similarity,
            "escalate": True,
            "reason": (
                "Retrieval confidence below threshold — "
                "escalating instead of guessing."
            )
        }

    prompt = build_prompt(query, evidence)
    answer_text = call_gemini(prompt)

    return {
        "query": query,
        "answer": answer_text,
        "evidence": evidence,
        "top_similarity": top_similarity,
        "escalate": False,
        "reason": None
    }


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_answer(result):

    print("\n" + "=" * 70)
    print("QUERY")
    print("=" * 70)
    print(result["query"])

    print("\n" + "=" * 70)

    if result["escalate"]:
        print("ESCALATED — NOT ENOUGH CONFIDENCE TO ANSWER")
        print("=" * 70)
        print(f"Reason:         {result['reason']}")
        print(f"Top similarity: {result['top_similarity']}")
        return

    print("ANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\n" + "=" * 70)
    print("EVIDENCE USED")
    print("=" * 70)

    for i, chunk in enumerate(result["evidence"], start=1):
        print(
            f"\n[{i}] {chunk['source']} (Page {chunk['page']}) "
            f"— similarity {chunk['similarity']}"
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    queries = [
        "What support is available to a woman facing violence?",

        "वन स्टॉप सेंटर में कौन सी सेवाएं उपलब्ध हैं?",

        "హింసను ఎదుర్కొంటున్న మహిళకు ఏ సహాయం అందుబాటులో ఉంది?"
    ]

    for query in queries:

        result = generate_answer(query)

        display_answer(result)
