# 🎓 AI Exam Portal — Multi-Agent System

An AI-powered exam portal where admins upload syllabus/notes PDFs, and a **7-agent LangGraph pipeline** automatically generates exams, manages student sessions, evaluates answers, and produces analytics dashboards. Integrated with **LangSmith** for full LLM observability, trace monitoring, and automated benchmark evaluation.

---

## ✨ Key Features

### 👨‍💼 Admin Side
- **Multi-PDF Upload** — Upload up to 5 PDF files per exam for richer content generation
- **AI-Powered Question Generation** — Automatically creates MCQs, Short Answer, and Long Answer questions from uploaded PDFs using LLM
- **Configurable Marks** — Assign custom point values for each question type (MCQ, Short, Long) during exam creation
- **Configurable Question Counts** — Set exactly how many MCQs, Short, and Long questions to generate
- **Unique Exam Codes** — Auto-generated 6-character codes for easy student access
- **Admin Dashboard** — View all exams with status badges, exam codes, and quick access to analytics
- **Detailed Analytics** — Per-exam analytics including score distribution, topic-wise analysis, and student rankings with name & email

### 👩‍🎓 Student Side
- **Simple Exam Access** — Enter a 6-character code to instantly join an exam
- **Timed Exams** — Countdown timer with auto-submit when time expires
- **Instant AI Grading** — Get scores immediately after submission with detailed question-by-question feedback
- **Past Exams History** — View all previously taken exams with scores, percentages, and links to detailed results
- **Detailed Results Page** — Review each question's marks, correct answers, and AI feedback

### 🛡️ Anti-Cheating Measures
- **Tab Switch Detection** — Warns students on tab switch; auto-submits after 3 tab switches
- **Paste Disabled** — Clipboard paste is blocked in answer fields
- **Copy Protection** — Question text cannot be copied
- **Event Logging** — All anti-cheat events are recorded per student session

### 🔬 Evaluation & Observability (LangSmith)
- **Full LLM Tracing** — Real-time tracking of every prompt, response, latency, and token consumption on LangSmith
- **Automated Agent Benchmark Evaluation** — Standalone evaluation suite testing question quality, scoring accuracy, and topic extraction
- **Semantic Answer Evaluation** — LLM-based evaluation for short and long answers (not just keyword matching)
- **Direct MCQ Scoring** — Instant correct/incorrect evaluation for multiple choice
- **Hallucination-Safe Marks** — Post-LLM override ensures configured marks are always respected

---

## 🤖 Multi-Agent Architecture

The exam generation pipeline uses **LangGraph** to orchestrate 7 specialized agents:

| Agent | Role |
|---|---|
| 🧠 Agent 1 — Content Understanding | PDF parsing → text chunking → FAISS vector indexing → topic extraction |
| 📝 Agent 2 — Question Generator | MCQ + Short + Long questions at Easy/Medium/Hard with configurable marks |
| 🏗️ Agent 3 — Website Builder | Generates exam config JSON for dynamic frontend rendering |
| 📋 Agent 4 — Exam Manager | Creates exam documents with unique codes, timer config, and session state |
| ✅ Agent 5 — Evaluation | Direct MCQ scoring + LLM-based semantic evaluation for subjective answers |
| 🛡️ Agent 6 — Anti-Cheating | Tab switch, copy-paste, and focus loss detection & logging |
| 📊 Agent 7 — Analytics | Score distribution, topic-wise weakness analysis, and student rankings |

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, LangGraph |
| **LLM & Tracing** | OpenRouter / LiteLLM, LangSmith, LangChain |
| **Database** | MongoDB Atlas / Local MongoDB |
| **Vector DB** | FAISS + sentence-transformers (`all-MiniLM-L6-v2`) |
| **Frontend** | React 18 + Vite + Tailwind CSS |
| **Auth** | JWT (JSON Web Tokens) + bcrypt |
| **Deployment** | Docker & Docker Compose |

---

## 🔬 LangSmith Observability & Evaluation

This project is instrumented with **LangSmith** to monitor LLM operations, trace agent execution paths, and run automated evaluation benchmarks.

### 1. Tracing
When `LANGCHAIN_TRACING_V2=true` is set, all agent invocations and LLM completions are streamed directly to LangSmith:
- **Trace Details:** Inspect system prompts, user inputs, raw outputs, token counts, and execution latency.
- **Agent Chains:** View nested multi-agent runs across the LangGraph StateGraph pipeline.

### 2. Running Automated Evaluations
Run the built-in test suite to evaluate agent performance across 8 benchmark test cases:

```bash
cd backend
python langsmith_eval.py
```

### 3. Evaluation Metrics
The evaluation script uploads datasets and runs custom evaluators in LangSmith:
- **`question_quality`**: Validates question structure, required keys, 4 options for MCQs, and valid correct answer mapping.
- **`evaluation_accuracy`**: Benchmarks the Evaluation Agent against ground-truth student answers (MCQ exact matching & semantic short answers).
- **`topic_extraction`**: Checks topic count, coherence, and syllabus keyword coverage.

