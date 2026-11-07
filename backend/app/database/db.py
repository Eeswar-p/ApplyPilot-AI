from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

Base = declarative_base()
engine = None
SessionLocal = None

def init_db(database_uri: str):
    """Initialize database engine and session factory."""
    global engine, SessionLocal
    connect_args = {}
    if database_uri.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        
    engine = create_engine(database_uri, connect_args=connect_args)
    SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return engine, SessionLocal

def get_engine():
    """Get active engine."""
    return engine

def create_all_tables():
    """Create all tables in the database if they do not exist."""
    if engine is not None:
        Base.metadata.create_all(bind=engine)

def drop_all_tables():
    """Drop all tables in the database."""
    if engine is not None:
        Base.metadata.drop_all(bind=engine)

def get_db_session():
    """Get active scoped db session."""
    if SessionLocal is None:
        raise RuntimeError("Database is not initialized. Call init_db() first.")
    return SessionLocal()

@contextmanager
def get_db_context():
    """Provide a database session context for background workers."""
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()
        SessionLocal.remove()
