# TalentGraph

**AI-Powered Resume Analysis & Candidate–Job Matching Platform**

TalentGraph helps recruiters and applicants move faster from resume upload to ranked, explainable candidate matches. The platform parses PDF resumes, extracts and normalizes skills, builds structured candidate profiles, and scores candidates against job descriptions using a transparent rule-based matching engine.

---

## 1. Project Overview

Hiring teams spend significant time manually screening resumes and comparing candidate skills against job requirements. Applicants, in turn, lack clear feedback on how well their profile aligns with a role.

**TalentGraph** addresses this by automating the early stages of recruitment:

- **Recruiters** post jobs, review ranked applicants, inspect candidate details, and shortlist or reject candidates from a live dashboard.
- **Applicants** browse jobs, apply with a resume, and track application status and match scores.
- **Guests** can upload a resume with a sample job description for instant parsing and match feedback.

The solution is useful because it combines resume intelligence, job matching, and recruiter workflow tooling in a single MVP—without requiring manual spreadsheet screening for every applicant.

**Target users:**
- Recruiters / hiring managers
- Job applicants
- Hackathon evaluators and demo users testing resume-to-JD matching

---

## 2. Problem Statement

Modern recruitment faces three recurring bottlenecks:

1. **Manual resume screening** — Recruiters read hundreds of resumes to find relevant skills and experience.
2. **Weak job–candidate alignment** — Matching is often subjective and inconsistent across reviewers.
3. **Slow evaluation cycles** — Ranking, comparison, and shortlisting take time when done by hand.

TalentGraph reduces this friction by structuring resume data and producing ranked match results automatically.

---

## 3. Solution

TalentGraph implements an end-to-end pipeline from document upload to ranked output:

```
Resume (PDF) or JSONL dataset record
        ↓
Text extraction / structured record load
        ↓
Skill extraction & canonicalization
        ↓
Structured candidate profile
        ↓
Job description / requirements processing
        ↓
Keyword-based skill overlap matching
        ↓
Score-based candidate ranking
        ↓
Recruiter dashboard & applicant tracking
```

**Implemented components:**

| Stage | Implementation |
|-------|----------------|
| Resume parsing | PDF text extraction via `pdfplumber` |
| Skill extraction | Section-aware extractor against skills master CSV |
| Skill normalization | Alias mapping via `skill_aliases.json` |
| Profile generation | Structured candidate profile builder |
| JD matching | Keyword overlap matcher |
| Ranking | Descending sort by `match_score` |
| Recruiter dashboard | Live metrics, charts, ranked tables, candidate modal |
| Batch dataset testing | Streaming JSONL ingestion service |

---

## 4. Key Features

### Authentication & Roles
- User registration and login (recruiter or applicant)
- JWT-based session handling
- Role-protected routes on frontend and backend

### Resume Processing
- PDF resume upload (guest flow and authenticated apply flow)
- Automated text extraction, skill detection, and canonicalization
- Structured candidate profile output (skills, summary, experience, education)

### Job Management
- Recruiters post jobs with title, skills, experience level, location, and description
- Applicants browse jobs, view job details, and apply with resume + contact info

### Matching & Ranking
- Candidate–job match score based on skill overlap with job requirements
- Ranked candidate lists per job
- Best-job selection across all jobs (dataset test endpoint)

### Recruiter Dashboard
- Real API-driven metrics (applications, shortlisted, interviewing, avg ATS)
- Pipeline, domain skill, and applications-per-job charts
- Ranked candidate table with detail modal
- Shortlist / reject actions with status updates

### Applicant Portal
- Job browsing and application submission
- My Applications page with friendly status labels and match scores

### Dataset Ingestion
- Streaming JSONL loader for large candidate datasets (memory-safe)
- Test endpoint to match dataset candidates against all jobs in the system

### GitHub Profile Analysis (Optional)
- GitHub URL analysis endpoint
- Optional Gemini API integration when `GEMINI_API_KEY` is configured; falls back to rule-based processing otherwise

