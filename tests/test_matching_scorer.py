from src.matching.candidate_features import CandidateFeatures
from src.matching.job_features import JobFeatures
from src.matching.scorer import score_skill_match


def test_score_skill_match_finds_skills_in_job_text():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=("data pipelines", "python", "sql", "postgresql"),
        experiences=(),
        projects=(),
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
        description=(
            "Build production data pipelines using Python, SQL, "
            "and PostgreSQL."
        ),
    )

    result = score_skill_match(candidate, job)

    assert result.matched_skills == (
        "data pipelines",
        "postgresql",
        "python",
        "sql",
    )
    assert result.missing_skills == ()
    assert result.score == 1.0


def test_score_skill_match_does_not_use_partial_word_matches():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=("r", "sql"),
        experiences=(),
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
        description="Prepare reports and analyze business requirements.",
    )

    result = score_skill_match(candidate, job)

    assert result.matched_skills == ()
    assert result.missing_skills == ()
    assert result.score == 0.0


def test_score_skill_match_handles_missing_job_description():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=("python", "sql"),
        experiences=(),
        projects=(),
    )

    job = JobFeatures(
        job_id=12,
        title="software engineer",
        company="example company",
        location=None,
        country=None,
        workplace_type=None,
        employment_type=None,
        department=None,
        description=None,
    )

    result = score_skill_match(candidate, job)

    assert result.matched_skills == ()
    assert result.missing_skills == ()
    assert result.score == 0.0