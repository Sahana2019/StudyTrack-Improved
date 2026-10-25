import os
from pathlib import Path

TEST_DB = Path(__file__).parent / "test_studytrack.db"

if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["STUDYTRACK_DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

import pytest


@pytest.fixture(scope="session", autouse=True)
def clean_test_database():
    yield

    # Close SQLAlchemy connections before deleting the SQLite file.
    from backend.database import engine

    engine.dispose()

    if TEST_DB.exists():
        TEST_DB.unlink()