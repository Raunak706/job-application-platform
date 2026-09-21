from src.matching.candidate_features import CandidateFeatures
from src.matching.job_features import JobFeatures
from src.matching.scorer import score_compatibility


def test_score_compatibility_reports_unknown_without_candidate_preferences():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=(),
        experiences=(),
        projects=(),
    )

    job = JobFeatures(
        job_id=10,
        title="data analyst",
        company="example company",
        location="new york, ny",
        country="us",
        workplace_type="hybrid",
        employment_type="full_time",
        department=None,
        description=None,
    )

    result = score_compatibility(candidate, job)

    assert result.score == 0.0
    assert result.statuses == (
        "location:unknown",
        "workplace:unknown",
        "employment_type:unknown",
    )


def test_score_compatibility_handles_missing_job_fields():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=(),
        experiences=(),
        projects=(),
    )

    job = JobFeatures(
        job_id=11,
        title="data scientist",
        company="example company",
        location=None,
        country=None,
        workplace_type=None,
        employment_type=None,
        department=None,
        description=None,
    )

    result = score_compatibility(candidate, job)

    assert result.score == 0.0
    assert result.statuses == (
        "location:unknown",
        "workplace:unknown",
        "employment_type:unknown",
    )

def test_score_compatibility_uses_candidate_preferences():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=(),
        experiences=(),
        projects=(),
        current_location="new brunswick, nj",
        current_country="us",
        preferences=(
            (
                "workplace",
                "workplace_types",
                {
                    "values": ["remote", "hybrid"],
                },
                "high",
            ),
            (
                "employment",
                "employment_types",
                {
                    "values": ["full_time"],
                },
                "high",
            ),
        ),
    )

    job = JobFeatures(
        job_id=12,
        title="data analyst",
        company="example company",
        location="new york, ny",
        country="us",
        workplace_type="hybrid",
        employment_type="full_time",
        department=None,
        description=None,
    )

    result = score_compatibility(candidate, job)

    assert result.score == 1.0
    assert result.statuses == (
        "location:compatible",
        "workplace:compatible",
        "employment_type:compatible",
    )