---

## 5. System Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Frontend (React + Vite)           │
│   Landing · Auth · Recruiter ·      │
│   Applicant · Guest Upload          │
└──────┬──────────────────────────────┘
       │  REST /api
       ▼
┌─────────────────────────────────────┐
│   Backend API (FastAPI)             │
│   auth · jobs · candidates ·        │
│   dashboards                        │
└──────┬──────────────────────────────┘
       │
       ├──────────────────────────────────┐
       ▼                                  ▼
┌──────────────────┐            ┌──────────────────┐
│  Resume Parser   │            │ JSONL Ingestion  │
│  (Member-1)      │            │ (streaming)      │
└────────┬─────────┘            └────────┬─────────┘
         │                                 │
         ▼                                 ▼
┌──────────────────────────────────────────────────┐
│  Skill Extraction → Canonicalization → Profile   │
└──────────────────────┬───────────────────────────┘
                       ▼
              ┌─────────────────┐
              │  JD Matcher     │
              │  (Member-2)     │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │  Ranker         │
              │  (Member-3)     │
              └────────┬────────┘
                       ▼
              ┌─────────────────┐
              │ SQLite Database │
              │ + Dashboard UI  │
              └─────────────────┘
```

---

## 6. Technology Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React 19 | UI framework |
| Vite 7 | Build tool & dev server |
| React Router 7 | Client-side routing |
| Tailwind CSS 3 | Styling |
| Framer Motion | Page & component animations |
| Recharts | Dashboard & results charts |
| Lucide React | Icons |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework |
| Python 3 | Runtime |
| SQLAlchemy | ORM |
| Pydantic / pydantic-settings | Request/response validation & config |
| bcrypt | Password hashing |
| python-jose | JWT tokens |
| pdfplumber | PDF text extraction |
| pandas | Skills dataset processing |
| httpx | HTTP client (GitHub fetcher) |

### Database
| Technology | Purpose |
|------------|---------|
| SQLite | Local persistence (`talentgraph.db`) |

### Data Assets
| Asset | Location |
|-------|----------|
| Candidate demo JSONL | `backend/app/datasets/candidate_demo.jsonl` |
| Skills master CSV | `backend/app/datasets/skills_master.csv` |
| Skills aliases CSV | `backend/app/datasets/skills_aliases.csv` |
| Section aliases JSON | `backend/app/configs/section_aliases.json` |
| Skill aliases JSON | `backend/app/configs/skill_aliases.json` |
| Candidate JSON schema | `schema/structured_candidate_schema.json` |

---

## 7. Project Workflow

### Candidate / Guest Flow
1. Upload a **PDF resume** on the guest upload page (or apply to a job while signed in).
2. Backend extracts resume text from the PDF.
3. Skills are identified from resume sections using the skills master list.
4. Skills are canonicalized via alias mapping.
5. A structured candidate profile is generated.
6. If a job description is provided, the matcher computes overlap and returns a match score.
7. Results appear on the results dashboard (guest) or in **My Applications** (applicant).

### Recruiter Flow
1. Sign in as a recruiter.
2. **Post a job** with title, skills, experience, location, and description.
3. Applicants apply; each application runs the parse → match pipeline automatically.
4. View **dashboard metrics** and **ranked candidates** per job.
5. Open a candidate detail modal to review skills, scores, and resume summary.
6. **Shortlist** or **reject** candidates; status updates reflect immediately.

### Dataset Test Flow (API)
1. Call `POST /api/candidates/test-dataset` with a JSONL path and record limit.
2. Records are streamed line-by-line (no full-file memory load).
3. Each record is converted to an internal profile and matched against all jobs.
4. Ranked results and best-match summaries are returned.

---

## 8. Matching Approach

TalentGraph uses **rule-based keyword overlap matching** — not embeddings or semantic search.

### How it works (`backend/app/services/jd_matching/matcher.py`)

1. Candidate skills are read from a JSON string: `{"skills": ["python", "react", ...]}`.
2. Job requirements text is lowercased.
3. Each candidate skill is checked as a **substring** of the job requirements.
4. **Match score** = `(matched_skills / total_skills) × 100`.
5. If at least one skill matches but the score is below 30, a floor of **30** is applied.
6. A recommendation label is assigned: `Strong Match` (>75), `Good Match` (>50), or `Weak Match`.

### Ranking (`backend/app/services/jd_matching/ranking.py`)

- Candidates are sorted by `match_score` in descending order.
- A `rank` field (1, 2, 3, …) is assigned after sorting.

This approach is transparent and fast, making it suitable for MVP demos and hackathon evaluation.

---

## 9. Dataset

### Candidate JSONL (`backend/app/datasets/candidate_demo.jsonl`)
- Contains **20 pre-built structured candidate records** for testing.
- Each line is a JSON object with fields such as `candidate_id`, `skills`, `summary_text`, `profile_text`, `education`, and `career_history`.
- Used by the dataset ingestion service and `POST /api/candidates/test-dataset`.

### Skills Master (`backend/app/datasets/skills_master.csv`)
- Master list of known skills used during resume skill extraction.

### Skills Aliases (`backend/app/datasets/skills_aliases.csv`, `backend/app/configs/skill_aliases.json`)
- Maps raw skill names to canonical forms (e.g., `"React.js"` → `react`).

### Section Aliases (`backend/app/configs/section_aliases.json`)
- Maps resume section headings (e.g., "Technical Skills", "Core Competencies") to normalized section types for extraction.

### Candidate Schema (`schema/structured_candidate_schema.json`)
- JSON schema used by offline validation scripts to verify structured profile shape.

---

## 10. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API health / welcome message |
| `/api/auth/register` | POST | Register recruiter or applicant |
| `/api/auth/login` | POST | Login and receive JWT |
| `/api/candidates/resume` | POST | Upload PDF resume, parse, optional JD match |
| `/api/candidates/github` | POST | Analyze GitHub profile |
| `/api/candidates/test-dataset` | POST | Stream JSONL dataset, match & rank (recruiter) |
| `/api/jobs/` | POST | Create job posting (recruiter) |
| `/api/jobs/` | GET | List all job postings |
| `/api/jobs/{job_id}` | GET | Get single job details |
| `/api/jobs/{job_id}/apply` | POST | Submit application with resume (applicant) |
| `/api/dashboards/recruiter/metrics` | GET | Recruiter dashboard metrics & charts data |
| `/api/dashboards/recruiter/jobs/{job_id}/candidates` | GET | Ranked candidates for a job |
| `/api/dashboards/recruiter/applications/{application_id}` | GET | Full candidate application detail |
| `/api/dashboards/recruiter/applications/{application_id}/status` | PATCH | Update application status (shortlist/reject) |
| `/api/dashboards/applicant/status` | GET | Applicant's application list & statuses |

---

## 11. Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### Clone & enter project
```bash
git clone <your-repo-url>
cd final
```

### Backend setup
```bash
# Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Start backend
```bash
# From project root
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### Frontend setup
```bash
cd frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:5173`  
API requests are proxied to `http://localhost:8000/api` via Vite.

