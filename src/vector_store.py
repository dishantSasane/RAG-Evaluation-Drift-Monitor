import chromadb
from chromadb.utils import embedding_functions
import config

def get_chroma_client():
    """Initializes and returns a persistent database storage client connection."""
    return chromadb.PersistentClient(path=config.CHROMA_DB_PATH)

def get_collection(client):
    """Fetches or constructs an isolated query schema collection inside the database vector path."""
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL_NAME
    )
    return client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )

def seed_database_if_empty(pdf_path: str):
    """Enforces database synchronization, mapping documents if the collection is unitialized."""
    from src.extractor import extract_and_tokenize, group_chunks
    
    client = get_chroma_client()
    collection = get_collection(client)
    
    if collection.count() == 0:
        print(f"Collection is unseeded. Injecting document layers from target path: {pdf_path}...")
        sentences = extract_and_tokenize(pdf_path)
        chunks = group_chunks(sentences, group_size=4, overlap=1)
        
        collection.add(
            documents=chunks,
            ids=[f"id_{i}" for i in range(len(chunks))]
        )
        print(f"Seeding operation complete. Ingested total entries count: {collection.count()}")
    else:
        print(f"Persistent vector space active. Total records validation: {collection.count()}")