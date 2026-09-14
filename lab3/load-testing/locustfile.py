"""
Load Testing with Locust – Lab 3
Simulates realistic user behavior against the application.

Usage:
  # Headless mode (CI/CD):
  locust -f locustfile.py --headless -u 100 -r 10 --run-time 60s --host http://localhost:8080

  # Web UI mode:
  locust -f locustfile.py --host http://localhost:8080
  # Then open http://localhost:8089
"""
import json
import random
import time
from locust import HttpUser, TaskSet, task, between, events
from locust.env import Environment


class UserBehavior(TaskSet):
    """Simulates typical application user behavior."""

    def on_start(self):
        """Called when a simulated user starts – perform login."""
        self.login()

    def login(self):
        response = self.client.post("/api/auth/login", json={
            "username": f"user_{random.randint(1, 100)}",
            "password": "testpassword"
        }, catch_response=True)

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token", "")
            response.success()
        else:
            self.token = ""
            response.failure(f"Login failed: {response.status_code}")

    @property
    def auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def get_homepage(self):
        """Most frequent – browse homepage."""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.failure("Homepage not found")

    @task(4)
    def get_dashboard(self):
        """Fetch main dashboard data."""
        with self.client.get("/api/dashboard", headers=self.auth_headers,
                             catch_response=True) as response:
            if response.status_code in [200, 304]:
                response.success()
            else:
                response.failure(f"Dashboard error: {response.status_code}")

    @task(3)
    def get_metrics(self):
        """Fetch metrics endpoint."""
        self.client.get("/metrics")

    @task(2)
    def list_items(self):
        """Browse item listing."""
        page = random.randint(1, 10)
        self.client.get(f"/api/items?page={page}&limit=20",
                        headers=self.auth_headers)

    @task(2)
    def get_item_detail(self):
        """View individual item."""
        item_id = random.randint(1, 500)
        with self.client.get(f"/api/items/{item_id}", headers=self.auth_headers,
                             catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Item error: {response.status_code}")

    @task(1)
    def create_item(self):
        """Submit a new item (write operation)."""
        self.client.post("/api/items", json={
            "name": f"Test Item {random.randint(1, 9999)}",
            "value": random.uniform(1.0, 100.0),
            "category": random.choice(["A", "B", "C"])
        }, headers=self.auth_headers)

    @task(1)
    def health_check(self):
        """Check application health."""
        self.client.get("/health")


class SpikeUser(HttpUser):
    """Regular user with normal think time."""
    tasks = [UserBehavior]
    wait_time = between(1, 3)
    weight = 3


class HeavyUser(HttpUser):
    """Power user with shorter think time – higher load."""
    tasks = [UserBehavior]
    wait_time = between(0.5, 1.5)
    weight = 1


# ── Event Hooks ────────────────────────────────────────────────────────────────
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"\n{'='*60}")
    print(f"  Lab 3 Load Test Starting")
    print(f"  Target: {environment.host}")
    print(f"  Users:  {environment.runner.target_user_count if environment.runner else 'N/A'}")
    print(f"{'='*60}\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.runner.stats
    print(f"\n{'='*60}")
    print(f"  Load Test Complete")
    print(f"  Total Requests:  {stats.total.num_requests}")
    print(f"  Total Failures:  {stats.total.num_failures}")
    print(f"  Avg Response:    {stats.total.avg_response_time:.1f}ms")
    print(f"  P95 Response:    {stats.total.get_response_time_percentile(0.95):.1f}ms")
    print(f"  RPS:             {stats.total.current_rps:.1f}")
    print(f"{'='*60}\n")
