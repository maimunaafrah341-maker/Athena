from sentence_transformers import SentenceTransformer


# ============================================================
# ATHENA — SHARED EMBEDDING MODEL
# ============================================================

MODEL_NAME = "intfloat/multilingual-e5-small"

print("Loading shared multilingual embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Shared embedding model ready.")