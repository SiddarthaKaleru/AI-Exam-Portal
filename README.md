# 🎓 AI Exam Portal — Multi-Agent System

An AI-powered exam portal where admins upload syllabus/notes PDFs, and a **7-agent LangGraph pipeline** automatically generates exams, manages student sessions, evaluates answers, and produces analytics dashboards.

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

### 🤖 AI & Evaluation
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
| **LLM** | OpenRouter / Groq AI via litellm |
| **Database** | MongoDB Atlas |
| **Vector DB** | FAISS + sentence-transformers |
| **Frontend** | React 18 + Vite + Tailwind CSS |
| **Auth** | JWT (JSON Web Tokens) + bcrypt |
| **HTTP Client** | Axios with JWT interceptor |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB Atlas account
- OpenRouter / Groq API key

### 1. Backend Setup

```bash
cd backend

# Create .env from template
cp .env.example .env
# Edit .env with your MongoDB Atlas URI and API key

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

### 3. Usage

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
│   │   ├── website_builder_agent.py # Exam config builder
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
│   │   └── llm_service.py           # LLM client (OpenRouter/Groq)
│   ├── utils/               # Utilities
│   │   └── auth.py                  # JWT token helpers
│   ├── main.py              # FastAPI entry point
│   ├── database.py          # MongoDB connection
│   └── config.py            # Environment config
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
│   │   │   └── QuestionCard.jsx     # Question display component
│   │   └── services/
│   │       └── api.js               # Axios API client with JWT
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── vite.config.js       # Vite build configuration
└── README.md
```

---

## 🔑 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
DB_NAME=ai_exam_portal
JWT_SECRET=your-secret-key
OPENROUTER_API_KEY=your-api-key
```

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user (admin/student) |
| POST | `/api/auth/login` | Login and receive JWT token |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/upload` | Upload PDF files (up to 5) |
| POST | `/api/admin/create-exam` | Create exam via AI pipeline |
| GET | `/api/admin/exams` | List all exams |

### Exam (Student)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/exam/{code}` | Fetch exam questions (answers stripped) |
| POST | `/api/exam/{code}/start` | Record exam start time |
| POST | `/api/exam/{code}/submit` | Submit answers for evaluation |
| POST | `/api/exam/{code}/anti-cheat` | Report anti-cheat events |
| GET | `/api/exam/{code}/result` | Get detailed exam results |
| GET | `/api/exam/student/submissions` | Get all past exam submissions |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/{examId}` | Get exam analytics & rankings |

---

## 📜 License

This project is built for educational purposes as a Major Project.
