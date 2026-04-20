"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_db, close_db
from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.exam import router as exam_router
from routes.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await connect_db()
    yield
    await close_db()


# ─── App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Exam Portal",
    description="Multi-Agent AI-powered exam generation and management system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routes ────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(exam_router)
app.include_router(analytics_router)


# ─── Health Check ────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "message": "🎓 AI Exam Portal API is running!",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
