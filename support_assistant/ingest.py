# ============================================================
# ZEPTO SUPPORT ASSISTANT - DOCUMENT INGESTION
# ============================================================

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ------------------------------------------------------------
# PATH CONFIGURATION
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "zepto_policies"


def load_documents():
    """
    Load all Zepto policy documents from the docs directory.
    """

    documents = []

    for file_path in sorted(DOCS_DIR.glob("doc_*.txt")):

        text = file_path.read_text(
            encoding="utf-8-sig"
        ).strip()

        documents.append(
            {
                "id": file_path.stem,
                "text": text
            }
        )

    return documents


def create_vector_database():
    """
    Load policy documents, generate embeddings locally,
    and store them in persistent ChromaDB.
    """

    print("Loading policy documents...")

    documents = load_documents()

    print(
        f"Documents loaded: {len(documents)}"
    )

    # Assignment requires exactly 8 policy documents
    if len(documents) != 8:
        raise ValueError(
            "Expected exactly 8 policy documents "
            f"but found {len(documents)}."
        )

    print(
        f"Loading embedding model: {MODEL_NAME}"
    )

    embedding_model = SentenceTransformer(
        MODEL_NAME
    )

    texts = [
        document["text"]
        for document in documents
    ]

    ids = [
        document["id"]
        for document in documents
    ]

    print("Generating embeddings...")

    embeddings = embedding_model.encode(
        texts,
        normalize_embeddings=True
    )

    print(
        "Embedding shape:",
        embeddings.shape
    )

    # Create persistent ChromaDB database
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Delete previous collection when rerunning ingestion
    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except Exception:
        pass

    # Cosine similarity collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        }
    )

    # Store documents + embeddings
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "source": document["id"]
            }
            for document in documents
        ]
    )

    print(
        "Documents stored in ChromaDB:",
        collection.count()
    )

    print(
        "ChromaDB location:",
        CHROMA_DIR
    )

    return collection


if __name__ == "__main__":

    create_vector_database()

    print(
        "\nIngestion completed successfully."
    )