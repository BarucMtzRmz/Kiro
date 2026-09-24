import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = Path(os.getenv("KIRO_DATA_DIR", BASE_DIR / "data" / "documents")).expanduser().resolve()
INDEX_DIR = Path(os.getenv("KIRO_INDEX_DIR", BASE_DIR / "data" / "index")).expanduser().resolve()
COLLECTION_NAME = os.getenv("KIRO_COLLECTION", "documents")

EMBEDDING_MODEL = os.getenv("KIRO_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

CHUNK_SIZE = int(os.getenv("KIRO_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("KIRO_CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("KIRO_TOP_K", "4"))

# "ollama" (fully local) or "openai" (any OpenAI-compatible API)
LLM_PROVIDER = os.getenv("KIRO_LLM_PROVIDER", "ollama").lower()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

DATA_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)
