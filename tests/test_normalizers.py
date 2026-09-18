from src.database.models import RawJobPosting
from src.normalization.greenhouse_normalizer import normalize_greenhouse_job
from src.normalization.lever_normalizer import normalize_lever_job


EXPECTED_FIELDS = {
    "raw_job_posting_id",
    "title",
    "company",
    "location",
    "country",
    "workplace_type",
    "employment_type",
    "department",
    "description",
    "source",
    "source_job_id",
    "source_url",
    "apply_url",
}


def test_lever_normalizer_returns_shared_contract():
    raw_job = RawJobPosting(
        id=1,
        source="lever",
        source_company="Example Company",
        source_job_id="lever-123",
        source_url="https://example.com/job",
        apply_url="https://example.com/apply",
        raw_payload={
            "text": "Software Engineer",
            "country": "US",
            "workplaceType": "hybrid",
            "descriptionPlain": "Example description",
            "categories": {
                "location": "New York, NY",
                "commitment": "Full time",
                "team": "Engineering",
            },
        },
    )

    result = normalize_lever_job(raw_job)

    assert set(result) == EXPECTED_FIELDS
    assert result["title"] == "Software Engineer"
    assert result["company"] == "Example Company"
    assert result["source"] == "lever"


def test_greenhouse_normalizer_returns_shared_contract():
    raw_job = RawJobPosting(
        id=2,
        source="greenhouse",
        source_company="Example Company",
        source_job_id="greenhouse-123",
        source_url="https://example.com/job",
        apply_url="https://example.com/job",
        raw_payload={
            "title": "Data Engineer",
            "location": {
                "name": "London, UK",
            },
            "metadata": [
                {
                    "name": "Location Type",
                    "value": "Hybrid",
                }
            ],
            "departments": [
                {
                    "name": "Data",
                }
            ],
            "content": "&lt;p&gt;Data &amp;amp; Analytics&lt;/p&gt;",
        },
    )

    result = normalize_greenhouse_job(raw_job)

    assert set(result) == EXPECTED_FIELDS
    assert result["title"] == "Data Engineer"
    assert result["company"] == "Example Company"
    assert result["source"] == "greenhouse"
    assert result["description"] == "Data & Analytics"


def test_normalizers_return_same_contract():
    lever_raw_job = RawJobPosting(
        id=1,
        source="lever",
        source_company="Lever Company",
        source_job_id="1",
        raw_payload={
            "text": "Software Engineer",
        },
    )

    greenhouse_raw_job = RawJobPosting(
        id=2,
        source="greenhouse",
        source_company="Greenhouse Company",
        source_job_id="2",
        raw_payload={
            "title": "Software Engineer",
        },
    )

    lever_result = normalize_lever_job(lever_raw_job)
    greenhouse_result = normalize_greenhouse_job(greenhouse_raw_job)

    assert set(lever_result) == set(greenhouse_result)
    assert set(lever_result) == EXPECTED_FIELDS