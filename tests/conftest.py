import app.database as database

database.init_db = lambda: None  # must happen BEFORE app.main is imported (it calls init_db on import)

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(monkeypatch):
    saved = {}

    def fake_save_job(title, issued_by, issue_date, valid):
        saved["valid"] = valid
        return 1

    monkeypatch.setattr("app.main.save_job", fake_save_job)
    monkeypatch.setattr("app.main.process_job", lambda job_id: None)  # no PDFs in API tests

    c = TestClient(app)
    c.saved = saved
    return c


def upload(client, csv_text, filename="names.csv"):
    return client.post(
        "/jobs",
        data={"title": "Bootcamp", "issued_by": "Acme", "issue_date": "2026-10-01"},
        files={"file": (filename, csv_text, "text/csv")},
    )
