import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

import backend.app.database as database
from backend.app.database import fetch_certificate


# ---------- fetch_certificate (real SQL, temporary SQLite DB) ----------
@pytest.fixture
def fake_db(monkeypatch):
    engine = create_engine("sqlite://", poolclass=StaticPool)  # in-memory, one shared connection
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE certificates (
                id INTEGER PRIMARY KEY,
                job_id INTEGER,
                name TEXT,
                status TEXT,
                file_path TEXT,
                error_message TEXT
            )
        """))
        conn.execute(text(
            "INSERT INTO certificates (id, job_id, name, status, file_path) "
            "VALUES (1, 1, 'Rahul Sharma', 'SUCCESS', 'storage/1/1.pdf')"
        ))
    monkeypatch.setattr(database, "engine", engine)


def test_fetch_certificate_found(fake_db):
    cert = fetch_certificate(1)
    assert cert == {
        "id": 1,
        "name": "Rahul Sharma",
        "status": "SUCCESS",
        "file_path": "storage/1/1.pdf",
    }


def test_fetch_certificate_not_found(fake_db):
    assert fetch_certificate(999) is None


# ---------- download endpoint ----------
def test_download_certificate(client, monkeypatch, tmp_path):
    pdf = tmp_path / "cert.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake pdf content")
    cert = {"id": 1, "name": "Rahul Sharma", "status": "SUCCESS", "file_path": str(pdf)}
    monkeypatch.setattr("app.main.fetch_certificate", lambda cert_id: cert)

    r = client.get("/certificates/1/download")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")


def test_download_unknown_certificate_returns_404(client, monkeypatch):
    monkeypatch.setattr("app.main.fetch_certificate", lambda cert_id: None)
    assert client.get("/certificates/999/download").status_code == 404


def test_download_failed_certificate_returns_404(client, monkeypatch):
    cert = {"id": 2, "name": "Amit", "status": "FAILED", "file_path": None}
    monkeypatch.setattr("app.main.fetch_certificate", lambda cert_id: cert)
    assert client.get("/certificates/2/download").status_code == 404