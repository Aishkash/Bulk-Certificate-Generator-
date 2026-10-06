import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(override=True)  # .env wins over any shell variable

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def init_db():
    """Base setup: creates the tables if they don't exist."""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                issued_by TEXT NOT NULL,
                issue_date DATE NOT NULL,
                status TEXT DEFAULT 'PENDING',
                total INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS certificates (
                id SERIAL PRIMARY KEY,
                job_id INTEGER NOT NULL REFERENCES jobs(id),
                name TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                file_path TEXT,
                error_message TEXT
            )
        """))

def save_job(title, issued_by, issue_date, valid, rejected):
    """Insert a job plus one certificate row per name. Returns the job id."""
    with engine.begin() as conn:
        job_id = conn.execute(
            text("""INSERT INTO jobs (title, issued_by, issue_date, total, failed_count)
                    VALUES (:title, :issued_by, :issue_date, :total, :failed)
                    RETURNING id"""),
            {"title": title, "issued_by": issued_by, "issue_date": issue_date,
             "total": len(valid) + len(rejected), "failed": len(rejected)},
        ).scalar()

        if valid:
            conn.execute(
                text("INSERT INTO certificates (job_id, name, status) "
                     "VALUES (:job_id, :name, 'PENDING')"),
                [{"job_id": job_id, "name": n} for n in valid],
            )
        if rejected:
            conn.execute(
                text("INSERT INTO certificates (job_id, name, status, error_message) "
                     "VALUES (:job_id, :name, 'FAILED', :error)"),
                [{"job_id": job_id, "name": r["name"], "error": r["error"]} for r in rejected],
            )
    return job_id


def fetch_job(job_id):
    """Returns (job, certificates), or None if the job doesn't exist."""
    with engine.connect() as conn:
        job = conn.execute(
            text("SELECT * FROM jobs WHERE id = :id"), {"id": job_id}
        ).mappings().first()
        if not job:
            return None
        certs = conn.execute(
            text("SELECT id, name, status, error_message FROM certificates "
                 "WHERE job_id = :id ORDER BY id"),
            {"id": job_id},
        ).mappings().all()
    return dict(job), [dict(c) for c in certs]