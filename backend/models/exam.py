"""Exam document helpers for MongoDB."""

from datetime import datetime, timezone


def create_exam_doc(
    title: str,
    subject: str,
    topic: str,
    syllabus: str,
    questions: list,
    duration_minutes: int,
    exam_code: str,
    created_by: str,
    config: dict = None,
) -> dict:
    """Create an exam document for MongoDB insertion."""
    return {
        "title": title,
        "subject": subject,
        "topic": topic,
        "syllabus": syllabus,
        "questions": questions,
        "duration_minutes": duration_minutes,
        "exam_code": exam_code,
        "created_by": created_by,
        "status": "active",  # active, expired, draft
        "config": config or {},
        "created_at": datetime.now(timezone.utc),
    }
