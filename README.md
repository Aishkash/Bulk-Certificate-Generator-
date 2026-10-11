# 🎓 Bulk Certificate Generator

A full-stack web application that automates certificate generation for events, courses, and training programs. Upload a CSV file containing recipient names, provide the certificate details, and generate personalized PDF certificates automatically.

The application uses **FastAPI and PostgreSQL** for the backend, with a **React frontend** for submitting certificate generation requests and tracking progress.

## 🚀 Live Demo

| Component | Link |
|---|---|
| 🌐 Frontend | [Bulk Certificate Generator](https://bulk-certificate-generator-five.vercel.app/) |
| ⚙️ Backend API | [Backend Service](https://bulk-certificate-generator-z488.onrender.com/) |
| 📚 API Documentation | [Interactive API Docs](https://bulk-certificate-generator-z488.onrender.com/docs) |
| ❤️ Health Check | [Backend Health](https://bulk-certificate-generator-z488.onrender.com/health) |

> **Note:** The backend is hosted on Render, so the first request after a period of inactivity may take longer while the service starts.

---

## ✨ Features

- **Bulk Certificate Generation:** Generate personalized PDF certificates for multiple recipients using a single CSV upload.
- **CSV Validation:** Validate uploaded files and recipient names before processing.
- **Automated PDF Generation:** Create certificates using a predefined template with the recipient's name, event title, issue date, and issuing organization.
- **Background Processing:** Process certificate generation tasks asynchronously without keeping the initial request waiting.
- **Real-Time Progress Tracking:** Retrieve job status, generated certificate counts, failed certificates, and pending tasks through the API.
- **Failure Isolation:** Handle individual certificate generation failures without interrupting the remaining certificates.
- **Individual Downloads:** Download successfully generated certificates using their unique IDs.
- **Persistent Job Records:** Store job and certificate information in PostgreSQL.
- **Interactive API Documentation:** Explore and test backend endpoints using FastAPI's Swagger UI.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | React, Vite, JavaScript |
| Database | PostgreSQL, Neon |
| Database Connectivity | SQLAlchemy, psycopg2 |
| Data Processing | Pandas |
| PDF Generation | ReportLab |
| File Uploads | Python Multipart |
| Testing | Pytest |
| Backend Deployment | Render |
| Frontend Deployment | Vercel |
| Version Control | Git, GitHub |

---

## 🏗️ Architecture

The application follows a simple client-server architecture.

```text
                   ┌──────────────────────────┐
                   │       React Frontend     │
                   │          (Vercel)        │
                   └────────────┬─────────────┘
                                │
                                │ HTTP Requests
                                ▼
                   ┌──────────────────────────┐
                   │       FastAPI Backend     │
                   │          (Render)        │
                   └────────────┬─────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
       ┌────────────────────┐     ┌────────────────────┐
       │  PostgreSQL / Neon │     │ BackgroundTasks    │
       │                    │     │                    │
       │ Jobs and Records   │     │ Certificate Jobs   │
       └────────────────────┘     └─────────┬──────────┘
                                            │
                                            ▼
                                 ┌────────────────────┐
                                 │   ReportLab PDF    │
                                 │    Generation      │
                                 └─────────┬──────────┘
                                           │
                                           ▼
                                 ┌────────────────────┐
                                 │ Generated PDF Files│
                                 │      Storage       │
                                 └────────────────────┘
```

### Workflow

1. The user enters the certificate title, issuing organization, and issue date in the frontend.
2. The user uploads a CSV file containing recipient names.
3. The frontend submits the data to the FastAPI backend using a multipart/form-data request.
4. The backend validates the CSV and recipient names.
5. The application creates a job record and schedules certificate generation as a background task.
6. The backend returns a job ID so the client can track the request.
7. The background processor generates a personalized PDF for each valid recipient.
8. Job and certificate statuses are stored in PostgreSQL.
9. The frontend retrieves job progress and allows users to download successfully generated certificates.

---

## 🔌 API Endpoints

**Base URL:**

```text
https://bulk-certificate-generator-z488.onrender.com
```

The following endpoints expose the application's certificate generation and tracking functionality.

| HTTP Method | Endpoint | Functionality | Expected Response |
|---|---|---|---|
| `GET` | `/` | Root endpoint, if configured, for checking basic API availability. | JSON or HTTP response |
| `GET` | `/health` | Health-check endpoint used to verify backend availability. | Health status |
| `POST` | `/jobs` | Upload a CSV and submit a bulk certificate generation job. | `202 Accepted` with job ID and validation summary |
| `GET` | `/jobs/{job_id}` | Retrieve job details, overall progress, certificate statuses, and results. | Job summary and certificate records |
| `GET` | `/certificates/{cert_id}/download` | Download an individual successfully generated certificate as a PDF. | PDF file or `404 Not Found` |

> **Implementation note:** The `/` endpoint is included only if it is defined in the application. The implemented API routes should be treated as the source of truth.

### 1. Health Check

**Request**

```http
GET /health
```

**Live endpoint:**  
https://bulk-certificate-generator-z488.onrender.com/health

Checks whether the backend health endpoint responds successfully.

### 2. Create a Certificate Generation Job

**Request**

```http
POST /jobs
```

**Content-Type:** `multipart/form-data`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `title` | String | Yes | Name of the event, course, or program |
| `issued_by` | String | Yes | Organization issuing the certificate |
| `issue_date` | Date | Yes | Certificate issue date in `YYYY-MM-DD` format |
| `file` | CSV File | Yes | CSV containing a `name` column |

**Example CSV**

```csv
name
Rahul Sharma
Priya Verma
Amit Das
```

**Example request**

```bash
curl -X POST \
  https://bulk-certificate-generator-z488.onrender.com/jobs \
  -F "title=Python Bootcamp 2026" \
  -F "issued_by=Acme Academy" \
  -F "issue_date=2026-10-01" \
  -F "file=@recipients.csv"
```

**Example response**

```json
{
  "job_id": 1,
  "summary": {
    "total": 3,
    "valid": 3,
    "rejected": 0
  },
  "rejected": []
}
```

The response provides the job ID required to retrieve processing status.

### 3. Retrieve Job Status

**Request**

```http
GET /jobs/{job_id}
```

**Example**

```bash
curl https://bulk-certificate-generator-z488.onrender.com/jobs/1
```

**Example response**

```json
{
  "summary": {
    "total": 3,
    "generated": 2,
    "failed": 1,
    "pending": 0
  },
  "job_id": 1,
  "title": "Python Bootcamp 2026",
  "status": "COMPLETED_WITH_ERRORS",
  "certificates": [
    {
      "id": 1,
      "name": "Rahul Sharma",
      "status": "SUCCESS",
      "error_message": null
    },
    {
      "id": 2,
      "name": "Priya Verma",
      "status": "FAILED",
      "error_message": "Certificate generation failed"
    }
  ]
}
```

The response includes the job summary, overall status, and individual certificate results.

**Job statuses**

| Status | Description |
|---|---|
| `PENDING` | The job is waiting to be processed. |
| `PROCESSING` | Certificate generation is in progress. |
| `COMPLETED` | All certificates were generated successfully. |
| `COMPLETED_WITH_ERRORS` | Processing finished, but one or more certificates failed. |

**Certificate statuses**

| Status | Description |
|---|---|
| `PENDING` | The certificate has not been generated yet. |
| `SUCCESS` | The certificate was generated successfully. |
| `FAILED` | Certificate generation failed. |

### 4. Download a Certificate

**Request**

```http
GET /certificates/{cert_id}/download
```

**Example**

```bash
curl -o certificate.pdf \
  https://bulk-certificate-generator-z488.onrender.com/certificates/1/download
```

The endpoint returns the PDF for a successfully generated certificate.

- `200 OK`: Certificate downloaded successfully.
- `404 Not Found`: Certificate does not exist or was not generated successfully.

Use the certificate IDs returned by `GET /jobs/{job_id}`.

---

## 📂 Project Structure

```text
Bulk-Certificate-Generator/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── generator.py
│   │   ├── parsing.py
│   │   └── processor.py
│   │
│   ├── storage/
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
```

> This structure reflects the backend/frontend separation. Adjust individual entries if your actual repository differs.

---

## ⚙️ Local Setup

### Prerequisites

Install the following:

- Python 3.10 or later
- Node.js and npm
- PostgreSQL database or a Neon PostgreSQL connection
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Aishkash/Bulk-Certificate-Generator-.git
cd Bulk-Certificate-Generator-
```

If your GitHub repository uses a different URL, replace the clone URL with your repository's actual URL.

### 2. Configure the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment.

**macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the backend directory.

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

Replace the placeholders with your PostgreSQL connection details.

**Important:** Never commit your `.env` file or expose database credentials in your repository.

### 4. Start the Backend

From the `backend` directory, run:

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Start the Frontend

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the local frontend URL displayed by Vite, usually:

```text
http://localhost:5173
```

Ensure the frontend API configuration points to the local backend during development and the deployed backend in production.

---

## 🧪 Testing

Run the backend tests from the backend directory with the virtual environment activated:

```bash
pytest -v
```

The test suite covers:

- Job creation and input validation
- CSV parsing and recipient validation
- PDF generation
- Job status and progress tracking
- Failure isolation during certificate generation
- Certificate retrieval and downloads

Database operations are mocked where appropriate so that the relevant tests can run without a live database.

---

## 🧠 Design Decisions

### 1. Background Processing

Certificate generation is scheduled using FastAPI `BackgroundTasks`. This allows the API to return a job ID without waiting for every PDF to finish generating.

The client can then poll the job status endpoint.

**Trade-off:** Background tasks run inside the application process. If the server restarts during processing, unfinished work may not resume automatically.

### 2. Failure Isolation

Each certificate is processed independently. If one certificate fails, the application records the failure and continues processing the remaining recipients.

This prevents a single invalid record from stopping the entire batch.

### 3. Input Validation

Validation occurs at two levels:

- **File-level validation:** Rejects unreadable CSV files, missing `name` columns, empty datasets, and files exceeding the configured row limit.
- **Row-level validation:** Rejects invalid recipient names while allowing valid recipients to continue through the pipeline.

Rejected records are returned in the job creation response.

### 4. Database Design

PostgreSQL stores job information and individual certificate records. SQLAlchemy provides database connectivity, while SQL queries are kept in the database module.

This separates database operations from API route handling.

### 5. Safe File Naming

Generated certificates use job and certificate IDs rather than user-provided names in their file paths.

This avoids problems involving special characters and unsafe file paths.

### 6. Single Certificate Template

The PDF layout is defined in the certificate generator module. Each certificate includes the recipient's name, event title, issue date, and issuing organization.

The current implementation uses one predefined template.

---


## Future Improvements

- Add ZIP downloads for all certificates belonging to a job.
- Introduce a persistent task queue using Celery or RQ.
- Add support for multiple certificate templates.
- Support additional languages and Unicode fonts.
- Persist rejected recipient records for later review.
- Add authentication and authorization.
- Add retry mechanisms for failed certificate generation.
- Improve frontend progress updates and error handling.

---

## Author

**Aishwarya Kashyap**

- GitHub: [Aishkash](https://github.com/Aishkash)
- Live Frontend: [Bulk Certificate Generator](https://bulk-certificate-generator-five.vercel.app/)
- Backend API: [FastAPI Service](https://bulk-certificate-generator-z488.onrender.com/)

---

## License

Add a license if you intend to distribute or reuse this project publicly.