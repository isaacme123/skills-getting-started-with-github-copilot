import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dictionary before each test.

    Arrange-Act-Assert tests mutate `activities`, so this fixture saves a deep
    copy at the start and restores it after the test finishes.
    """
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities_returns_all():
    # Arrange: nothing to set up beyond the fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success_and_duplicate():
    # Arrange
    email = "new@mergington.edu"
    activity = "Chess Club"

    # Act - first signup
    resp1 = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )
    # Assert success
    assert resp1.status_code == 200
    assert "Signed up" in resp1.json()["message"]

    # Act - duplicate signup
    resp2 = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )
    # Assert duplicate error
    assert resp2.status_code == 400
    assert (
        resp2.json()["detail"] == "Student is already signed up for this activity"
    )


def test_signup_activity_not_found():
    # Act
    resp = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})

    # Assert
    assert resp.status_code == 404


def test_unregister_success_and_errors():
    # Arrange: add a participant so we can remove them
    email = "tester@mergington.edu"
    activity = "Chess Club"
    activities[activity]["participants"].append(email)

    # Act - remove
    resp = client.delete(
        f"/activities/{activity}/unregister", params={"email": email}
    )
    # Assert success
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # Act - try again (should fail)
    resp2 = client.delete(
        f"/activities/{activity}/unregister", params={"email": email}
    )
    # Assert error detail
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_activity_not_found():
    # Act
    resp = client.delete("/activities/Nope/unregister", params={"email": "a@b.com"})

    # Assert
    assert resp.status_code == 404
