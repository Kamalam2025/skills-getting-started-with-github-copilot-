import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities database before each test to ensure isolation."""
    # Arrange: Save original state
    original = copy.deepcopy(activities)
    yield
    # Teardown: Restore original state
    activities.clear()
    activities.update(original)

# Test GET /activities
def test_get_activities():
    # Arrange: No special setup needed
    # Act: Make GET request
    response = client.get("/activities")
    # Assert: Check status and content
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]

# Test POST /activities/{activity_name}/signup - Success
def test_signup_success():
    # Arrange: Choose an activity and new email
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act: Make POST request
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert: Check success response
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # Assert: Verify participant was added
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]

# Test POST /activities/{activity_name}/signup - Activity not found
def test_signup_activity_not_found():
    # Arrange: Use non-existent activity
    activity = "Nonexistent Activity"
    email = "test@mergington.edu"
    # Act: Make POST request
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert: Check 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# Test POST /activities/{activity_name}/signup - Already signed up
def test_signup_already_signed_up():
    # Arrange: Use an email already in the activity
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    # Act: Make POST request
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert: Check 400 error
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

# Test DELETE /activities/{activity_name}/signup - Success
def test_unregister_success():
    # Arrange: Choose an activity and existing participant
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert: Check success response
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    # Assert: Verify participant was removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]

# Test DELETE /activities/{activity_name}/signup - Activity not found
def test_unregister_activity_not_found():
    # Arrange: Use non-existent activity
    activity = "Nonexistent Activity"
    email = "test@mergington.edu"
    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert: Check 404 error
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# Test DELETE /activities/{activity_name}/signup - Not signed up
def test_unregister_not_signed_up():
    # Arrange: Use an email not in the activity
    activity = "Chess Club"
    email = "notsignedup@mergington.edu"
    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    # Assert: Check 400 error
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]

# Test GET / (root redirect)
def test_root_redirect():
    # Arrange: No special setup
    # Act: Make GET request to root
    response = client.get("/")
    # Assert: Check redirect to static file
    assert response.status_code == 200  # FastAPI handles redirect internally in test client
    # Note: In a real browser, this would redirect; TestClient follows redirects by default