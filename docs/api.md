# REST API Specification

## Match Endpoints

### `GET /api/matches`
Returns paginated list of candidate matches.
- **Query Params**: `confidence` (HIGH/MEDIUM/LOW), `status` (POSSIBLE/CLAIMED/REJECTED), `report_id`, `page`, `per_page`
- **Response**: `200 OK` with matches array and pagination metadata.

### `GET /api/matches/<id>`
Returns detailed match object with score breakdown.
- **Response**: `200 OK` or `403 Forbidden` if IDOR check fails.

### `POST /api/matches/run`
Triggers intelligent matching engine.
- **Body**: `{ "lost_report_id": 1 }` (optional)
- **Response**: `200 OK` with generated match count.

### `POST /api/matches/<id>/refresh`
Re-calculates signal scores for a match pair.

---

## Claim & Verification Endpoints

### `POST /api/claims/submit`
Submits a claim for a match pair.
- **Body**: `{ "match_id": 1, "remarks": "My item" }`
- **Response**: `201 Created` with claim object.

### `GET /api/claims/<id>`
Returns claim status and public verification questions.
- **Response**: `200 OK` with claim details and public question list (expected answers omitted!).

### `POST /api/claims/<id>/verify`
Submits answers to private verification questions.
- **Body**: `{ "answers": { "1": "Student ID for John Doe" } }`
- **Response**: `200 OK` with evaluated verification score and status `UNDER_VERIFICATION`.

---

## Notification Endpoints

### `GET /api/notifications`
Returns user notifications.

### `POST /api/notifications/<id>/read`
Marks a notification as read.