### Production build (frontend)
```bash
cd frontend
npm run build
npm run preview
```

---

## 12. Environment Variables

TalentGraph uses environment variables via `backend/app/core/config.py`. There is no root `.env.example`; optional GitHub analyzer keys are documented in `githubhacathon/.env.example`.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | No | `your-secret-key-here` | JWT signing secret |
| `DATABASE_URL` | No | `sqlite:///./talentgraph.db` | SQLAlchemy database URL |
| `GEMINI_API_KEY` | No | — | Optional Gemini key for GitHub analyzer |
| `GITHUB_TOKEN` | No | — | Optional GitHub token for higher API rate limits |

### Frontend
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | `/api` | API base URL (Vite proxy used in dev) |

Example (backend):
```bash
export SECRET_KEY="change-me-in-production"
export DATABASE_URL="sqlite:///./talentgraph.db"
```

---

## 13. Folder Structure

```
final/
├── backend/
│   └── app/
│       ├── api/
│       │   ├── api_router.py          # Route registration
│       │   ├── deps.py                # Auth dependencies
│       │   └── endpoints/
│       │       ├── auth.py
│       │       ├── candidates.py
│       │       ├── jobs.py
│       │       └── dashboards.py
│       ├── core/
│       │   ├── config.py
│       │   └── security.py
│       ├── db/
│       │   ├── models.py
│       │   ├── session.py
│       │   └── migrate.py
│       ├── schemas/
│       │   ├── job.py
│       │   ├── user.py
│       │   └── github_schemas.py
│       ├── services/
│       │   ├── resume_parser/         # Member-1: PDF → profile
│       │   ├── jd_matching/           # Member-2 & 3: match + rank
│       │   ├── dataset_ingestion/     # JSONL streaming ingestion
│       │   ├── application_service.py
│       │   └── github_analyzer/
│       ├── configs/                   # Alias JSON files
│       ├── datasets/                  # JSONL, CSV skill data
│       └── main.py
├── frontend/
│   └── src/
│       ├── pages/                     # Route pages
│       ├── components/                # UI components
│       ├── services/                  # api.js, auth.js
│       ├── routes/                    # AppRoutes, RoleRoute
│       ├── context/                   # Theme, Analysis state
│       └── utils/
├── resume_parser/                     # Standalone/offline parser copy
├── githubhacathon/                    # Legacy GitHub analyzer prototype
├── schema/
│   └── structured_candidate_schema.json
├── validation/
│   └── validate_profiles.py
├── requirements.txt
└── README.md
```

