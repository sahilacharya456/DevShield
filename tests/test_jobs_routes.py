from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api import routes_jobs


def test_enqueue_supply_chain_job(monkeypatch):
    class FakeTaskResult:
        id = "job-123"
        status = "PENDING"

    class FakeTask:
        @staticmethod
        def delay(manifest_name, manifest_content):
            assert manifest_name == "requirements.txt"
            assert manifest_content == "requests==2.25.1"
            return FakeTaskResult()

    monkeypatch.setattr(routes_jobs, "scan_supply_chain_manifest_task", FakeTask)

    app = FastAPI()
    app.include_router(routes_jobs.router)
    client = TestClient(app)

    response = client.post(
        "/scans/supply-chain",
        json={"manifest_name": "requirements.txt", "manifest_content": "requests==2.25.1"},
    )

    assert response.status_code == 200
    assert response.json() == {"job_id": "job-123", "status": "PENDING"}


def test_get_job_status_success(monkeypatch):
    class FakeResult:
        status = "SUCCESS"
        result = {"status": "success"}

        def successful(self):
            return True

        def failed(self):
            return False

    def fake_get_task_result(job_id):
        assert job_id == "job-123"
        return FakeResult()

    monkeypatch.setattr(routes_jobs, "get_task_result", fake_get_task_result)

    app = FastAPI()
    app.include_router(routes_jobs.router)
    client = TestClient(app)

    response = client.get("/job-123")

    assert response.status_code == 200
    assert response.json() == {
        "job_id": "job-123",
        "status": "SUCCESS",
        "result": {"status": "success"},
        "error": None,
    }
