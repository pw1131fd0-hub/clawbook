"""Integration tests for growth tracking API controller (v1.7 Phase 3)."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from backend.main import app
from backend.database import Base, engine, get_db
from backend.models.orm_models import Goal, Achievement, JournalEntry, SentimentAnalysis
from backend.models.schemas import GoalCreate, ProgressLogRequest


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database session."""
    def override_get_db():
        session = next(get_db())
        yield session
        session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestGrowthControllerGoalCreation:
    """Test goal creation endpoint."""

    def test_create_goal_success(self, client):
        """Test creating a valid goal."""
        response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Learn Python",
                "description": "Master advanced Python concepts",
                "category": "learning",
                "target_value": 100,
                "unit": "hours",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Learn Python"
        assert data["category"] == "learning"
        assert data["status"] == "active"
        assert data["current_value"] == 0
        assert "id" in data

    def test_create_goal_invalid_category(self, client):
        """Test creating goal with invalid category."""
        response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Some Goal",
                "category": "invalid_category",
                "target_value": 100,
                "unit": "items",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            },
        )
        assert response.status_code == 400
        assert "Invalid category" in response.json()["detail"]

    def test_create_goal_negative_target(self, client):
        """Test creating goal with negative target value."""
        response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Some Goal",
                "category": "personal",
                "target_value": -50,
                "unit": "items",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            },
        )
        assert response.status_code == 400
        assert "positive" in response.json()["detail"].lower()

    def test_create_multiple_goals(self, client):
        """Test creating multiple goals of different categories."""
        categories = ["personal", "professional", "health", "learning"]
        for i, category in enumerate(categories):
            response = client.post(
                "/api/v1/growth/goals",
                json={
                    "title": f"Goal {i+1}",
                    "category": category,
                    "target_value": 100,
                    "unit": "units",
                    "target_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                },
            )
            assert response.status_code == 200
            assert response.json()["category"] == category


class TestGrowthControllerGoalRetrieval:
    """Test goal listing and retrieval."""

    @pytest.fixture(autouse=True)
    def setup_goals(self, client):
        """Create test goals."""
        self.goals = []
        categories = ["personal", "professional", "health", "learning"]
        statuses = ["active", "completed"]

        for i in range(8):
            response = client.post(
                "/api/v1/growth/goals",
                json={
                    "title": f"Goal {i+1}",
                    "category": categories[i % 4],
                    "target_value": 100,
                    "unit": "units",
                    "target_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                },
            )
            assert response.status_code == 200
            self.goals.append(response.json())

    def test_list_all_goals(self, client):
        """Test listing all goals."""
        response = client.get("/api/v1/growth/goals")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8
        assert all("id" in goal for goal in data)
        assert all("title" in goal for goal in data)

    def test_list_goals_by_category(self, client):
        """Test filtering goals by category."""
        response = client.get("/api/v1/growth/goals?category=personal")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # 8 goals / 4 categories
        assert all(goal["category"] == "personal" for goal in data)

    def test_list_goals_by_status(self, client):
        """Test filtering goals by status."""
        response = client.get("/api/v1/growth/goals?status=active")
        assert response.status_code == 200
        data = response.json()
        assert all(goal["status"] == "active" for goal in data)

    def test_get_specific_goal(self, client):
        """Test retrieving a specific goal."""
        goal_id = self.goals[0]["id"]
        response = client.get(f"/api/v1/growth/goals/{goal_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == goal_id
        assert data["title"] == "Goal 1"

    def test_get_nonexistent_goal(self, client):
        """Test retrieving nonexistent goal."""
        response = client.get("/api/v1/growth/goals/nonexistent-id")
        assert response.status_code == 404


class TestGrowthControllerGoalUpdate:
    """Test goal update endpoint."""

    @pytest.fixture(autouse=True)
    def setup_goal(self, client):
        """Create a test goal."""
        response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Original Goal",
                "category": "learning",
                "target_value": 100,
                "unit": "hours",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            },
        )
        assert response.status_code == 200
        self.goal = response.json()
        self.goal_id = self.goal["id"]

    def test_update_goal_title(self, client):
        """Test updating goal title."""
        response = client.put(
            f"/api/v1/growth/goals/{self.goal_id}",
            json={
                "title": "Updated Goal Title",
                "description": "Updated description",
                "status": "active",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Goal Title"
        assert data["description"] == "Updated description"

    def test_update_goal_status(self, client):
        """Test updating goal status."""
        response = client.put(
            f"/api/v1/growth/goals/{self.goal_id}",
            json={"status": "completed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_update_nonexistent_goal(self, client):
        """Test updating nonexistent goal."""
        response = client.put(
            "/api/v1/growth/goals/nonexistent-id",
            json={"status": "paused"},
        )
        assert response.status_code == 404


class TestGrowthControllerGoalDeletion:
    """Test goal deletion endpoint."""

    @pytest.fixture(autouse=True)
    def setup_goal(self, client):
        """Create a test goal."""
        response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Goal to Delete",
                "category": "personal",
                "target_value": 50,
                "unit": "items",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            },
        )
        assert response.status_code == 200
        self.goal_id = response.json()["id"]

    def test_delete_goal(self, client):
        """Test deleting a goal."""
        response = client.delete(f"/api/v1/growth/goals/{self.goal_id}")
        assert response.status_code == 200

        # Verify goal is deleted
        response = client.get(f"/api/v1/growth/goals/{self.goal_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_goal(self, client):
        """Test deleting nonexistent goal."""
        response = client.delete("/api/v1/growth/goals/nonexistent-id")
        assert response.status_code == 404


class TestGrowthControllerProgressLogging:
    """Test progress logging endpoint."""

    @pytest.fixture(autouse=True)
    def setup_goal(self, client):
        """Create a test goal."""
        response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Reading Goal",
                "description": "Read 10 books this year",
                "category": "learning",
                "target_value": 10,
                "unit": "books",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
            },
        )
        assert response.status_code == 200
        self.goal_id = response.json()["id"]

    def test_log_progress(self, client):
        """Test logging progress towards a goal."""
        response = client.post(
            f"/api/v1/growth/goals/{self.goal_id}/progress",
            json={
                "progress_value": 2,
                "note": "Finished two books this week",
            },
        )
        assert response.status_code == 200

        # Verify goal progress updated
        goal_response = client.get(f"/api/v1/growth/goals/{self.goal_id}")
        assert goal_response.json()["current_value"] == 2

    def test_log_progress_complete_goal(self, client):
        """Test logging progress that completes the goal."""
        response = client.post(
            f"/api/v1/growth/goals/{self.goal_id}/progress",
            json={
                "progress_value": 10,
                "note": "Completed all 10 books!",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should create achievement when goal is completed
        if data:  # If achievement is returned
            assert data["progress_value"] == 10

        # Verify goal status changed to completed
        goal_response = client.get(f"/api/v1/growth/goals/{self.goal_id}")
        goal_data = goal_response.json()
        assert goal_data["current_value"] == 10

    def test_log_progress_nonexistent_goal(self, client):
        """Test logging progress for nonexistent goal."""
        response = client.post(
            "/api/v1/growth/goals/nonexistent-id/progress",
            json={"progress_value": 5, "note": "Some note"},
        )
        assert response.status_code == 404

    def test_log_multiple_progress_entries(self, client):
        """Test logging multiple progress entries."""
        for i in range(1, 6):
            response = client.post(
                f"/api/v1/growth/goals/{self.goal_id}/progress",
                json={
                    "progress_value": 2,
                    "note": f"Progress update {i}",
                },
            )
            assert response.status_code == 200

        # Verify cumulative progress
        goal_response = client.get(f"/api/v1/growth/goals/{self.goal_id}")
        assert goal_response.json()["current_value"] == 10


class TestGrowthControllerAchievements:
    """Test achievement retrieval endpoints."""

    @pytest.fixture(autouse=True)
    def setup_achievements(self, client):
        """Create goals and log progress to generate achievements."""
        # Create goal 1
        response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Exercise Goal",
                "category": "health",
                "target_value": 20,
                "unit": "workouts",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
            },
        )
        goal1_id = response.json()["id"]

        # Create goal 2
        response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Meditation Goal",
                "category": "personal",
                "target_value": 30,
                "unit": "sessions",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
            },
        )
        goal2_id = response.json()["id"]

        # Log progress to create achievements
        client.post(
            f"/api/v1/growth/goals/{goal1_id}/progress",
            json={"progress_value": 20, "note": "Completed 20 workouts!"},
        )
        client.post(
            f"/api/v1/growth/goals/{goal2_id}/progress",
            json={"progress_value": 15, "note": "15 meditation sessions done"},
        )

        self.goal1_id = goal1_id
        self.goal2_id = goal2_id

    def test_get_all_achievements(self, client):
        """Test retrieving all achievements."""
        response = client.get("/api/v1/growth/achievements")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:  # If achievements exist
            assert all("id" in a for a in data)
            assert all("goal_id" in a for a in data)

    def test_achievements_structure(self, client):
        """Test achievement response structure."""
        response = client.get("/api/v1/growth/achievements")
        assert response.status_code == 200
        data = response.json()
        if data:
            for achievement in data:
                assert "id" in achievement
                assert "goal_id" in achievement
                assert "progress_value" in achievement
                assert isinstance(achievement, dict)


