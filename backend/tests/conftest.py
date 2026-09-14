import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.db.firebase import get_db

app = create_app()

class MockFirestoreClient:
    def collection(self, name):
        return MockCollection(name)
        
class MockCollection:
    def __init__(self, name):
        self.name = name
    def document(self, id=None):
        return MockDocument(id)

class MockDocument:
    def __init__(self, id):
        self.id = id
    def get(self):
        return self
    @property
    def exists(self):
        return False
    def to_dict(self):
        return {}
    def set(self, data):
        pass

@pytest.fixture(scope="function")
def db():
    yield MockFirestoreClient()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)
