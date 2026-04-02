"""Performance monitoring and metrics service for ClawBook."""
import logging
import time
from datetime import datetime, UTC, timedelta
from typing import Optional, Dict, Any
from collections import defaultdict
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """A single performance metric data point."""

    timestamp: datetime
    value: float
    endpoint: str
    method: str
    status_code: int
    duration_ms: float


@dataclass
class PerformanceMetrics:
    """Aggregated performance metrics for a given period."""

    endpoint: str
    method: str
    total_requests: int = 0
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        return data


class PerformanceMonitor:
    """Monitors and aggregates performance metrics for API endpoints."""

    def __init__(self, retention_hours: int = 24):
        """Initialize the performance monitor.

        Args:
            retention_hours: How long to keep metrics in memory (default: 24 hours)
        """
        self.retention_hours = retention_hours
        self.metrics_buffer: list[MetricPoint] = []
        self.aggregated_metrics: Dict[tuple, PerformanceMetrics] = {}
        self._start_time = time.time()

    def record_metric(self, endpoint: str, method: str, status_code: int,
                     duration_ms: float) -> None:
        """Record a performance metric for an API call.

        Args:
            endpoint: The API endpoint path
            method: HTTP method (GET, POST, etc.)
            status_code: HTTP response status code
            duration_ms: Response time in milliseconds
        """
        try:
            now = datetime.now(UTC)
            metric = MetricPoint(
                timestamp=now,
                value=duration_ms,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                duration_ms=duration_ms
            )
            self.metrics_buffer.append(metric)

            # Update aggregated metrics
            self._update_aggregated_metrics(endpoint, method, status_code, duration_ms)

            # Clean up old data
            self._cleanup_old_metrics(now)

            logger.debug(f"Recorded metric: {endpoint} {method} - {duration_ms:.2f}ms - {status_code}")
        except Exception as e:
            logger.error(f"Error recording performance metric: {e}")

    def _update_aggregated_metrics(self, endpoint: str, method: str,
                                   status_code: int, duration_ms: float) -> None:
        """Update aggregated metrics for an endpoint."""
        key = (endpoint, method)

        if key not in self.aggregated_metrics:
            self.aggregated_metrics[key] = PerformanceMetrics(
                endpoint=endpoint,
                method=method
            )

        metrics = self.aggregated_metrics[key]
        metrics.total_requests += 1
        metrics.min_response_time_ms = min(metrics.min_response_time_ms, duration_ms)
        metrics.max_response_time_ms = max(metrics.max_response_time_ms, duration_ms)

        # Calculate running average
        total_time = (metrics.avg_response_time_ms * (metrics.total_requests - 1)) + duration_ms
        metrics.avg_response_time_ms = total_time / metrics.total_requests

        if 200 <= status_code < 300:
            metrics.success_count += 1
        else:
            metrics.error_count += 1

        metrics.last_updated = datetime.now(UTC)

    def _cleanup_old_metrics(self, now: datetime) -> None:
        """Remove metrics older than the retention period."""
        cutoff_time = now - timedelta(hours=self.retention_hours)
        self.metrics_buffer = [
            m for m in self.metrics_buffer
            if m.timestamp > cutoff_time
        ]

    def get_endpoint_metrics(self, endpoint: Optional[str] = None,
                            method: Optional[str] = None) -> list[Dict[str, Any]]:
        """Get aggregated metrics for endpoints.

        Args:
            endpoint: Optional endpoint to filter by
            method: Optional HTTP method to filter by

        Returns:
            List of metrics dictionaries
        """
        results = []
        for (ep, meth), metrics in self.aggregated_metrics.items():
            if endpoint and ep != endpoint:
                continue
            if method and meth != method:
                continue
            results.append(metrics.to_dict())
        return results

    def get_slowest_endpoints(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Get the slowest endpoints by average response time.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of slowest endpoint metrics
        """
        sorted_metrics = sorted(
            self.aggregated_metrics.values(),
            key=lambda m: m.avg_response_time_ms,
            reverse=True
        )
        return [m.to_dict() for m in sorted_metrics[:limit]]

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors across all endpoints.

        Returns:
            Dictionary with error statistics
        """
        total_errors = sum(m.error_count for m in self.aggregated_metrics.values())
        total_requests = sum(m.total_requests for m in self.aggregated_metrics.values())

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
            "uptime_seconds": time.time() - self._start_time,
            "timestamp": datetime.now(UTC).isoformat()
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary.

        Returns:
            Dictionary with overall metrics
        """
        if not self.aggregated_metrics:
            return {
                "avg_response_time_ms": 0,
                "min_response_time_ms": 0,
                "max_response_time_ms": 0,
                "total_requests": 0,
                "timestamp": datetime.now(UTC).isoformat()
            }

        metrics = list(self.aggregated_metrics.values())
        avg_times = [m.avg_response_time_ms for m in metrics]
        min_times = [m.min_response_time_ms for m in metrics]
        max_times = [m.max_response_time_ms for m in metrics]

        return {
            "avg_response_time_ms": sum(avg_times) / len(avg_times) if avg_times else 0,
            "min_response_time_ms": min(min_times) if min_times else 0,
            "max_response_time_ms": max(max_times) if max_times else 0,
            "total_requests": sum(m.total_requests for m in metrics),
            "endpoints_tracked": len(self.aggregated_metrics),
            "timestamp": datetime.now(UTC).isoformat()
        }

    def reset_metrics(self) -> None:
        """Reset all metrics and start fresh."""
        self.metrics_buffer = []
        self.aggregated_metrics = {}
        self._start_time = time.time()
        logger.info("Performance metrics reset")


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
