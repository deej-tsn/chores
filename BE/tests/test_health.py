"""
Tests for the /healthz readiness probe.

The probe is consumed by the Docker healthcheck and by scripts/release.sh, so it must:
- return 200 with a stable body when the app and database are fine
- need no authentication (a probe has no cookie)
- report 503, not 200, when the database is unreachable
"""

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.utils.database.db import get_session


def test_healthz_returns_ok(client: TestClient):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthz_needs_no_authentication(client: TestClient):
    # A fresh client carries no access_token cookie and no bearer token.
    response = TestClient(app, base_url="https://testserver").get("/healthz")

    assert response.status_code == 200


def test_healthz_returns_503_when_database_is_unavailable():
    """A broken database must not report healthy, or a bad release slips through unnoticed."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with patch.object(Session, "exec", side_effect=RuntimeError("db gone")):
            response = TestClient(app, base_url="https://testserver").get("/healthz")
    finally:
        app.dependency_overrides.pop(get_session, None)
        session.close()

    assert response.status_code == 503
    assert response.json()["detail"] == "database unavailable"
