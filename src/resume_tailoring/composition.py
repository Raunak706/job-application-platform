from dataclasses import dataclass
from typing import Callable

from src.candidate_profile.contracts import CanonicalCandidateProfile
from src.matching.contracts import CandidateJobMatchResult
from src.resume_tailoring.contracts import TailoringInput


MIN_PROJECT_BULLETS = 2
MAX_PROJECT_BULLETS = 4

MIN_EXPERIENCE_BULLETS = 2
MAX_EXPERIENCE_BULLETS = 4


@dataclass(frozen=True, slots=True)
class ExperienceContentAllocation:
    experience_id: int
    target_bullets: int


@dataclass(frozen=True, slots=True)
class ProjectContentAllocation:
    project_id: int
    target_bullets: int


@dataclass(frozen=True, slots=True)
class ResumeCompositionPlan:
    experiences: tuple[ExperienceContentAllocation, ...]
    projects: tuple[ProjectContentAllocation, ...]


def build_composition_plan_from_profile(
    profile: CanonicalCandidateProfile,
    tailoring_input: TailoringInput,
    match_result: CandidateJobMatchResult,
) -> ResumeCompositionPlan:
    if profile.identity.candidate_id != tailoring_input.candidate_id:
        raise ValueError(
            "Tailoring input candidate does not match candidate profile."
        )

    if match_result.candidate_id != tailoring_input.candidate_id:
        raise ValueError(
            "Match result candidate does not match tailoring input."
        )

    if match_result.job_id != tailoring_input.job.job_id:
        raise ValueError(
            "Match result job does not match tailoring input."
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

    return build_composition_plan(
        experience_ids=experience_ids,
        project_ids=project_ids,
        experience_relevance=experience_relevance,
        project_relevance=project_relevance,
    )


def build_rich_composition_plan(
    tailoring_input: TailoringInput,
) -> ResumeCompositionPlan:
    return ResumeCompositionPlan(
        experiences=tuple(
            ExperienceContentAllocation(
                experience_id=experience.id,
                target_bullets=MAX_EXPERIENCE_BULLETS,
            )
            for experience in tailoring_input.experiences
        ),
        projects=tuple(
            ProjectContentAllocation(
                project_id=project.id,
                target_bullets=MAX_PROJECT_BULLETS,
            )
            for project in tailoring_input.projects
        ),
    )


def build_evidence_relevance(
    *,
    selected_ids: tuple[int, ...],
    skill_links,
    matched_skills: tuple[str, ...],
    entity_id_getter: Callable,
) -> dict[int, int]:
    selected_id_set = set(selected_ids)

    matched_skill_names = {
        skill.casefold()
        for skill in matched_skills
    }

    evidence_skills: dict[int, set[str]] = {
        entity_id: set()
        for entity_id in selected_ids
    }

    for skill_link in skill_links:
        entity_id = entity_id_getter(skill_link)

        if entity_id not in selected_id_set:
            continue

        normalized_name = skill_link.skill.normalized_name.casefold()

        if normalized_name not in matched_skill_names:
            continue

        evidence_skills[entity_id].add(normalized_name)

    return {
        entity_id: len(skill_names)
        for entity_id, skill_names in evidence_skills.items()
    }


def build_composition_plan(
    *,
    experience_ids: tuple[int, ...],
    project_ids: tuple[int, ...],
    experience_relevance: dict[int, int],
    project_relevance: dict[int, int],
) -> ResumeCompositionPlan:
    experience_allocations = _allocate_experiences(
        experience_ids,
        experience_relevance,
    )

    project_allocations = _allocate_projects(
        project_ids,
        project_relevance,
    )

    return ResumeCompositionPlan(
        experiences=experience_allocations,
        projects=project_allocations,
    )


def _allocate_experiences(
    experience_ids: tuple[int, ...],
    relevance: dict[int, int],
) -> tuple[ExperienceContentAllocation, ...]:
    if not experience_ids:
        return ()

    highest_relevance = max(
        relevance.get(experience_id, 0)
        for experience_id in experience_ids
    )

    return tuple(
        ExperienceContentAllocation(
            experience_id=experience_id,
            target_bullets=_target_bullets(
                relevance=relevance.get(experience_id, 0),
                highest_relevance=highest_relevance,
                minimum=MIN_EXPERIENCE_BULLETS,
                maximum=MAX_EXPERIENCE_BULLETS,
            ),
        )
        for experience_id in experience_ids
    )


def _allocate_projects(
    project_ids: tuple[int, ...],
    relevance: dict[int, int],
) -> tuple[ProjectContentAllocation, ...]:
    if not project_ids:
        return ()

    highest_relevance = max(
        relevance.get(project_id, 0)
        for project_id in project_ids
    )

    return tuple(
        ProjectContentAllocation(
            project_id=project_id,
            target_bullets=_target_bullets(
                relevance=relevance.get(project_id, 0),
                highest_relevance=highest_relevance,
                minimum=MIN_PROJECT_BULLETS,
                maximum=MAX_PROJECT_BULLETS,
            ),
        )
        for project_id in project_ids
    )


def _target_bullets(
    *,
    relevance: int,
    highest_relevance: int,
    minimum: int,
    maximum: int,
) -> int:
    if highest_relevance <= 0:
        return minimum

    if relevance == highest_relevance and highest_relevance > 1:
        return maximum

    if relevance >= 3:
        return min(3, maximum)

    return minimum