Results, comparison charts, and run traces are accessible on [smith.langchain.com](https://smith.langchain.com) under the configured project (`ai-exam-portal`).

---

## 🐳 Run with Docker (Recommended)

Make sure you have **Docker Desktop** installed and running on your system.

### 1. Configure Environment Variables
Copy `.env.example` to `.env` in the root directory and configure your keys:
```bash
cp .env.example .env
```

### 2. Build and Start All Containers
```bash
docker compose up --build
```
> **What this does:**
> - Launches **MongoDB** container on port `27017` with persistent volume
> - Builds and runs the **FastAPI Backend** container on port `8000`
> - Builds and serves the **React Frontend** via Nginx on ports `5173` and `3000` with automatic API reverse-proxying

### 3. Open in Browser
- Frontend Application: [http://localhost:5173](http://localhost:5173) or [http://localhost:3000](http://localhost:3000)
- Backend Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

To stop the containers:
```bash
docker compose down
```

---

## 🚀 Manual Quick Start (Without Docker)

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (Local or Atlas account)
- OpenRouter API key
- LangSmith API key (Optional, for tracing & evaluation)

### 1. Backend Setup

```bash
cd backend

# Create .env from template
cp .env.example .env
# Edit .env with your MongoDB URI, OpenRouter key, and LangSmith key

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Usage Guide

1. Open `http://localhost:5173`
2. **Register as Admin** → Login
3. **Create Exam**: Upload PDFs → Fill exam details → Configure question counts & marks → Generate
4. **Copy the 6-character exam code**
5. Open incognito → **Register as Student** → Enter exam code
6. Take the exam → Submit → View instant AI-graded results
7. **Student Dashboard**: View all past exams and scores
8. **Admin**: View detailed analytics dashboard per exam

---

## 📁 Project Structure

```
├── backend/
│   ├── agents/              # 7 LangGraph agents + orchestrator
│   │   ├── content_agent.py         # PDF parsing & vector indexing
│   │   ├── question_agent.py        # AI question generation
│   │   ├── website_agent.py         # Exam config builder
│   │   ├── exam_manager_agent.py    # Exam document & code creation
│   │   ├── evaluation_agent.py      # Answer evaluation (MCQ + LLM)
│   │   ├── anti_cheat_agent.py      # Anti-cheat event analysis
│   │   ├── analytics_agent.py       # Score analytics & rankings
│   │   ├── orchestrator.py          # LangGraph pipeline orchestration
│   │   └── state.py                 # Shared pipeline state definition
│   ├── models/              # MongoDB document models
│   │   ├── exam.py                  # Exam document helper
│   │   └── submission.py            # Submission document helper
│   ├── routes/              # FastAPI API endpoints
│   │   ├── auth.py                  # Register & Login
│   │   ├── admin.py                 # PDF upload, exam creation, listing
│   │   ├── exam.py                  # Student exam access, submit, results
│   │   └── analytics.py             # Exam analytics
│   ├── services/            # Core services
│   │   ├── pdf_service.py           # PDF text extraction
│   │   ├── vector_store.py          # FAISS vector store management
│   │   └── llm_service.py           # LLM client with LangSmith tracing
│   ├── utils/               # Utilities
│   │   └── auth.py                  # JWT token helpers
│   ├── langsmith_eval.py    # LangSmith evaluation benchmark suite
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # MongoDB connection
│   ├── config.py            # Environment config
│   ├── Dockerfile           # Backend containerization
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/           # React page components
│   │   │   ├── Login.jsx            # Login page
│   │   │   ├── Register.jsx         # Registration page
│   │   │   ├── AdminDashboard.jsx   # Admin exam management
│   │   │   ├── CreateExam.jsx       # Multi-step exam creation wizard
│   │   │   ├── StudentDashboard.jsx # Exam join + past exams history
│   │   │   ├── ExamPortal.jsx       # Live exam taking interface
│   │   │   ├── Results.jsx          # Detailed result breakdown
│   │   │   └── Analytics.jsx        # Admin analytics dashboard
│   │   ├── components/      # Reusable UI components
│   │   │   ├── Navbar.jsx           # Navigation bar
│   │   │   ├── ProtectedRoute.jsx   # Auth route guard
│   │   │   ├── QuestionCard.jsx     # Question display component
│   │   │   └── Timer.jsx            # Exam countdown timer
│   │   └── services/
│   │       └── api.js               # Axios API client with JWT
│   ├── Dockerfile           # Frontend containerization
│   ├── nginx.conf           # Nginx reverse proxy configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── vite.config.js       # Vite build configuration
├── docker-compose.yml       # Multi-container orchestration
└── README.md
```

---

## 🔑 Environment Variables

Create a `.env` file in the `backend/` directory or root directory:

```env
# MongoDB
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?appName=Cluster0
DB_NAME=ai_exam_portal

# LLM (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key_here
LLM_MODEL=openrouter/nvidia/nemotron-3-super-120b-a12b:free

# Auth
JWT_SECRET=your_jwt_secret_key_here

# LangSmith Tracing & Evaluation (https://smith.langchain.com)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=ai-exam-portal
```

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user (admin/student) |
| POST | `/api/auth/login` | Login and receive JWT token |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/admin/upload` | Upload PDF files (up to 5) |
| POST | `/api/admin/create-exam` | Create exam via AI pipeline |
| GET | `/api/admin/exams` | List all exams |

### Exam (Student)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/exam/{code}` | Fetch exam questions (answers stripped) |
| POST | `/api/exam/{code}/start` | Record exam start time |
| POST | `/api/exam/{code}/submit` | Submit answers for evaluation |
| POST | `/api/exam/{code}/anti-cheat` | Report anti-cheat events |
| GET | `/api/exam/{code}/result` | Get detailed exam results |
| GET | `/api/exam/student/submissions` | Get all past exam submissions |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analytics/{examId}` | Get exam analytics & rankings |

---

## 📜 License

This project is built for educational purposes as a Major Project.

