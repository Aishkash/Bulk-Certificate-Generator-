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

def save_job(title, issued_by, issue_date, valid):
    """Insert a job plus one PENDING certificate per valid name. Returns the job id."""
    with engine.begin() as conn:
        job_id = conn.execute(
            text("""INSERT INTO jobs (title, issued_by, issue_date, total)
                    VALUES (:title, :issued_by, :issue_date, :total)
                    RETURNING id"""),
            {"title": title, "issued_by": issued_by,
             "issue_date": issue_date, "total": len(valid)},
        ).scalar()

        if valid:
            conn.execute(
                text("INSERT INTO certificates (job_id, name, status) "
                     "VALUES (:job_id, :name, 'PENDING')"),
                [{"job_id": job_id, "name": n} for n in valid],
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

def get_pending(job_id):
    """Job details plus certificates still waiting to be generated."""
    with engine.connect() as conn:
        job = conn.execute(
            text("SELECT * FROM jobs WHERE id = :id"), {"id": job_id}
        ).mappings().first()
        certs = conn.execute(
            text("SELECT id, name FROM certificates "
                 "WHERE job_id = :id AND status = 'PENDING' ORDER BY id"),
            {"id": job_id},
        ).mappings().all()
    return dict(job), [dict(c) for c in certs]


def update_job(job_id, status):
    with engine.begin() as conn:
        conn.execute(text("UPDATE jobs SET status = :s WHERE id = :id"),
                     {"s": status, "id": job_id})


def update_certificate(cert_id, job_id, status, file_path=None, error=None):
    """Update one certificate and keep the job's counters in sync."""
    column = "success_count" if status == "SUCCESS" else "failed_count"
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE certificates SET status = :s, file_path = :f, "
                 "error_message = :e WHERE id = :id"),
            {"s": status, "f": file_path, "e": error, "id": cert_id},
        )
        conn.execute(
            text(f"UPDATE jobs SET {column} = {column} + 1 WHERE id = :id"),
            {"id": job_id},
        )
def fetch_certificate(cert_id):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, name, status, file_path FROM certificates WHERE id = :id"),
            {"id": cert_id},
        ).mappings().first()
    return dict(row) if row else None