# ============================================================
# ZEPTO SUPPORT ASSISTANT - CHROMADB RETRIEVAL
# ============================================================

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "zepto_policies"


# ------------------------------------------------------------
# LOAD EMBEDDING MODEL ONCE
# ------------------------------------------------------------

embedding_model = SentenceTransformer(MODEL_NAME)


def get_collection():
    """
    Get a fresh reference to the ChromaDB collection.

    We intentionally do not keep the collection as a global
    object because ingestion may recreate the collection.
    """

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    return client.get_collection(
        name=COLLECTION_NAME
    )


def retrieve_documents(query, top_k=3):
    """
    Retrieve the top-k most similar Zepto policy documents
    using cosine similarity.
    """

    # Get current collection instead of using an old/stale
    # collection reference.
    collection = get_collection()

    # Generate embedding for the customer query.
    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    # Perform real top-k vector retrieval.
    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_documents = []

    for i in range(
        len(results["ids"][0])
    ):

        document_id = (
            results["ids"][0][i]
        )

        document_text = (
            results["documents"][0][i]
        )

        distance = (
            results["distances"][0][i]
        )

        # ChromaDB collection uses cosine distance.
        # cosine similarity = 1 - cosine distance
        similarity = 1 - float(distance)

        retrieved_documents.append(
            {
                "id": document_id,
                "text": document_text,
                "distance": float(distance),
                "similarity": float(similarity)
            }
        )

    return retrieved_documents


# ------------------------------------------------------------
# MANUAL RETRIEVAL TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    test_query = "What is the delivery fee?"

    print("\nQuery:")
    print(test_query)

    print("\nTop 3 retrieved documents:\n")

    results = retrieve_documents(
        test_query,
        top_k=3
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        print("=" * 70)

        print(
            f"Rank: {rank}"
        )

        print(
            f"Document ID: {result['id']}"
        )

        print(
            f"Similarity: {result['similarity']:.4f}"
        )

        print(
            f"Text: {result['text'][:250]}..."
        )

        print()