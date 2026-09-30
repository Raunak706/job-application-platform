from dataclasses import dataclass

from src.resume_tailoring.composition import (
    build_evidence_relevance,
)
from src.resume_tailoring.contracts import (
    TailoringInput,
)
from src.matching.contracts import (
    CandidateJobMatchResult,
)


@dataclass(frozen=True, slots=True)
class FitRelevance:
    experiences: dict[int, int]
    projects: dict[int, int]


def build_fit_relevance(
    *,
    profile,
    tailoring_input: TailoringInput,
    match_result: CandidateJobMatchResult,
) -> FitRelevance:
    if match_result.candidate_id != tailoring_input.candidate_id:
        raise ValueError(
            "Match result candidate does not match "
            "tailoring input."
        )

    if match_result.job_id != tailoring_input.job.job_id:
        raise ValueError(
            "Match result job does not match "
            "tailoring input."
        )

    experience_ids = tuple(
        experience.id
        for experience in tailoring_input.experiences
    )

    project_ids = tuple(
        project.id
        for project in tailoring_input.projects
    )

    experience_relevance = build_evidence_relevance(
        selected_ids=experience_ids,
        skill_links=profile.experience_skills,
        matched_skills=match_result.matched_skills,
        entity_id_getter=lambda link: link.experience_id,
    )

    project_relevance = build_evidence_relevance(
        selected_ids=project_ids,
        skill_links=profile.project_skills,
        matched_skills=match_result.matched_skills,
        entity_id_getter=lambda link: link.project_id,
    )

    return FitRelevance(
        experiences=experience_relevance,
        projects=project_relevance,
    )