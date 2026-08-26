# Works for either Hugging Face Spaces (Docker SDK, free CPU tier
# ~16GB RAM) or Google Cloud Run (configurable memory, generous free
# tier) -- both are candidates for tonight, chosen by whichever
# teammate gets there first, so this shouldn't need editing either way.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rebuilds the vector DB from the tracked source PDFs at image-build
# time, same reason as render.yaml's buildCommand -- chroma_db/ is
# gitignored, so nothing here has it until this runs.
RUN python ingestion.py

# Shell form (not exec-array form) so $PORT actually expands: Cloud
# Run injects PORT itself (normally 8080) and requires listening on
# it; HF Spaces doesn't set PORT at all, so it falls back to 7860,
# Spaces' expected default. Same image, either platform, no edits.
EXPOSE 7860
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}
