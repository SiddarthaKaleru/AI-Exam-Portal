"""Agent 4 — Exam Manager Agent.

Generates unique exam codes, manages session state, timer configuration.
"""

import random
import string
from datetime import datetime, timezone
from database import get_database
from models.exam import create_exam_doc


def _generate_exam_code(length: int = 6) -> str:
    """Generate a unique alphanumeric exam code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


async def exam_manager_agent(state: dict) -> dict:
    """Create exam in database with unique code."""
    print("🔗 Agent 4: Exam Manager — creating exam link...")

    from motor.motor_asyncio import AsyncIOMotorClient
    from config import MONGO_URI, DB_NAME
    
    # Create a local client for this thread's event loop
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Generate unique exam code
    exam_code = _generate_exam_code()
    while await db.exams.find_one({"exam_code": exam_code}):
        exam_code = _generate_exam_code()

    # Create exam document
    exam_doc = create_exam_doc(
        title=state.get("exam_config", {}).get("title", "Untitled Exam"),
        subject=state.get("subject", ""),
        topic=state.get("topic", ""),
        syllabus=state.get("syllabus", ""),
        questions=state.get("questions", []),
        duration_minutes=state.get("duration_minutes", 30),
        exam_code=exam_code,
        created_by=state.get("created_by", ""),
        config=state.get("exam_config", {}),
    )

    result = await db.exams.insert_one(exam_doc)
    exam_id = str(result.inserted_id)

    print(f"   ✅ Exam created: code={exam_code}, id={exam_id}")

    return {
        **state,
        "exam_code": exam_code,
        "exam_id": exam_id,
        "status": "exam_created",
    }
