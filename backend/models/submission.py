"""Submission document helpers for MongoDB."""

from datetime import datetime, timezone


def create_submission_doc(
    exam_id: str,
    student_id: str,
    student_name: str,
    answers: list,
) -> dict:
    """Create a submission document for MongoDB insertion."""
    return {
        "exam_id": exam_id,
        "student_id": student_id,
        "student_name": student_name,
        "answers": answers,
        "score": 0,
        "max_score": 0,
        "percentage": 0,
        "evaluation_details": [],
        "anti_cheat_flags": [],
        "started_at": None,
        "submitted_at": datetime.now(timezone.utc),
    }
