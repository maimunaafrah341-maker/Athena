# For Hugging Face Spaces (Docker SDK) -- Spaces' free CPU tier gives
# ~16GB RAM, well clear of the 512MB ceiling that Render's free tier
# hit twice tonight. Spaces' proxy expects the app on port 7860 by
# default, hence that specific port below (not $PORT -- that's a
# Render/Heroku convention, not HF's).
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rebuilds the vector DB from the tracked source PDFs at image-build
# time, same reason as render.yaml's buildCommand -- chroma_db/ is
# gitignored, so nothing here has it until this runs.
RUN python ingestion.py

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