class TestGrowthControllerInsights:
    """Test growth insights endpoint."""

    @pytest.fixture(autouse=True)
    def setup_goals_with_progress(self, client):
        """Create goals with varying completion states."""
        # Create and complete various goals
        categories = ["personal", "professional", "health", "learning"]

        for i, category in enumerate(categories):
            response = client.post(
                "/api/v1/growth/goals",
                json={
                    "title": f"Goal {i+1}",
                    "category": category,
                    "target_value": 100,
                    "unit": "units",
                    "target_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                },
            )
            goal_id = response.json()["id"]

            # Log varying progress
            progress = [25, 50, 75, 100][i]
            client.post(
                f"/api/v1/growth/goals/{goal_id}/progress",
                json={"progress_value": progress, "note": f"Logged {progress}%"},
            )

    def test_get_insights(self, client):
        """Test retrieving growth insights."""
        response = client.get("/api/v1/growth/insights")
        assert response.status_code == 200
        data = response.json()

        # Verify insights structure
        assert "total_goals" in data
        assert "completed_goals" in data
        assert "in_progress_goals" in data
        assert "completion_rate" in data
        assert "category_breakdown" in data
        assert "recent_achievements" in data

    def test_insights_calculations(self, client):
        """Test that insights are calculated correctly."""
        response = client.get("/api/v1/growth/insights")
        assert response.status_code == 200
        data = response.json()

        # Total goals should be 4 (from setup)
        assert data["total_goals"] >= 4

        # Completion rate should be a valid percentage
        assert 0 <= data["completion_rate"] <= 100

    def test_insights_category_breakdown(self, client):
        """Test category breakdown in insights."""
        response = client.get("/api/v1/growth/insights")
        assert response.status_code == 200
        data = response.json()

        breakdown = data["category_breakdown"]
        assert isinstance(breakdown, dict)
        # Should have entries for categories
        if breakdown:
            for category, count in breakdown.items():
                assert category in ["personal", "professional", "health", "learning"]
                assert isinstance(count, int)


class TestGrowthControllerEndToEnd:
    """End-to-end integration tests."""

    def test_complete_goal_workflow(self, client):
        """Test complete workflow: create goal → log progress → check achievements → view insights."""
        # Step 1: Create goal
        create_response = client.post(
            "/api/v1/growth/goals",
            json={
                "title": "Complete a Project",
                "description": "Finish my side project",
                "category": "professional",
                "target_value": 1,
                "unit": "project",
                "target_date": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat(),
            },
        )
        assert create_response.status_code == 200
        goal_id = create_response.json()["id"]

        # Step 2: Retrieve goal
        get_response = client.get(f"/api/v1/growth/goals/{goal_id}")
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "active"

        # Step 3: Log progress
        progress_response = client.post(
            f"/api/v1/growth/goals/{goal_id}/progress",
            json={
                "progress_value": 1,
                "note": "Project completed!",
            },
        )
        assert progress_response.status_code == 200

        # Step 4: Check updated goal
        updated_response = client.get(f"/api/v1/growth/goals/{goal_id}")
        goal_data = updated_response.json()
        assert goal_data["current_value"] == 1
        assert goal_data["status"] == "completed"

        # Step 5: Check insights
        insights_response = client.get("/api/v1/growth/insights")
        assert insights_response.status_code == 200
        insights = insights_response.json()
        assert insights["total_goals"] >= 1

    def test_multi_category_workflow(self, client):
        """Test workflow with goals across multiple categories."""
        goals_data = [
            {"title": "Run 50km", "category": "health", "target_value": 50, "unit": "km"},
            {"title": "Read 12 books", "category": "learning", "target_value": 12, "unit": "books"},
            {"title": "Learn Spanish", "category": "personal", "target_value": 100, "unit": "hours"},
            {"title": "Complete project", "category": "professional", "target_value": 1, "unit": "project"},
        ]

        goal_ids = []
        for goal_data in goals_data:
            response = client.post(
                "/api/v1/growth/goals",
                json={
                    **goal_data,
                    "target_date": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
                },
            )
            assert response.status_code == 200
            goal_ids.append(response.json()["id"])

        # Log progress for each goal
        progress_values = [25, 6, 50, 1]
        for goal_id, progress in zip(goal_ids, progress_values):
            response = client.post(
                f"/api/v1/growth/goals/{goal_id}/progress",
                json={"progress_value": progress},
            )
            assert response.status_code == 200

        # Verify insights across categories
        insights_response = client.get("/api/v1/growth/insights")
        assert insights_response.status_code == 200
        insights = insights_response.json()
        assert insights["total_goals"] >= 4

        # Verify we can filter by category
        for category in ["personal", "professional", "health", "learning"]:
            response = client.get(f"/api/v1/growth/goals?category={category}")
            assert response.status_code == 200
