"""Agent 2 — Question Generator Agent.

Creates MCQs, short-answer, and long-answer questions at multiple difficulty levels.
"""

from services.vector_store import search_store
from services.llm_service import generate_json


def question_agent(state: dict) -> dict:
    """Generate exam questions from the knowledge base."""
    print("📝 Agent 2: Question Generator — creating questions...")

    topics = state.get("topics", [])
    store_id = state.get("store_id", "")
    subject = state.get("subject", "General")
    num_mcq = state.get("num_mcq", 5)
    num_short = state.get("num_short", 3)
    num_long = state.get("num_long", 2)
    marks_mcq = state.get("marks_mcq", 1)
    marks_short = state.get("marks_short", 3)
    marks_long = state.get("marks_long", 5)

    all_questions = []

    # Gather context from vector store for all topics
    context_chunks = []
    for topic in topics:
        results = search_store(store_id, topic, top_k=3)
        for r in results:
            context_chunks.append(r["chunk"])

    context = "\n\n".join(context_chunks[:15])  # Cap context size

    # Generate MCQs
    mcq_prompt = f"""You are an expert exam question generator for the subject: {subject}.

Based on this content:
{context}

Topics covered: {', '.join(topics)}

Generate exactly {num_mcq} Multiple Choice Questions (MCQs).
Mix difficulty levels: Easy, Medium, Hard.

Return JSON array with this EXACT structure:
[
  {{
    "type": "mcq",
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "difficulty": "easy",
    "topic": "Relevant Topic",
    "marks": {marks_mcq},
    "explanation": "Brief explanation of correct answer"
  }}
]"""

    mcqs = generate_json(mcq_prompt)
    if isinstance(mcqs, dict):
        mcqs = mcqs.get("questions", mcqs.get("mcqs", []))
    
    # Enforce exact marks to prevent LLM hallucinations
    for q in mcqs:
        q["marks"] = marks_mcq
        
    all_questions.extend(mcqs)

    # Generate Short Answer Questions
    short_prompt = f"""You are an expert exam question generator for the subject: {subject}.

Based on this content:
{context}

Topics covered: {', '.join(topics)}

Generate exactly {num_short} Short Answer Questions.
Mix difficulty levels. Each answer should be 2-4 sentences.

Return JSON array with this EXACT structure:
[
  {{
    "type": "short",
    "question": "Question text here?",
    "model_answer": "The expected answer in 2-4 sentences.",
    "difficulty": "medium",
    "topic": "Relevant Topic",
    "marks": {marks_short},
    "keywords": ["key1", "key2", "key3"]
  }}
]"""

    shorts = generate_json(short_prompt)
    if isinstance(shorts, dict):
        shorts = shorts.get("questions", shorts.get("short_answers", []))
        
    for q in shorts:
        q["marks"] = marks_short

    all_questions.extend(shorts)

    # Generate Long Answer Questions
    long_prompt = f"""You are an expert exam question generator for the subject: {subject}.

Based on this content:
{context}

Topics covered: {', '.join(topics)}

Generate exactly {num_long} Long Answer / Essay Questions.
These should require detailed explanations (5-10 sentences).

Return JSON array with this EXACT structure:
[
  {{
    "type": "long",
    "question": "Question text here?",
    "model_answer": "A detailed model answer covering all key points.",
    "difficulty": "hard",
    "topic": "Relevant Topic",
    "marks": {marks_long},
    "keywords": ["key1", "key2", "key3", "key4", "key5"]
  }}
]"""

    longs = generate_json(long_prompt)
    if isinstance(longs, dict):
        longs = longs.get("questions", longs.get("long_answers", []))
        
    for q in longs:
        q["marks"] = marks_long

    all_questions.extend(longs)

    # Add question IDs
    for idx, q in enumerate(all_questions):
        q["id"] = idx + 1

    print(f"   ✅ Generated {len(all_questions)} questions: {len(mcqs)} MCQ, {len(shorts)} Short, {len(longs)} Long")

    return {
        **state,
        "questions": all_questions,
        "status": "questions_generated",
    }
