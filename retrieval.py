import chromadb

from embedding_model import model


# ============================================================
# CONFIGURATION
# ============================================================

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "athena_knowledge"


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

print(f"Connected to collection: {COLLECTION_NAME}")
print(f"Total knowledge chunks: {collection.count()}")


# ============================================================
# RETRIEVE RELEVANT DOCUMENTS
# ============================================================

def retrieve(query, top_k=5):
    """
    Retrieve the most relevant knowledge chunks for a query.
    """

    # E5 models expect queries to use the "query:" prefix
    query_text = "query: " + query

    query_embedding = model.encode(
        [query_text],
        normalize_embeddings=True
    )

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k
    )

    retrieved_documents = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Chroma is using cosine distance.
        # Convert distance to an approximate similarity score.
        similarity = 1 - distance

        retrieved_documents.append({
            "text": document,
            "source": metadata["source"],
            "page": metadata["page"],
            "chunk": metadata["chunk"],
            "similarity": round(similarity, 4)
        })

    return retrieved_documents


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(query, results):

    print("\n" + "=" * 70)
    print("QUERY")
    print("=" * 70)

    print(query)

    print("\n" + "=" * 70)
    print("RETRIEVED EVIDENCE")
    print("=" * 70)

    for i, result in enumerate(results, start=1):

        print(f"\nRESULT {i}")
        print("-" * 70)

        print(f"Source:     {result['source']}")
        print(f"Page:       {result['page']}")
        print(f"Chunk:      {result['chunk']}")
        print(f"Similarity: {result['similarity']}")

        print("\nText:")
        print(result["text"])


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    queries = [
        "What support is available to a woman facing violence?",

        "हिंसा का सामना करने वाली महिला के लिए कौन सी सहायता उपलब्ध है?",

        "హింసను ఎదుర్కొంటున్న మహిళకు ఏ సహాయం అందుబాటులో ఉంది?"
    ]

    for query in queries:

        results = retrieve(query, top_k=5)

        display_results(query, results)