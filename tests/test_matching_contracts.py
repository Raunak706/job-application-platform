from dataclasses import FrozenInstanceError

import pytest

from src.matching.contracts import CandidateJobMatchResult


def test_candidate_job_match_result_stores_structured_match_data():
    result = CandidateJobMatchResult(
        candidate_id=1,
        job_id=10,
        matcher_version="v1",
        overall_score=0.75,
        skill_score=0.8,
        title_relevance_score=0.7,
        evidence_score=0.75,
        compatibility_score=0.75,
        matched_skills=("Python", "SQL"),
        missing_skills=("Spark",),
        supporting_experience_ids=(101,),
        supporting_project_ids=(201,),
        compatibility=("workplace:compatible", "location:unknown"),
        reasons=("Matched Python and SQL.",),
    )

    assert result.candidate_id == 1
    assert result.job_id == 10
    assert result.matcher_version == "v1"
    assert result.overall_score == 0.75
    assert result.matched_skills == ("Python", "SQL")
    assert result.missing_skills == ("Spark",)
    assert result.supporting_experience_ids == (101,)
    assert result.supporting_project_ids == (201,)


def test_candidate_job_match_result_is_immutable():
    result = CandidateJobMatchResult(
        candidate_id=1,
        job_id=10,
        matcher_version="v1",
        overall_score=0.0,
        skill_score=0.0,
        title_relevance_score=0.0,
        evidence_score=0.0,
        compatibility_score=0.0,
        matched_skills=(),
        missing_skills=(),
        supporting_experience_ids=(),
        supporting_project_ids=(),
        compatibility=(),
        reasons=(),
    )

    with pytest.raises(FrozenInstanceError):
        result.overall_score = 1.0