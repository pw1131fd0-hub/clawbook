"""API controller for performance monitoring endpoints."""
import logging
from fastapi import APIRouter, Query
from backend.services.performance_service import get_performance_monitor

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics")
async def get_metrics(endpoint: str | None = Query(None), method: str | None = Query(None)):
    """Get aggregated performance metrics for endpoints.

    Query Parameters:
        - endpoint: Optional endpoint path to filter by
        - method: Optional HTTP method to filter by (GET, POST, etc.)

    Returns:
        List of performance metrics for matching endpoints
    """
    monitor = get_performance_monitor()
    metrics = monitor.get_endpoint_metrics(endpoint=endpoint, method=method)
    return {"metrics": metrics}


@router.get("/slowest")
async def get_slowest_endpoints(limit: int = Query(10, ge=1, le=100)):
    """Get the slowest endpoints by average response time.

    Query Parameters:
        - limit: Maximum number of results to return (default: 10, max: 100)

    Returns:
        List of slowest endpoints with their metrics
    """
    monitor = get_performance_monitor()
    slowest = monitor.get_slowest_endpoints(limit=limit)
    return {"slowest_endpoints": slowest, "count": len(slowest)}


@router.get("/summary")
async def get_performance_summary():
    """Get overall performance summary across all endpoints.

    Returns:
        Overall performance statistics including:
        - avg_response_time_ms: Average response time across all endpoints
        - min_response_time_ms: Minimum response time
        - max_response_time_ms: Maximum response time
        - total_requests: Total number of requests tracked
        - endpoints_tracked: Number of unique endpoints
    """
    monitor = get_performance_monitor()
    summary = monitor.get_performance_summary()
    return summary


@router.get("/errors")
async def get_error_summary():
    """Get error summary and statistics.

    Returns:
        Error statistics including:
        - total_requests: Total number of requests
        - total_errors: Total number of errors (non-2xx responses)
        - error_rate: Percentage of requests that resulted in errors
        - uptime_seconds: Time the monitor has been active
    """
    monitor = get_performance_monitor()
    errors = monitor.get_error_summary()
    return errors


@router.post("/reset")
async def reset_metrics():
    """Reset all performance metrics (admin function).

    Warning: This will clear all collected performance data.

    Returns:
        Confirmation message
    """
    monitor = get_performance_monitor()
    monitor.reset_metrics()
    logger.info("Performance metrics reset by admin")
    return {"message": "Performance metrics reset successfully"}
