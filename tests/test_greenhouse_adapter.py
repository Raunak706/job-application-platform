from src.ingestion import greenhouse_adapter


def test_to_raw_record_uses_generic_contract():
    source = {
        "source_type": "greenhouse",
        "company": "example",
        "company_name": "Example Company",
    }

    job = {
        "id": 123,
        "title": "Data Engineer",
        "absolute_url": "https://example.com/job",
        "first_published": "2026-09-18T00:00:00+00:00",
    }

    record = greenhouse_adapter.to_raw_record(
        job,
        source,
    )

    assert record["source"] == "greenhouse"
    assert record["source_company"] == "Example Company"
    assert record["source_job_id"] == "123"
    assert record["source_url"] == "https://example.com/job"
    assert record["apply_url"] == "https://example.com/job"
    assert record["title"] == "Data Engineer"
    assert record["raw_payload"] == job