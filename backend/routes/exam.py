"""Exam routes — student-facing exam endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import get_database
from utils.auth import get_current_user
from models.submission import create_submission_doc
from agents.evaluation_agent import evaluation_agent
from agents.anti_cheat_agent import anti_cheat_agent
from bson import ObjectId

router = APIRouter(prefix="/api/exam", tags=["Exam"])


# ─── Schemas ─────────────────────────────────────────────────────────

class SubmitExamRequest(BaseModel):
    answers: list  # [{question_id: int, answer: str}, ...]


class AntiCheatEvent(BaseModel):
    events: list  # [{type: str, timestamp: str}, ...]


# ─── Endpoints ───────────────────────────────────────────────────────

@router.get("/{exam_code}")
async def get_exam(exam_code: str, user: dict = Depends(get_current_user)):
    """Fetch exam for a student (questions without correct answers)."""
    db = get_database()

    exam = await db.exams.find_one({"exam_code": exam_code.upper()})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found. Check your exam code.")

    if exam.get("status") != "active":
        raise HTTPException(status_code=400, detail="This exam is no longer active.")

    # Strip correct answers from questions before sending to student
    safe_questions = []
    for q in exam.get("questions", []):
        safe_q = {
            "id": q.get("id"),
            "type": q.get("type"),
            "question": q.get("question"),
            "difficulty": q.get("difficulty"),
            "marks": q.get("marks"),
            "topic": q.get("topic"),
        }
        if q.get("type") == "mcq":
            safe_q["options"] = q.get("options", [])
        safe_questions.append(safe_q)

    return {
        "exam": {
            "id": str(exam["_id"]),
            "title": exam.get("config", {}).get("title", exam.get("title", "")),
            "subject": exam.get("subject", ""),
            "topic": exam.get("topic", ""),
            "duration_minutes": exam.get("duration_minutes", 30),
            "total_marks": exam.get("config", {}).get("total_marks", 0),
            "questions": safe_questions,
            "config": exam.get("config", {}),
        }
    }


@router.post("/{exam_code}/start")
async def start_exam(exam_code: str, user: dict = Depends(get_current_user)):
    """Record exam start time for a student."""
    db = get_database()

    exam = await db.exams.find_one({"exam_code": exam_code.upper()})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Check if already started
    existing = await db.exam_sessions.find_one({
        "exam_id": str(exam["_id"]),
        "student_id": user.get("sub", ""),
    })

    if existing:
        return {
            "message": "Exam already started",
            "started_at": existing.get("started_at"),
        }

    # Create session
    session = {
        "exam_id": str(exam["_id"]),
        "student_id": user.get("sub", ""),
        "started_at": datetime.now(timezone.utc),
        "anti_cheat_events": [],
    }
    await db.exam_sessions.insert_one(session)

    return {
        "message": "Exam started",
        "started_at": session["started_at"],
        "duration_minutes": exam.get("duration_minutes", 30),
    }


@router.post("/{exam_code}/submit")
async def submit_exam(
    exam_code: str,
    req: SubmitExamRequest,
    user: dict = Depends(get_current_user),
):
    """Submit exam answers and trigger evaluation."""
    db = get_database()

    exam = await db.exams.find_one({"exam_code": exam_code.upper()})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Check if a submission already exists
    existing_sub = await db.submissions.find_one({
        "exam_id": str(exam["_id"]),
        "student_id": user.get("sub", ""),
    })

    if existing_sub:
        raise HTTPException(status_code=400, detail="You have already submitted this exam")

    # Run evaluation agent
    eval_result = await evaluation_agent(
        questions=exam.get("questions", []),
        answers=req.answers,
    )

    # Get anti-cheat data
    session = await db.exam_sessions.find_one({
        "exam_id": str(exam["_id"]),
        "student_id": user.get("sub", ""),
    })
    anti_cheat_flags = []
    if session and session.get("anti_cheat_events"):
        ac_result = anti_cheat_agent(session["anti_cheat_events"])
        anti_cheat_flags = ac_result.get("flags", [])

    # Fetch full user details to get the actual name
    student_user = await db.users.find_one({"_id": ObjectId(user.get("sub"))})
    actual_name = student_user.get("name", "Unknown") if student_user else "Unknown"

    # Create submission
    submission = create_submission_doc(
        exam_id=str(exam["_id"]),
        student_id=user.get("sub", ""),
        student_name=actual_name,
        answers=req.answers,
    )
    submission["student_email"] = user.get("email", "Unknown")
    submission.update({
        "score": eval_result.get("score", 0),
        "max_score": eval_result.get("max_score", 0),
        "percentage": eval_result.get("percentage", 0),
        "evaluation_details": eval_result.get("evaluation_details", []),
        "anti_cheat_flags": anti_cheat_flags,
    })

    # Use find_one_and_update with upsert to prevent race conditions
    from pymongo import ReturnDocument
    
    result = await db.submissions.find_one_and_update(
        {
            "exam_id": str(exam["_id"]),
            "student_id": user.get("sub", "")
        },
        {"$setOnInsert": submission},
        upsert=True,
        return_document=ReturnDocument.BEFORE
    )

    # If result is not None, it means the document already existed before this update
    if result is not None:
        raise HTTPException(status_code=400, detail="You have already submitted this exam")

    # Need to fetch the newly created ID
    new_doc = await db.submissions.find_one({
        "exam_id": str(exam["_id"]),
        "student_id": user.get("sub", ""),
    })

    return {
        "message": "Exam submitted and evaluated!",
        "submission_id": str(new_doc["_id"]),
        "score": eval_result.get("score", 0),
        "max_score": eval_result.get("max_score", 0),
        "percentage": eval_result.get("percentage", 0),
    }


@router.post("/{exam_code}/anti-cheat")
async def report_anti_cheat(
    exam_code: str,
    req: AntiCheatEvent,
    user: dict = Depends(get_current_user),
):
    """Report anti-cheat events from the frontend."""
    db = get_database()

    exam = await db.exams.find_one({"exam_code": exam_code.upper()})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Append events to session
    await db.exam_sessions.update_one(
        {"exam_id": str(exam["_id"]), "student_id": user.get("sub", "")},
        {"$push": {"anti_cheat_events": {"$each": req.events}}},
    )

    return {"message": "Events recorded"}


@router.get("/{exam_code}/result")
async def get_result(exam_code: str, user: dict = Depends(get_current_user)):
    """Get exam result for a student."""
    db = get_database()

    exam = await db.exams.find_one({"exam_code": exam_code.upper()})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    submission = await db.submissions.find_one({
        "exam_id": str(exam["_id"]),
        "student_id": user.get("sub", ""),
    })

    if not submission:
        raise HTTPException(status_code=404, detail="No submission found for this exam")

    submission["_id"] = str(submission["_id"])

    return {
        "exam_title": exam.get("title", ""),
        "result": submission,
    }

@router.get("/student/submissions")
async def get_student_submissions(user: dict = Depends(get_current_user)):
    """Get all past exam submissions for the logged-in student."""
    db = get_database()
    student_id = user.get("sub", "")
    
    # 1. Fetch all submissions by this student
    cursor = db.submissions.find({"student_id": student_id}).sort("submitted_at", -1)
    submissions = await cursor.to_list(length=100)
    
    # 2. Extract unique exam IDs
    exam_ids = list({ObjectId(sub["exam_id"]) for sub in submissions if sub.get("exam_id")})
    
    # 3. Fetch corresponding exam details
    exams_cursor = db.exams.find({"_id": {"$in": exam_ids}}, {"title": 1, "subject": 1, "topic": 1, "exam_code": 1})
    exams_data = await exams_cursor.to_list(length=100)
    
    # Create lookup dictionary
    exam_lookup = {str(e["_id"]): e for e in exams_data}
    
    # 4. Format the final output
    formatted_submissions = []
    for sub in submissions:
        exam_info = exam_lookup.get(sub.get("exam_id"), {})
        
        # Determine title
        title = exam_info.get("title")
        if not title and exam_info.get("subject"):
            title = f"{exam_info.get('subject')} - {exam_info.get('topic', 'Exam')}"
        elif not title:
            title = "Unknown Exam"
            
        formatted_submissions.append({
            "submission_id": str(sub["_id"]),
            "exam_id": sub.get("exam_id"),
            "exam_code": exam_info.get("exam_code", "N/A"),
            "exam_title": title,
            "score": sub.get("score", 0),
            "max_score": sub.get("max_score", 0),
            "percentage": sub.get("percentage", 0),
            "submitted_at": sub.get("submitted_at")
        })
        
    return {"submissions": formatted_submissions}
