"""
Tests for authorization in the backend API.

These tests ensure that endpoints requiring specific roles (admin, user) properly restrict access
to users without those roles. The backend has the following role-based restrictions:

- GET /users/ : requires admin role
- GET /users/{user_id} : requires admin role
- GET /count : requires admin role
- PATCH /timetable : requires user or admin role for assigning to self

Note: There are no POST endpoints that require specific roles in the current API.
The POST /token and POST /users/ are open for authentication and registration.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.utils.database.db import UserDB
from app.utils.auth.password import get_password_hash
from app.config import get_settings

TEST_ROLES = ["read-only-user", "user", "admin", "guest"]

def create_test_user(session: Session, email: str, password: str, role: str = "read-only-user") -> UserDB:
    hashed_password = get_password_hash(password)
    user = UserDB(
        email=email,
        first_name="Test",
        second_name="User",
        colour="BLUE",
        hashed_password=hashed_password,
        role=role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login_user(client: TestClient, email: str, password: str):
    response = client.post("/token", data={"username": email, "password": password})
    return response


@pytest.mark.parametrize("role", TEST_ROLES)
def test_get_users_requires_admin(client: TestClient, session: Session, role: str):
    # Create a user with the given role
    user = create_test_user(session, f"{role}@example.com", "password123", role)

    # Login as that user
    login_response = login_user(client, user.email, "password123")
    assert login_response.status_code == 200

    # Try to get users
    response = client.get("/users/")
    if role == "admin":
        assert response.status_code == 200
    else:
        assert response.status_code == 403  # Forbidden


@pytest.mark.parametrize("role", TEST_ROLES)
def test_get_user_by_id_requires_admin(client: TestClient, session: Session, role: str):
    # Create a user with the given role
    user = create_test_user(session, f"{role}@example.com", "password123", role)

    # Create another user to fetch
    other_user = create_test_user(session, "other@example.com", "password123", "read-only-user")

    # Login as the first user
    login_response = login_user(client, user.email, "password123")
    assert login_response.status_code == 200

    # Try to get the other user
    response = client.get(f"/users/{other_user.id}")
    if role == "admin":
        assert response.status_code == 200
    else:
        assert response.status_code == 403  # Forbidden


@pytest.mark.parametrize("role", TEST_ROLES)
def test_get_count_requires_admin(client: TestClient, session: Session, role: str):
    # Create a user with the given role
    user = create_test_user(session, f"{role}@example.com", "password123", role)

    # Login as that user
    login_response = login_user(client, user.email, "password123")
    assert login_response.status_code == 200

    # Try to get count
    response = client.get("/count")
    if role == "admin":
        assert response.status_code == 200
    else:
        assert response.status_code == 403  # Forbidden


@pytest.mark.parametrize("role", TEST_ROLES)
def test_update_timetable_requires_user_or_admin(client: TestClient, session: Session, role: str):
    # Create a user with the given role
    user = create_test_user(session, f"{role}@example.com", "password123", role)

    # Login as that user
    login_response = login_user(client, user.email, "password123")
    assert login_response.status_code == 200

    # Get a valid dayID from the timetable
    from app.utils.database.db import Timetable
    from sqlmodel import select
    timetable_entry = session.exec(select(Timetable).limit(1)).first()
    assert timetable_entry is not None
    day_id = timetable_entry.id

    # Try to update timetable (assign to self)
    from datetime import date
    response = client.patch("/timetable", json={
        "dayID": day_id,
        "assign_to_self": True,
        "week": str(date.today())
    })
    if role in ["user", "admin"]:
        # Should succeed or fail based on other conditions, but not 401/403 for role
        assert response.status_code in [200, 404, 400]  # 404 if week mismatch, etc.
    else:
        assert response.status_code == 401  # Unauthorized due to role


def test_unauthenticated_cannot_access_protected_endpoints(client: TestClient):
    # Without login, try protected endpoints
    endpoints = ["/users/", "/users/1", "/count", "/timetable"]
    for endpoint in endpoints:
        if endpoint == "/timetable":
            response = client.patch(endpoint, json={"dayID": 1, "assign_to_self": True, "week": "2023-01-01"})
        else:
            response = client.get(endpoint)
        assert response.status_code == 401  # Unauthorized


def test_logout_clears_cookie(client: TestClient, session: Session):
    """Test that logout endpoint clears the access_token cookie."""
    # Create and login a user
    user = create_test_user(session, "test@example.com", "password123", "user")
    login_response = login_user(client, user.email, "password123")
    assert login_response.status_code == 200
    
    # Verify cookie is set after login
    assert "access_token" in client.cookies
    original_cookie = client.cookies.get("access_token")
    assert original_cookie is not None
    
    # Call logout endpoint
    logout_response = client.post("/logout")
    assert logout_response.status_code == 200
    assert logout_response.json() == {'message': 'logged out'}
    
    # Verify cookie is cleared (should be deleted or empty)
    # After logout, the cookie should be deleted from the client
    assert "access_token" not in client.cookies or client.cookies.get("access_token") == ""


def test_protected_route_blocked_after_logout(client: TestClient, session: Session):
    """Test that protected routes are blocked after logout."""
    # Create and login a user
    user = create_test_user(session, "test@example.com", "password123", "admin")
    login_response = login_user(client, user.email, "password123")
    assert login_response.status_code == 200
    
    # Verify protected endpoint works when logged in
    users_response = client.get("/users/")
    assert users_response.status_code == 200
    
    # Call logout endpoint
    logout_response = client.post("/logout")
    assert logout_response.status_code == 200
    
    # Verify protected endpoint is blocked after logout
    protected_response = client.get("/users/")
    assert protected_response.status_code == 401  # Unauthorized


def test_logout_post_only_enforcement(client: TestClient, session: Session):
    """Test that logout endpoint only accepts POST requests."""
    # Create and login a user
    user = create_test_user(session, "test@example.com", "password123", "user")
    login_response = login_user(client, user.email, "password123")
    assert login_response.status_code == 200
    
    # Test GET request to /logout (should fail or return 405)
    get_response = client.get("/logout")
    assert get_response.status_code == 405  # Method Not Allowed
    
    # Test PUT request to /logout (should fail or return 405)
    put_response = client.put("/logout")
    assert put_response.status_code == 405  # Method Not Allowed
    
    # Test DELETE request to /logout (should fail or return 405)
    delete_response = client.delete("/logout")
    assert delete_response.status_code == 405  # Method Not Allowed
    
    # Test that POST still works
    post_response = client.post("/logout")
    assert post_response.status_code == 200