from app.database import get_pending, update_certificate, update_job
from app.generator import create_pdf


def process_job(job_id):
    job, certs = get_pending(job_id)
    update_job(job_id, "PROCESSING")
    failed = 0

    for cert in certs:
        path = f"storage/{job_id}/{cert['id']}.pdf"
        try:
            create_pdf(path, cert["name"], job["title"], job["issued_by"], job["issue_date"])
            update_certificate(cert["id"], job_id, "SUCCESS", file_path=path)
        except Exception as e:
            failed += 1
            update_certificate(cert["id"], job_id, "FAILED", error=str(e))

    update_job(job_id, "COMPLETED_WITH_ERRORS" if failed else "COMPLETED")
