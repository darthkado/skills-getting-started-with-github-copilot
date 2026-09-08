from urllib.parse import quote

from src import app as app_module


class TestRoot:
    def test_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivities:
    def test_lists_available_activities(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert expected_activity in activities
        assert activities[expected_activity]["description"]
        assert activities[expected_activity]["schedule"]
        assert activities[expected_activity]["max_participants"] == 12
        assert isinstance(activities[expected_activity]["participants"], list)


class TestSignup:
    def test_registers_new_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in app_module.activities[activity_name]["participants"]

    def test_rejects_duplicate_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Student is already signed up for this activity"
        }

    def test_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_requires_email(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{quote(activity_name)}/signup")

        # Assert
        assert response.status_code == 422


class TestUnregister:
    def test_removes_existing_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in app_module.activities[activity_name]["participants"]

    def test_rejects_missing_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "missing.student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Student is not signed up for this activity"
        }

    def test_rejects_unknown_activity(self, client):
        # Arrange
        activity_name = "Unknown Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_requires_email(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.delete(f"/activities/{quote(activity_name)}/signup")

        # Assert
        assert response.status_code == 422
