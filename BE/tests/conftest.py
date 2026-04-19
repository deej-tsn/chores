import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import date, timedelta

from app.main import app
from app.utils.database.db import get_session, Timetable, TimeSlot
from app.config import get_settings


@pytest.fixture(name="session")
def session_fixture():
    # Create an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Create some timetable data
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        for i in range(7):
            for time_slot in [TimeSlot.Morning, TimeSlot.Evening]:
                timetable_entry = Timetable(
                    day=monday + timedelta(days=i),
                    time=time_slot,
                    assigned=None
                )
                session.add(timetable_entry)
        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, base_url="https://testserver")
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def settings():
    return get_settings()