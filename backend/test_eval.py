import asyncio
import os
import sys

sys.path.append(os.path.dirname(__file__))

from agents.evaluation_agent import evaluation_agent

async def test_eval():
    questions = [
        {
            "id": 1,
            "type": "mcq",
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": "4",
            "marks": 1,
        },
        {
            "id": 2,  # Let's see if string vs int id matters
            "type": "short",
            "question": "Explain trees.",
            "model_answer": "A tree is a hierarchical data structure.",
            "keywords": ["hierarchical", "data", "structure"],
            "marks": 3,
        }
    ]
    
    # Frontend sends string values for answer
    answers = [
        {"question_id": 1, "answer": "4"},
        {"question_id": 2, "answer": "It is a hierarchical structure for data."}
    ]
    
    result = await evaluation_agent(questions, answers)
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_eval())
