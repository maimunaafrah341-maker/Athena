import sys
import os
from unittest.mock import MagicMock

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# retrieval.py and google.genai both do real work at import time
# (loading the embedding model, connecting to ChromaDB, creating an
# API client). Fake them out BEFORE importing answer_engine so this
# test can run without a chroma_db, an internet connection, or an
# API key.

fake_retrieval = MagicMock()
sys.modules["retrieval"] = fake_retrieval

fake_genai = MagicMock()
sys.modules["google.genai"] = fake_genai
sys.modules["google"] = MagicMock(genai=fake_genai)

import answer_engine  # noqa: E402


# ============================================================
# TEST HELPERS
# ============================================================

def make_chunk(similarity, source="OSC_Guidelines.pdf", page=3):
    return {
        "text": "Sample evidence text.",
        "source": source,
        "page": page,
        "chunk": 0,
        "similarity": similarity
    }


# ============================================================
# TESTS
# ============================================================

def test_no_evidence_escalates():

    answer_engine.retrieve = MagicMock(return_value=[])

    result = answer_engine.generate_answer("some query")

    assert result["escalate"] is True
    assert result["answer"] is None
    print("PASS: no evidence -> escalate")


def test_low_confidence_escalates_without_calling_model():

    answer_engine.retrieve = MagicMock(
        return_value=[make_chunk(similarity=0.31)]
    )
    answer_engine.call_gemini = MagicMock(
        side_effect=AssertionError("call_gemini should NOT be called")
    )

    result = answer_engine.generate_answer("some query")

    assert result["escalate"] is True
    assert result["answer"] is None
    print("PASS: low similarity -> escalate, model never called")


def test_high_confidence_generates_answer():

    answer_engine.retrieve = MagicMock(
        return_value=[make_chunk(similarity=0.82)]
    )
    answer_engine.call_gemini = MagicMock(
        return_value="Grounded answer text [Source: OSC_Guidelines.pdf, Page: 3]"
    )

    result = answer_engine.generate_answer("some query")

    assert result["escalate"] is False
    assert result["answer"] is not None
    assert "OSC_Guidelines.pdf" in result["answer"]
    print("PASS: high similarity -> answer generated")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    test_no_evidence_escalates()
    test_low_confidence_escalates_without_calling_model()
    test_high_confidence_generates_answer()

    print("\nAll answer_engine logic tests passed.")
