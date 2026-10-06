import uvicorn
from datetime import date

from fastapi.responses import FileResponse
from app.database import fetch_certificate, fetch_job, init_db, save_job


from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.parsing import ParseError, read_names, validate_names
from app.processor import process_job

init_db()

app = FastAPI(title="Bulk Certificate Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/jobs", status_code=202)
def create_job(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    issued_by: str = Form(...),
    issue_date: date = Form(...),
    file: UploadFile = File(...),
):
    try:
        names = read_names(file.file)
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))

    valid, rejected = validate_names(names)
    job_id = save_job(title, issued_by, issue_date, valid)
    background_tasks.add_task(process_job, job_id)

    return {
        "job_id": job_id,
        "summary": {"total": len(names), "valid": len(valid), "rejected": len(rejected)},
        "rejected": rejected,  # the UI shows these
    }
@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    result = fetch_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")

    job, certs = result
    generated = sum(1 for c in certs if c["status"] == "SUCCESS")
    failed = sum(1 for c in certs if c["status"] == "FAILED")

    return {
        "summary": {
            "total": job["total"],
            "generated": generated,
            "failed": failed,
            "pending": job["total"] - generated - failed,
        },
        "job_id": job["id"],
        "title": job["title"],
        "status": job["status"],
        "certificates": certs,
    }
@app.get("/certificates/{cert_id}/download")
def download_certificate(cert_id: int):
    cert = fetch_certificate(cert_id)
    if not cert or cert["status"] != "SUCCESS":
        raise HTTPException(status_code=404, detail="Certificate not available")
    return FileResponse(cert["file_path"], media_type="application/pdf",
                        filename=f"{cert['name']}.pdf")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)