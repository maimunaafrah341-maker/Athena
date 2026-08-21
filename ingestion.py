import os
import re

import chromadb
from pypdf import PdfReader

from embedding_model import model
from understanding import detect_language


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_DIR = "data/sources"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "athena_knowledge"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """Clean extracted PDF text."""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# CHUNKING
# ============================================================

def create_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks."""

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ============================================================
# PROCESS ONE PDF
# ============================================================

def process_pdf(pdf_path):
    """Extract text from every page of a PDF."""

    reader = PdfReader(pdf_path)

    all_chunks = []

    filename = os.path.basename(pdf_path)

    print(f"\nProcessing: {filename}")
    print(f"Pages: {len(reader.pages)}")

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if not text:
            continue

        text = clean_text(text)

        if not text:
            continue

        page_chunks = create_chunks(text)

        for chunk_number, chunk in enumerate(page_chunks):

            all_chunks.append({
                "text": chunk,
                "source": filename,
                "page": page_number,
                "chunk": chunk_number,
                "language": detect_language(chunk)
            })

    print(f"Chunks created: {len(all_chunks)}")

    return all_chunks


# ============================================================
# LOAD ALL PDFs
# ============================================================

def load_all_documents():

    documents = []

    for filename in os.listdir(SOURCE_DIR):

        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(SOURCE_DIR, filename)

        pdf_chunks = process_pdf(pdf_path)

        documents.extend(pdf_chunks)

    return documents


# ============================================================
# STORE IN CHROMADB
# ============================================================

def store_in_chroma(documents):

    print("\nConnecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=CHROMA_DIR
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        }
    )

    print("Creating embeddings...")

    texts = [
        "passage: " + document["text"]
        for document in documents
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    ids = []
    metadata = []
    raw_documents = []

    for index, document in enumerate(documents):

        ids.append(
            f"{document['source']}_"
            f"page_{document['page']}_"
            f"chunk_{document['chunk']}"
        )

        metadata.append({
           "source": document["source"],
           "page": document["page"],
           "chunk": document["chunk"],
           "language": document["language"]
        })

        raw_documents.append(document["text"])

    collection.upsert(
        ids=ids,
        documents=raw_documents,
        embeddings=embeddings.tolist(),
        metadatas=metadata
    )

    print("\nSuccessfully stored documents in ChromaDB.")

    print(f"Total chunks stored: {collection.count()}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ATHENA KNOWLEDGE INGESTION")
    print("=" * 60)

    documents = load_all_documents()

    if not documents:
        print("\nNo PDF documents found.")
        print(f"Check: {SOURCE_DIR}")
        exit()

    print("\n" + "=" * 60)
    print(f"TOTAL CHUNKS: {len(documents)}")
    print("=" * 60)

    store_in_chroma(documents)

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)