---

## 14. Testing

### Backend import check
```bash
python -c "from backend.app.main import app; print('OK')"
```

### Dataset ingestion smoke test
```bash
python -c "
from backend.app.services.dataset_ingestion import resolve_dataset_path, stream_jsonl_records
path = resolve_dataset_path('backend/app/datasets/candidate_demo.jsonl')
print(len(list(stream_jsonl_records(path, limit=5))), 'records loaded')
"
```

### Resume parser tests (integrated backend copy)
```bash
python -m pytest backend/app/services/resume_parser/tests/ -q
```

### Resume parser tests (standalone copy)
```bash
python -m pytest resume_parser/tests/ -q
```

### Profile schema validation
```bash
python validation/validate_profiles.py --help
```

### API test (dataset endpoint)
Requires a recruiter JWT from `POST /api/auth/login`.

```bash
curl -X POST http://localhost:8000/api/candidates/test-dataset \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"dataset_path": "backend/app/datasets/candidate_demo.jsonl", "limit": 5}'
```

---

## 15. Future Improvements

The following are **not implemented** in the current MVP and are listed as realistic next steps:

- Semantic / embedding-based job–candidate matching
- Vector database for large-scale candidate search
- LLM-powered resume insights and interview question generation
- TF-IDF or weighted skill importance scoring
- Real-time collaborative shortlisting workflows
- Production deployment (PostgreSQL, Docker, CI/CD)
- Email notifications for application status changes

---

## 16. Conclusion

TalentGraph demonstrates a complete recruitment MVP: from PDF resume parsing and skill normalization to job posting, applicant matching, ranked dashboards, and candidate management. Built with React and FastAPI, it gives recruiters a practical starting point for data-driven hiring while keeping the matching logic transparent and explainable.

For hackathon evaluation, the fastest demo path is:
1. Register as recruiter → post a job.
2. Register as applicant → apply with a PDF resume.
3. Return to recruiter dashboard → review ranked candidates and shortlist.

---

**Team:** TalentGraph  
**License:** See repository license file (if applicable).
