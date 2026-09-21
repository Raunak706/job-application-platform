from src.matching.candidate_features import CandidateFeatures
from src.matching.job_features import JobFeatures
from src.matching.scorer import score_evidence_match


def test_score_evidence_match_finds_relevant_experience_and_project():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=("python", "sql", "postgresql"),
        experiences=(
            (
                101,
                "Data Engineer",
                "Built Python and SQL data pipelines.",
            ),
            (
                102,
                "Machine Learning Engineer",
                "Built computer vision models.",
            ),
        ),
        projects=(
            (
                201,
                "Analytics Platform",
                "Built a PostgreSQL analytics workflow.",
            ),
        ),
    )

    job = JobFeatures(
        job_id=10,
        title="data engineer",
        company="example company",
        location=None,
        country=None,
        workplace_type=None,
        employment_type=None,
        department="data",
        description="Build Python, SQL, and PostgreSQL data pipelines.",
    )

    result = score_evidence_match(candidate, job)

    assert result.supporting_experience_ids == (101,)
    assert result.supporting_project_ids == (201,)
    assert result.score > 0.0


def test_score_evidence_match_handles_no_relevant_evidence():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=(),
        experiences=(
            (
                101,
                "Graphic Designer",
                "Created marketing illustrations.",
            ),
        ),
        projects=(),
    )

    job = JobFeatures(
        job_id=11,
        title="data analyst",
        company="example company",
        location=None,
        country=None,
        workplace_type=None,
        employment_type=None,
        department=None,
        description="Analyze SQL datasets and build reports.",
    )

    result = score_evidence_match(candidate, job)

    assert result.supporting_experience_ids == ()
    assert result.supporting_project_ids == ()
    assert result.score == 0.0