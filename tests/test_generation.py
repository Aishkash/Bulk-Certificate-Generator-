from app import processor
from app.generator import create_pdf


# ---------- certificate generation ----------
def test_create_pdf(tmp_path):
    path = tmp_path / "cert.pdf"
    create_pdf(str(path), "Rahul Sharma", "Bootcamp", "Acme", "2026-10-01")
    assert path.exists()
    assert path.read_bytes().startswith(b"%PDF")


# ---------- individual failure ----------
def run_job(monkeypatch, names, fail_name=None):
    statuses, results = [], []
    job = {"title": "Bootcamp", "issued_by": "Acme", "issue_date": "2026-10-01"}
    certs = [{"id": i, "name": n} for i, n in enumerate(names, 1)]

    monkeypatch.setattr(processor, "get_pending", lambda job_id: (job, certs))
    monkeypatch.setattr(processor, "update_job", lambda job_id, status: statuses.append(status))
    monkeypatch.setattr(
        processor, "update_certificate",
        lambda cert_id, job_id, status, file_path=None, error=None: results.append((cert_id, status, error)),
    )

    def fake_pdf(path, name, *args):
        if name == fail_name:
            raise ValueError("bad font")

    monkeypatch.setattr(processor, "create_pdf", fake_pdf)

    processor.process_job(1)
    return statuses, results


def test_all_succeed(monkeypatch):
    statuses, results = run_job(monkeypatch, ["A", "B", "C"])
    assert [r[1] for r in results] == ["SUCCESS", "SUCCESS", "SUCCESS"]
    assert statuses == ["PROCESSING", "COMPLETED"]


def test_one_failure_does_not_stop_others(monkeypatch):
    statuses, results = run_job(monkeypatch, ["A", "B", "C"], fail_name="B")
    assert [r[1] for r in results] == ["SUCCESS", "FAILED", "SUCCESS"]
    assert results[1][2] == "bad font"
    assert statuses[-1] == "COMPLETED_WITH_ERRORS"
