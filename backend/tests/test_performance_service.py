"""Tests for the performance monitoring service."""
import pytest
from datetime import datetime, UTC
from backend.services.performance_service import PerformanceMonitor, get_performance_monitor


class TestPerformanceMonitor:
    """Test cases for the PerformanceMonitor class."""

    def test_record_metric(self):
        """Test recording a single performance metric."""
        monitor = PerformanceMonitor()
        monitor.record_metric(
            endpoint="/api/v1/posts",
            method="GET",
            status_code=200,
            duration_ms=125.5
        )

        metrics = monitor.get_endpoint_metrics()
        assert len(metrics) == 1
        assert metrics[0]["endpoint"] == "/api/v1/posts"
        assert metrics[0]["method"] == "GET"
        assert metrics[0]["total_requests"] == 1
        assert metrics[0]["success_count"] == 1
        assert metrics[0]["error_count"] == 0

    def test_aggregated_metrics(self):
        """Test that multiple requests are aggregated correctly."""
        monitor = PerformanceMonitor()

        # Record multiple requests
        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        monitor.record_metric("/api/v1/posts", "GET", 200, 150.0)
        monitor.record_metric("/api/v1/posts", "GET", 200, 200.0)

        metrics = monitor.get_endpoint_metrics()
        assert len(metrics) == 1
        assert metrics[0]["total_requests"] == 3
        assert metrics[0]["success_count"] == 3
        assert metrics[0]["avg_response_time_ms"] == 150.0
        assert metrics[0]["min_response_time_ms"] == 100.0
        assert metrics[0]["max_response_time_ms"] == 200.0

    def test_error_tracking(self):
        """Test that errors are tracked correctly."""
        monitor = PerformanceMonitor()

        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        monitor.record_metric("/api/v1/posts", "GET", 500, 150.0)
        monitor.record_metric("/api/v1/posts", "POST", 201, 200.0)
        monitor.record_metric("/api/v1/posts", "POST", 400, 75.0)

        metrics = monitor.get_endpoint_metrics()
        get_metrics = next(m for m in metrics if m["method"] == "GET")
        post_metrics = next(m for m in metrics if m["method"] == "POST")

        assert get_metrics["total_requests"] == 2
        assert get_metrics["success_count"] == 1
        assert get_metrics["error_count"] == 1

        assert post_metrics["total_requests"] == 2
        assert post_metrics["success_count"] == 1
        assert post_metrics["error_count"] == 1

    def test_get_slowest_endpoints(self):
        """Test getting the slowest endpoints."""
        monitor = PerformanceMonitor()

        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        monitor.record_metric("/api/v1/comments", "GET", 200, 500.0)
        monitor.record_metric("/api/v1/users", "GET", 200, 250.0)

        slowest = monitor.get_slowest_endpoints(limit=2)
        assert len(slowest) == 2
        assert slowest[0]["endpoint"] == "/api/v1/comments"
        assert slowest[1]["endpoint"] == "/api/v1/users"

    def test_error_summary(self):
        """Test error summary calculation."""
        monitor = PerformanceMonitor()

        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        monitor.record_metric("/api/v1/posts", "GET", 500, 100.0)

        summary = monitor.get_error_summary()
        assert summary["total_requests"] == 3
        assert summary["total_errors"] == 1
        assert abs(summary["error_rate"] - 33.33) < 0.01

    def test_performance_summary(self):
        """Test overall performance summary."""
        monitor = PerformanceMonitor()

        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        monitor.record_metric("/api/v1/comments", "GET", 200, 200.0)

        summary = monitor.get_performance_summary()
        assert summary["total_requests"] == 2
        assert summary["endpoints_tracked"] == 2
        assert summary["avg_response_time_ms"] == 150.0
        assert summary["min_response_time_ms"] == 100.0
        assert summary["max_response_time_ms"] == 200.0

    def test_filter_by_endpoint(self):
        """Test filtering metrics by endpoint."""
        monitor = PerformanceMonitor()

        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        monitor.record_metric("/api/v1/comments", "GET", 200, 200.0)

        posts_metrics = monitor.get_endpoint_metrics(endpoint="/api/v1/posts")
        assert len(posts_metrics) == 1
        assert posts_metrics[0]["endpoint"] == "/api/v1/posts"

    def test_filter_by_method(self):
        """Test filtering metrics by HTTP method."""
        monitor = PerformanceMonitor()

        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        monitor.record_metric("/api/v1/posts", "POST", 201, 200.0)

        get_metrics = monitor.get_endpoint_metrics(method="GET")
        assert len(get_metrics) == 1
        assert get_metrics[0]["method"] == "GET"

    def test_reset_metrics(self):
        """Test resetting metrics."""
        monitor = PerformanceMonitor()

        monitor.record_metric("/api/v1/posts", "GET", 200, 100.0)
        assert len(monitor.get_endpoint_metrics()) == 1

        monitor.reset_metrics()
        assert len(monitor.get_endpoint_metrics()) == 0

    def test_global_monitor_singleton(self):
        """Test that the global monitor is a singleton."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        assert monitor1 is monitor2
