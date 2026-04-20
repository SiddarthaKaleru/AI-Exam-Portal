"""Agent 1 — Content Understanding Agent.

Parses PDF, chunks text, builds FAISS vector index, extracts topics via LLM.
"""

from services.pdf_service import extract_and_chunk
from services.vector_store import create_store
from services.llm_service import generate_json


def content_agent(state: dict) -> dict:
    """Process PDF and build knowledge base."""
    print("🧠 Agent 1: Content Understanding — processing PDFs...")

    # Extract and chunk all PDFs
    pdf_text = ""
    chunks = []
    pdf_paths = state.get("pdf_paths", [])
    for i, pdf_path in enumerate(pdf_paths, 1):
        print(f"   📄 Processing PDF {i}/{len(pdf_paths)}: {pdf_path}")
        result = extract_and_chunk(pdf_path)
        pdf_text += result["full_text"] + "\n\n"
        chunks.extend(result["chunks"])

    # Build FAISS vector store
    store_id = f"exam_{state.get('subject', 'default')}_{state.get('topic', 'default')}"
    create_store(store_id, chunks)

    # Extract topics using LLM
    topic_prompt = f"""Analyze the following academic content and extract the main topics/concepts covered.

Subject: {state.get('subject', 'General')}
Topic Area: {state.get('topic', 'General')}
Syllabus: {state.get('syllabus', 'Not provided')}

Content (first 3000 chars):
{pdf_text[:3000]}

Return a JSON array of topic strings. Example: ["Topic 1", "Topic 2", "Topic 3"]
Extract between 3-8 key topics from the content."""

    topics = generate_json(topic_prompt)
    if isinstance(topics, dict):
        topics = topics.get("topics", list(topics.values())[0] if topics else [])

    print(f"   ✅ Extracted {len(chunks)} chunks, {len(topics)} topics: {topics}")

    return {
        **state,
        "pdf_text": pdf_text,
        "chunks": chunks,
        "topics": topics if isinstance(topics, list) else [str(topics)],
        "store_id": store_id,
        "status": "content_processed",
    }
