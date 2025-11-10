"""
SQLite Database utilities for CrossIt backend
"""
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import os

# Database path - shared volume with frontend
DB_PATH = Path(__file__).parent.parent.parent / "crossit.db"

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialize database with schema"""
    # Try to find schema file in multiple locations
    possible_paths = [
        Path(__file__).parent.parent.parent / "schema.sql",  # backend/schema.sql
        Path("/app/schema.sql"),  # Docker root
    ]
    
    schema_path = None
    for path in possible_paths:
        if path.exists():
            schema_path = path
            break
    
    if not schema_path:
        raise FileNotFoundError(f"Schema file not found in any of: {possible_paths}")
    
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    with get_db() as conn:
        conn.executescript(schema)
    
    print("✅ Database initialized successfully")

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return results as list of dicts"""
    with get_db() as conn:
        cursor = conn.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
    with get_db() as conn:
        cursor = conn.execute(query, params)
        return cursor.rowcount

if __name__ == "__main__":
    init_database()

