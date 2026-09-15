# Security & Authorization Documentation

Member 2 enforces multi-layered security controls across API endpoints, data models, and user workflows.

## Security Controls

### 1. Insecure Direct Object Reference (IDOR) Protection
- Match endpoints (`/api/matches/<id>`) verify that the requesting user owns the associated lost report or holds admin privileges.
- Claim endpoints (`/api/claims/<id>`) verify that the requesting user is the claimant or an administrator.

### 2. Private Answer Leakage Prevention
- Verification questions serialization exposes only `to_public_dict()`, omitting `expected_answer`.
- Claimant templates (`verify.html`) receive public question structures only.
- Privileged expected answer inspection is restricted exclusively to authorized admin routes (`/admin/claims/<id>/review`).

### 3. Database & Input Security
- SQLAlchemy ORM parameterized queries prevent SQL injection.
- Jinja2 auto-escaping prevents Cross-Site Scripting (XSS).
- Werkzeug password hashing (`pbkdf2:sha256`) secures user credentials.
- File upload validation enforces allowed extension whitelisting (`png`, `jpg`, `jpeg`, `webp`) and `secure_filename()` sanitization.

### 4. Audit Logging
- Security-critical operations (Registration, Login, Claim Submission, Verification Answers, Admin Approval/Rejection) are recorded in `AuditLog`.
