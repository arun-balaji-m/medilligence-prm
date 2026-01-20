from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class TableSchema(BaseModel):
    """Schema for table metadata in ChromaDB"""
    table_name: str
    description: str
    columns: List[Dict[str, str]]  # [{name, type, description}]
    jsonb_columns: Optional[List[Dict[str, Any]]] = None  # [{column_name, structure}]
    indexed_columns: List[str] = []
    example_queries: List[str] = []
    database_name: str = "main"
    row_count_estimate: Optional[int] = None


class QueryRequest(BaseModel):
    """User's natural language query"""
    query: str = Field(..., description="Natural language question")


class QueryResponse(BaseModel):
    """Response containing query results"""
    success: bool
    sql_query: Optional[str] = None
    preview_data: Optional[List[Dict[str, Any]]] = None
    total_rows: Optional[int] = None
    columns: Optional[List[str]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tables_used: Optional[List[str]] = None


class TableSearchResult(BaseModel):
    """Result from semantic search"""
    model_config = ConfigDict(protected_namespaces=())

    table_name: str
    relevance_score: float
    schema: str
    source: str  # "semantic" or "llama"