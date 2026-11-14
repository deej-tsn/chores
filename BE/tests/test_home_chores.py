"""Tests for the fortnightly home-chores slice.

Covers the period maths (which is easy to get subtly wrong), lazy/idempotent
seeding, the claim/unclaim contract, group claims, and the role matrix.
"""

import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.utils.auth.password import get_password_hash
from app.utils.database.db import (
    FORTNIGHT_ANCHOR,
    HomeChore,
    HomeChoreAssignment,
    UserDB,
    add_period_assignments,
    get_fortnight_start,
)

TEST_ROLES = ["read-only-user", "user", "admin", "guest"]


def create_user(
    session: Session,
    email: str,
    password: str = "password123",
    role: str = "user",
    first_name: str = "Test",
) -> UserDB:
    user = UserDB(
        email=email,
        first_name=first_name,
        second_name="User",
        colour="BLUE",
        hashed_password=get_password_hash(password),
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login(client: TestClient, email: str, password: str = "password123"):
    return client.post("/token", data={"username": email, "password": password})


def first_assignment(client: TestClient) -> dict:
    """GET the current period and return its first chore entry."""
    response = client.get("/chores/home")
    assert response.status_code == 200
    return response.json()["chores"][0]


def chore_by_id(payload: dict, assignment_id: int) -> dict:
    return next(chore for chore in payload["chores"] if chore["id"] == assignment_id)


# ─────────────────────────────────────────────
#               PERIOD MATHS
# ─────────────────────────────────────────────

@pytest.mark.parametrize(
    "offset_days, expected_offset",
    [
        (0, 0),      # the anchor itself
        (1, 0),      # Tuesday of the anchor fortnight
        (7, 0),      # second week — must NOT start a new period
        (13, 0),     # last day of the anchor fortnight
        (14, 14),    # first day of the next period
        (27, 14),    # last day of the next period
        (-1, -14),   # floor division must handle pre-anchor dates
        (-14, -14),
    ],
)
def test_get_fortnight_start(offset_days: int, expected_offset: int):
    day = FORTNIGHT_ANCHOR + datetime.timedelta(days=offset_days)
    assert get_fortnight_start(day) == FORTNIGHT_ANCHOR + datetime.timedelta(days=expected_offset)


def test_get_fortnight_start_defaults_to_today():
    assert get_fortnight_start() == get_fortnight_start(datetime.date.today())


# ─────────────────────────────────────────────
#               READ / SEEDING
# ─────────────────────────────────────────────

def test_read_is_public(client: TestClient):
    response = client.get("/chores/home")

    assert response.status_code == 200
    payload = response.json()
    assert payload["periodStart"] == get_fortnight_start().isoformat()
    assert {chore["chore"] for chore in payload["chores"]} == {
        "Clean the house",
        "Grocery shopping",
    }
    # Anonymous callers can read, but never own anything.
    assert all(chore["claimed_by"] == [] for chore in payload["chores"])


def test_week_inside_fortnight_normalises_to_same_period(client: TestClient):
    current = get_fortnight_start()
    off_week = current + datetime.timedelta(days=7)

    response = client.get(f"/chores/home?period={off_week.isoformat()}")

    assert response.status_code == 200
    assert response.json()["periodStart"] == current.isoformat()


def test_add_period_assignments_is_idempotent(session: Session):
    period = get_fortnight_start()

    add_period_assignments(session, period)
    add_period_assignments(session, period)

    assignments = session.exec(
        select(HomeChoreAssignment).where(HomeChoreAssignment.period_start == period)
    ).all()
    assert len(assignments) == 2


def test_new_catalogue_chore_backfills_existing_period(session: Session, client: TestClient):
    session.add(HomeChore(name="Water the plants", description="Every plant, once."))
    session.commit()

    add_period_assignments(session, get_fortnight_start())

    chores = client.get("/chores/home").json()["chores"]
    assert "Water the plants" in {chore["chore"] for chore in chores}


# ─────────────────────────────────────────────
#                   CLAIMS
# ─────────────────────────────────────────────

def test_claim_and_unclaim_are_idempotent(client: TestClient, session: Session):
    create_user(session, "claimer@example.com", first_name="Alice")
    assert login(client, "claimer@example.com").status_code == 200

    assignment = first_assignment(client)
    body = {
        "assignmentID": assignment["id"],
        "period": get_fortnight_start().isoformat(),
    }

    first = client.patch("/chores/home", json={**body, "claimed": True})
    assert first.status_code == 200
    assert chore_by_id(first.json(), assignment["id"])["claimed_by"] == ["Alice"]
    assert chore_by_id(first.json(), assignment["id"])["claimed_by_me"] is True

    # Claiming twice must not duplicate anything.
    second = client.patch("/chores/home", json={**body, "claimed": True})
    assert chore_by_id(second.json(), assignment["id"])["claimed_by"] == ["Alice"]

    left = client.patch("/chores/home", json={**body, "claimed": False})
    assert chore_by_id(left.json(), assignment["id"])["claimed_by"] == []
    assert chore_by_id(left.json(), assignment["id"])["claimed_by_me"] is False

    # Leaving twice is also a no-op.
    again = client.patch("/chores/home", json={**body, "claimed": False})
    assert again.status_code == 200
    assert chore_by_id(again.json(), assignment["id"])["claimed_by"] == []


def test_two_people_can_share_one_chore(client: TestClient, session: Session):
    create_user(session, "alice@example.com", first_name="Alice")
    create_user(session, "bob@example.com", first_name="Bob")

    assert login(client, "alice@example.com").status_code == 200
    assignment = first_assignment(client)
    body = {
        "assignmentID": assignment["id"],
        "claimed": True,
        "period": get_fortnight_start().isoformat(),
    }
    client.patch("/chores/home", json=body)

    assert login(client, "bob@example.com").status_code == 200
    shared = client.patch("/chores/home", json=body).json()

    assert chore_by_id(shared, assignment["id"])["claimed_by"] == ["Alice", "Bob"]


def test_leaving_does_not_remove_other_claims(client: TestClient, session: Session):
    create_user(session, "alice@example.com", first_name="Alice")
    create_user(session, "bob@example.com", first_name="Bob")

    assert login(client, "alice@example.com").status_code == 200
    assignment = first_assignment(client)
    period = get_fortnight_start().isoformat()
    client.patch(
        "/chores/home",
        json={"assignmentID": assignment["id"], "claimed": True, "period": period},
    )

    assert login(client, "bob@example.com").status_code == 200
    client.patch(
        "/chores/home",
        json={"assignmentID": assignment["id"], "claimed": True, "period": period},
    )
    bob_leaves = client.patch(
        "/chores/home",
        json={"assignmentID": assignment["id"], "claimed": False, "period": period},
    ).json()

    assert chore_by_id(bob_leaves, assignment["id"])["claimed_by"] == ["Alice"]


# ─────────────────────────────────────────────
#                AUTHORIZATION
# ─────────────────────────────────────────────

@pytest.mark.parametrize("role", TEST_ROLES)
def test_update_home_chore_role_matrix(client: TestClient, session: Session, role: str):
    create_user(session, f"{role}@example.com", role=role)
    assert login(client, f"{role}@example.com").status_code == 200

    assignment = first_assignment(client)
    response = client.patch(
        "/chores/home",
        json={
            "assignmentID": assignment["id"],
            "claimed": True,
            "period": get_fortnight_start().isoformat(),
        },
    )

    if role in ["user", "admin"]:
        assert response.status_code == 200
    else:
        assert response.status_code == 401  # matches PATCH /chores/dog-walking's convention


def test_unauthenticated_cannot_claim(client: TestClient):
    assignment = first_assignment(client)

    response = client.patch(
        "/chores/home",
        json={
            "assignmentID": assignment["id"],
            "claimed": True,
            "period": get_fortnight_start().isoformat(),
        },
    )

    assert response.status_code == 401


def test_unknown_assignment_returns_404(client: TestClient, session: Session):
    create_user(session, "claimer@example.com")
    assert login(client, "claimer@example.com").status_code == 200

    response = client.patch(
        "/chores/home",
        json={
            "assignmentID": 999_999,
            "claimed": True,
            "period": get_fortnight_start().isoformat(),
        },
    )

    assert response.status_code == 404
