"""
Admin endpoints for email management and testing.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.overdue_email_scheduler import overdue_scheduler

router = APIRouter(prefix="/admin/email", tags=["Email Admin"])


@router.api_route("/trigger-overdue-check", methods=["GET", "POST"])
def trigger_overdue_check():
    """
    Manually trigger an overdue email check.
    Useful for testing or immediate processing.
    Supports both GET and POST methods for convenience.
    """
    try:
        overdue_scheduler.run_manual_check()
        return {"message": "Overdue email check triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering check: {str(e)}")


@router.get("/scheduler-status")
def get_scheduler_status():
    """Get the current status of the overdue email scheduler."""
    return {
        "is_running": overdue_scheduler.is_running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None
            }
            for job in overdue_scheduler.scheduler.get_jobs()
        ]
    }



