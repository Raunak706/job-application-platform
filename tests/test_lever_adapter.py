from src.ingestion import lever_adapter


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, url, params, timeout):
        self.calls.append(
            {
                "url": url,
                "params": params,
                "timeout": timeout,
            }
        )
        return FakeResponse(self.responses.pop(0))


def test_fetch_jobs_paginates_until_short_page(monkeypatch):
    first_page = [
        {"id": str(index)}
        for index in range(100)
    ]
    second_page = [
        {"id": "100"},
        {"id": "101"},
    ]

    fake_session = FakeSession(
        [
            first_page,
            second_page,
        ]
    )

    monkeypatch.setattr(
        lever_adapter,
        "create_retry_session",
        lambda: fake_session,
    )

    jobs = lever_adapter.fetch_jobs(
        company="example",
        page_size=100,
    )

    assert len(jobs) == 102

    assert fake_session.calls[0]["params"] == {
        "mode": "json",
        "skip": 0,
        "limit": 100,
    }

    assert fake_session.calls[1]["params"] == {
        "mode": "json",
        "skip": 100,
        "limit": 100,
    }


def test_to_raw_record_uses_generic_contract():
    source = {
        "source_type": "lever",
        "company": "example",
        "company_name": "Example Company",
    }

    job = {
        "id": "job-123",
        "text": "Software Engineer",
        "hostedUrl": "https://example.com/job",
        "applyUrl": "https://example.com/apply",
        "createdAt": 0,
    }

    record = lever_adapter.to_raw_record(
        job,
        source,
    )

    assert record["source"] == "lever"
    assert record["source_company"] == "Example Company"
    assert record["source_job_id"] == "job-123"
    assert record["source_url"] == "https://example.com/job"
    assert record["apply_url"] == "https://example.com/apply"
    assert record["title"] == "Software Engineer"
    assert record["raw_payload"] == job