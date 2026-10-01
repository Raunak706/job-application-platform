from dataclasses import dataclass

from src.matching.contracts import CandidateJobMatchResult
from src.resume_tailoring.composition import build_evidence_relevance
from src.resume_tailoring.contracts import TailoringInput
from src.resume_tailoring.resume_evidence_relevance import (
    score_resume_evidence,
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

    job_text = getattr(
        tailoring_input.job,
        "description",
        None,
    )

    experience_relevance = _add_resume_relevance(
        relevance=experience_relevance,
        selected_ids=experience_ids,
        skill_links=profile.experience_skills,
        entity_id_getter=lambda link: link.experience_id,
        job_text=job_text,
    )

    project_relevance = _add_resume_relevance(
        relevance=project_relevance,
        selected_ids=project_ids,
        skill_links=profile.project_skills,
        entity_id_getter=lambda link: link.project_id,
        job_text=job_text,
    )

    return FitRelevance(
        experiences=experience_relevance,
        projects=project_relevance,
    )


def _add_resume_relevance(
    *,
    relevance: dict[int, int],
    selected_ids: tuple[int, ...],
    skill_links,
    entity_id_getter,
    job_text: str | None,
) -> dict[int, int]:
    augmented = dict(relevance)

    for entity_id in selected_ids:
        evidence_terms = []

        for link in skill_links:
            if entity_id_getter(link) != entity_id:
                continue

            evidence_terms.extend(
                (
                    link.skill.normalized_name,
                    link.skill.canonical_name,
                    link.usage_description,
                )
            )

        semantic_score = score_resume_evidence(
            job_text=job_text,
            evidence_terms=evidence_terms,
        )

        augmented[entity_id] = (
            augmented.get(entity_id, 0)
            + semantic_score
        )

    return augmented