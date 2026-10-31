from contextlib import contextmanager
from app.config import settings


@contextmanager
def get_db_connection():
    import psycopg2
    from psycopg2.extras import RealDictCursor

    conn = psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()
