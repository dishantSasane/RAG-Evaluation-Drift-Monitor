import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "poolside/laguna-xs-2.1:free"
JUDGE_MODEL = "cohere/north-mini-code:free"
EVAL_TEMP = 0.0
DRIFT_ALERT_THRESHOLD = 0.10

LEDGER_FILE_PATH = "score_history.json"

# ChromaDB Configurations
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "hdfc_terms_collection"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Security Boundary Gate Check
if not OPENROUTER_API_KEY:
    print("Critical System Boot Error: 'OPENROUTER_API_KEY' environment variable is missing.")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}