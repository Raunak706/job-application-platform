from src.database.models import Job
from src.matching.job_features import extract_job_features


def test_extract_job_features_normalizes_text_fields():
    job = Job(
        id=10,
        raw_job_posting_id=None,
        title="Data Engineer",
        company="Example Company",
        location="New York, NY",
        country="US",
        workplace_type="Hybrid",
        employment_type="Full Time",
        department="Data",
        description="Build Python and SQL data pipelines.",
        source="test",
        source_job_id="job-10",
        source_url=None,
        apply_url=None,
    )

    result = extract_job_features(job)

    assert result.job_id == 10
    assert result.title == "data engineer"
    assert result.company == "example company"
    assert result.location == "new york, ny"
    assert result.country == "us"
    assert result.workplace_type == "hybrid"
    assert result.employment_type == "full time"
    assert result.department == "data"
    assert result.description == "build python and sql data pipelines."


def test_extract_job_features_handles_optional_fields():
    job = Job(
        id=11,
        raw_job_posting_id=None,
        title="Data Analyst",
        company="Example Company",
        location=None,
        country=None,
        workplace_type=None,
        employment_type=None,
        department=None,
        description=None,
        source="test",
        source_job_id="job-11",
        source_url=None,
        apply_url=None,
    )

    result = extract_job_features(job)

    assert result.job_id == 11
    assert result.title == "data analyst"
    assert result.location is None
    assert result.country is None
    assert result.workplace_type is None
    assert result.employment_type is None
    assert result.department is None
    assert result.description is None