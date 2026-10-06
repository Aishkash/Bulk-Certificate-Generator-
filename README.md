
# Bulk Certificate Generator

A backend API (FastAPI + PostgreSQL) that takes a CSV of recipient names, generates a PDF certificate for each valid name using one predefined template, and lets the client track progress and download the results. A small React frontend is included.

## Tech stack

- Python, FastAPI
- PostgreSQL (Neon), accessed with SQLAlchemy and plain SQL
- pandas (CSV parsing), ReportLab (PDF generation)
- pytest (tests), React + Vite (frontend)

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

Tables are created automatically on startup.

## Run the application

Backend (from the project root):

```bash
python -m app.main
```

API runs at `http://127.0.0.1:8000`. Interactive docs: `http://127.0.0.1:8000/docs`.

Frontend (second terminal):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Run tests

```bash
python -m pytest -v
```

Tests do not need the database. DB calls are replaced with fakes, and the PDF generator runs for real.

Covered: creating a job, input validation, PDF generation, job status/progress, a single certificate failing without stopping the others, and retrieving/downloading certificates.

## Submit a certificate generation request

`POST /jobs` (multipart/form-data)

| Field | Description |
|---|---|
| `title` | Event or course name |
| `issued_by` | Issuing organisation |
| `issue_date` | `YYYY-MM-DD` |
| `file` | CSV with a `name` column (max 1000 rows) |

Example `recipients.csv`:

```csv
name
Rahul Sharma
Priya Verma
Amit Das
```

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -F "title=Python Bootcamp 2026" \
  -F "issued_by=Acme Academy" \
  -F "issue_date=2026-10-01" \
  -F "file=@recipients.csv"
```

Response (`202 Accepted`, returned immediately):

```json
{
  "job_id": 1,
  "summary": {"total": 3, "valid": 3, "rejected": 0},
  "rejected": []
}
```

`rejected` lists the names that failed validation, each with a reason, for the UI to display.

## Check progress

`GET /jobs/{job_id}`

```json
{
  "summary": {"total": 3, "generated": 2, "failed": 1, "pending": 0},
  "job_id": 1,
  "title": "Python Bootcamp 2026",
  "status": "COMPLETED_WITH_ERRORS",
  "certificates": [
    {"id": 1, "name": "Rahul Sharma", "status": "SUCCESS", "error_message": null},
    {"id": 2, "name": "Priya Verma", "status": "FAILED", "error_message": "..."}
  ]
}
```

- Job status: `PENDING`, `PROCESSING`, `COMPLETED`, `COMPLETED_WITH_ERRORS`
- Certificate status: `PENDING`, `SUCCESS`, `FAILED`

## Retrieve generated certificates

`GET /certificates/{certificate_id}/download` returns the PDF.
It returns `404` if the certificate does not exist or failed to generate.

Take the ids from the `certificates` list in the job status response:

```bash
curl -o rahul.pdf http://127.0.0.1:8000/certificates/1/download
```

## API summary

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/jobs` | Submit a bulk request |
| GET | `/jobs/{job_id}` | Status, summary and per-certificate results |
| GET | `/certificates/{id}/download` | Download one PDF |
| GET | `/health` | Health check |

## Project structure

```
app/
  main.py        routes
  parsing.py     CSV reading and name validation
  database.py    connection, table setup, all SQL
  generator.py   PDF template (ReportLab)
  processor.py   background job loop
tests/           pytest tests
frontend/        React app (form + dashboard)
storage/         generated PDFs (gitignored)
```

## Design decisions

1. **Background processing.** A request can contain many recipients, so generating PDFs inside the request could time out. `POST /jobs` saves the job, schedules the work with FastAPI `BackgroundTasks`, and returns `202` with a `job_id`. The client polls `GET /jobs/{job_id}`. `BackgroundTasks` was chosen because it needs no extra infrastructure (no Redis or worker). Limitation: the task runs inside the server process, so a restart mid-job leaves the remaining certificates `PENDING`. In production I would use Celery or RQ with a persistent queue.

2. **Failure isolation.** Each certificate is generated inside its own `try/except`. If one fails it is marked `FAILED` with the error message and the rest continue. The job ends as `COMPLETED_WITH_ERRORS` if any failed.

3. **Two levels of validation.**
   - File level (rejects the request with `400`): not a readable CSV, no `name` column, no data rows, more than 1000 rows.
   - Row level (never rejects the request): an empty name or a name over 100 characters. These rows are skipped, and returned in the `rejected` list of the `POST /jobs` response so the UI can show them. They are not stored in the database or generated.

4. **Duplicate names are allowed.** Two different people can share a name, and the spec does not ask for duplicate detection, so each row gets its own certificate.

5. **Single fixed template.** The certificate layout is defined in code in `generator.py` (border, recipient name, title, date, issuer). Only one design is supported, as required.

6. **Files named by ID.** PDFs are saved as `storage/{job_id}/{certificate_id}.pdf`. User-provided names are never used in file paths, which avoids path traversal and special-character problems.

7. **Plain SQL.** The queries are short, so SQLAlchemy is used only for the connection and `text()` queries. No ORM models. All SQL lives in `database.py`, so `main.py` has no SQL.

8. **Tests without the database.** DB functions are replaced with fakes so tests run offline. `fetch_certificate` is tested against a temporary in-memory SQLite database.

## Known limitations

- Jobs in progress are lost if the server restarts (see decision 1).
- The default Helvetica font supports Latin characters only. Names in other scripts fail for that certificate and are reported as `FAILED`.
- Rejected entries are returned only in the `POST /jobs` response, so refreshing the dashboard loses that list.
- CSV only (UTF-8), 1000 rows maximum.
- No ZIP download. Certificates are downloaded one by one.