from backend.tests.conftest import upload


# ---------- creating a job ----------
def test_create_job(client):
    r = upload(client, "name\nRahul Sharma\nPriya Verma\n")
    assert r.status_code == 202
    assert r.json()["job_id"] == 1
    assert r.json()["summary"] == {"total": 2, "valid": 2, "rejected": 0}
    assert client.saved["valid"] == ["Rahul Sharma", "Priya Verma"]


def test_duplicate_names_are_allowed(client):
    r = upload(client, "name\nRahul Sharma\nRahul Sharma\n")
    assert r.json()["summary"]["valid"] == 2


# ---------- validation ----------
def test_blank_name_is_rejected_but_job_still_created(client):
    r = upload(client, "name,city\nRahul Sharma,Pune\n,Delhi\n")
    body = r.json()
    assert r.status_code == 202
    assert body["summary"] == {"total": 2, "valid": 1, "rejected": 1}
    assert body["rejected"][0]["error"] == "Name is required"



def test_too_long_name_is_rejected(client):
    r = upload(client, f"name\n{'a' * 101}\n")
    assert r.json()["rejected"][0]["error"].startswith("Name is too long")


def test_missing_name_column_returns_400(client):
    r = upload(client, "email\nrahul@example.com\n")
    assert r.status_code == 400


def test_empty_file_returns_400(client):
    assert upload(client, "").status_code == 400


def test_header_only_file_returns_400(client):
    assert upload(client, "name\n").status_code == 400


def test_missing_form_field_returns_422(client):
    r = client.post("/jobs", data={"title": "x"}, files={"file": ("a.csv", "name\nA\n")})
    assert r.status_code == 422
def test_job_status_summary(client, monkeypatch):
    job = {"id": 1, "title": "Bootcamp", "status": "PROCESSING", "total": 3}
    certs = [
        {"id": 1, "name": "A", "status": "SUCCESS", "error_message": None},
        {"id": 2, "name": "B", "status": "FAILED", "error_message": "boom"},
        {"id": 3, "name": "C", "status": "PENDING", "error_message": None},
    ]
    monkeypatch.setattr("app.main.fetch_job", lambda job_id: (job, certs))

    r = client.get("/jobs/1")
    assert r.status_code == 200
    assert r.json()["summary"] == {"total": 3, "generated": 1, "failed": 1, "pending": 1}
    assert r.json()["status"] == "PROCESSING"


def test_unknown_job_returns_404(client, monkeypatch):
    monkeypatch.setattr("app.main.fetch_job", lambda job_id: None)
    assert client.get("/jobs/999").status_code == 404