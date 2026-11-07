import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from app import create_app
from app.database.db import get_db_session, create_all_tables, drop_all_tables

@pytest.fixture(scope="session")
def app():
    test_app = create_app("testing")
    with test_app.app_context():
        create_all_tables()
        yield test_app
        drop_all_tables()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        session = get_db_session()
        yield session
        session.rollback()
