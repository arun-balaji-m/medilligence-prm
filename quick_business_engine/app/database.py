from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from quick_business_engine.app.config import get_settings
import os

# Disable ChromaDB telemetry completely
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

settings = get_settings()

# PostgreSQL Connection
engine = create_engine(
    settings.QUBE_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_db():
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure ChromaDB directory exists
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

# ChromaDB Client (Persistent) - Disable telemetry
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIRECTORY,
    settings=ChromaSettings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# Get or create collection
registry_collection = chroma_client.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME,
    metadata={"description": "Database table schemas and metadata"}
)

# Embedding Model (Local)
embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

def execute_query(query: str, fetch_all: bool = False):
    """
    Execute a SQL query safely
    """
    with get_db() as db:
        result = db.execute(text(query))
        if fetch_all:
            return result.fetchall()
        else:
            return result.fetchmany(settings.MAX_ROWS_PREVIEW)