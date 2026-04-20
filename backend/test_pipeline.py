import asyncio
import os
import sys

# Add backend to path so imports work
sys.path.append(os.path.dirname(__file__))

from database import connect_db, close_db
from agents.orchestrator import run_exam_pipeline

async def test():
    await connect_db()
    
    input_state = {
        "subject": "Test Subj",
        "topic": "Test Topic",
        "syllabus": "Just test data",
        "pdf_path": "",
        "pdf_text": "This is test notes about trees and graphs.",
        "duration_minutes": 10,
        "num_mcq": 1,
        "num_short": 0,
        "num_long": 0,
        "created_by": "admin"
    }
    
    # We skip content_agent normally by mocking pdf_text, but we need to pass a mock if we want it to work fully, 
    # Actually wait, content_agent requires pdf_path.
    # Let's just create a tiny test.pdf
    with open("test.txt", "w") as f:
        f.write("This is a test document. Trees and graphs are data structures.")
    
    input_state["pdf_path"] = "test.txt"
    
    print("Running pipeline...")
    result = await run_exam_pipeline(input_state)
    print("Result status:", result.get("status"))
    print("Error if any:", result.get("error"))
    print("Exam code:", result.get("exam_code"))
    
    await close_db()

if __name__ == "__main__":
    asyncio.run(test())
