"""PDF text extraction and chunking service using PyMuPDF."""

import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for vector indexing."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def extract_and_chunk(file_path: str, chunk_size: int = 500, overlap: int = 50) -> dict:
    """Extract text from PDF and split into chunks."""
    full_text = extract_text_from_pdf(file_path)
    chunks = chunk_text(full_text, chunk_size, overlap)
    return {
        "full_text": full_text,
        "chunks": chunks,
        "num_chunks": len(chunks),
    }
