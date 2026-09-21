from src.matching.candidate_features import CandidateFeatures
from src.matching.job_features import JobFeatures
from src.matching.scorer import score_title_relevance


def test_score_title_relevance_matches_related_data_roles():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=(),
        experiences=(
            (
                101,
                "Machine Learning Engineer",
                "Built data pipelines and machine learning models.",
            ),
            (
                102,
                "Artificial Intelligence Intern",
                "Built NLP and computer vision systems.",
            ),
        ),
        projects=(),
    )

    job = JobFeatures(
        job_id=10,
        title="data scientist",
        company="example company",
        location=None,
        country=None,
        workplace_type=None,
        employment_type=None,
        department=None,
        description=None,
    )

    result = score_title_relevance(candidate, job)

    assert result.score > 0.0
    assert result.supporting_experience_ids == (101,)


def test_score_title_relevance_is_zero_for_unrelated_role():
    candidate = CandidateFeatures(
        candidate_id=1,
        skills=(),
        experiences=(
            (
                101,
                "Machine Learning Engineer",
                "Built machine learning systems.",
            ),
        ),
        projects=(),
    )

    job = JobFeatures(
        job_id=11,
        title="graphic designer",
        company="example company",
        location=None,
        country=None,
        workplace_type=None,
        employment_type=None,
        department=None,
        description=None,
    )

    result = score_title_relevance(candidate, job)

    assert result.score == 0.0
    assert result.supporting_experience_ids == ()