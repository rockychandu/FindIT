# FindIT - College Lost & Found Management System

FindIT is a professional, secure, and production-ready **College Lost & Found Management System** built with **Python, Flask, SQLite (SQLAlchemy ORM), HTML, Vanilla CSS, and JavaScript**.

The system connects students, faculty, staff, and campus security authorities through a single, authoritative source-of-truth database for reporting lost/found items, computing local deterministic matches, performing private verification, processing claim approvals, and executing physical item handovers with immutable audit logging.

---

## 🌟 Key Features

1. **Authentication & Role-Based Access Control**:
   - Student, Staff, and College Authority (Admin) accounts with Werkzeug password hashing.
   - Server-side access enforcement (`@login_required`, `@admin_required`).

2. **Lost & Found Reporting**:
   - Structured forms with system-generated public report IDs (e.g. `LF-2026-000001`).
   - Image upload validation (type, extension whitelist, max 5MB size limit, UUID renaming).
   - Secret **Private Verification Questions & Answers** setup during lost item reporting (answers are strictly hidden from public view/APIs).

3. **Local Algorithmic Matching Engine (No External API Keys)**:
   - 100% local calculation of text similarity (TF-IDF vectorizer + cosine similarity), category scoring, location fuzzy overlap, and date/time decay formulas.
   - Automated candidate ranking and real-time internal notification alerts for potential matches above threshold (>= 30%).

4. **Private Verification & Claims Workflow**:
   - Claimants must answer the private questions set by the lost item owner.
   - Engine calculates similarity between claimant responses and hidden expected answers.
   - Side-by-side audit view for college authorities to review answers and make informed approval or rejection decisions.

5. **Physical Handover & State Machine**:
   - Valid state transitions (`REPORTED_LOST`/`FOUND` -> `POSSIBLE_MATCH` -> `CLAIM_SUBMITTED` -> `UNDER_VERIFICATION` -> `CLAIM_APPROVED`/`REJECTED` -> `HANDOVER_PENDING` -> `RETURNED` -> `CLOSED`).
   - Admin logs physical ID check notes and records physical item return.

6. **Audit Trail**:
   - Immutable security and action log tracking system events, user logins, report creations, claim decisions, and handovers.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- `pip`

### 2. Installation & Setup

1. Clone or navigate to the repository directory:
   ```bash
   cd FindIT
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Seed the database (Seeds standard categories and default admin/student accounts):
   ```bash
   python seeds.py
   ```

### 3. Running the Application

Launch the Flask development server:
```bash
python run.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

#### Demo Accounts:
- **Admin**: `admin@college.edu` / Password: `AdminPass123!`
- **Student**: `student@college.edu` / Password: `StudentPass123!`

---

## 🧪 Running Automated Tests

Run the Pytest suite covering Auth, Reports, Matching, Claims, Handover, Security, and full E2E workflow:
```bash
pytest -v
```

---

## 📁 Architecture Overview

```text
FindIT/
├── app/
│   ├── models/ (User, ItemReport, ItemImage, Category, Match, Claim, VerificationQuestion, VerificationResponse, Handover, Notification, AuditLog)
│   ├── matching/ (Local TF-IDF & weighted similarity engine)
│   ├── services/ (Auth, Item, Claim, Matching, Audit services)
│   ├── validators/ (Form input & file upload validators)
│   ├── auth/ (Session decorators & access control)
│   ├── routes/ (Auth, Main, Item, Claim, and Admin routes)
│   └── utils/ (ID generator, File upload security)
├── static/
│   ├── css/ (style.css - FindIT design system)
│   ├── js/ (main.js - Dynamic verification builder & image preview)
│   └── images/
├── templates/ (Jinja2 layout and view templates)
├── tests/ (Pytest test suite: unit, security, and end-to-end integration tests)
├── uploads/ (Uploaded item photographs storage)
├── config.py
├── run.py
├── seeds.py
└── requirements.txt
```
