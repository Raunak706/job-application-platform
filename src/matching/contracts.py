from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CandidateJobMatchResult:
    candidate_id: int
    job_id: int
    matcher_version: str

    overall_score: float

    skill_score: float
    title_relevance_score: float
    evidence_score: float
    compatibility_score: float

    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]

    supporting_experience_ids: tuple[int, ...]
    supporting_project_ids: tuple[int, ...]

    compatibility: tuple[str, ...]
    reasons: tuple[str, ...]
    