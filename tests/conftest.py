import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def app(db_path):
    return create_app({"TESTING": True, "DATABASE_PATH": db_path})


@pytest.fixture
def client(app):
    return app.test_client()


def add(client, kind, text, reason):
    return client.post("/entries", data={"kind": kind, "text": text, "reason": reason})
