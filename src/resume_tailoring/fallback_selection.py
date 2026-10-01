from dataclasses import replace

from src.candidate_profile.contracts import CanonicalCandidateProfile
from src.matching.contracts import CandidateJobMatchResult
from src.resume_tailoring.contracts import TailoringInput
from src.resume_tailoring.resume_evidence_relevance import (
    score_resume_evidence,
)
from src.resume_tailoring.selector import (
    ALLOWED_RESUME_VISIBILITIES,
    APPROVED_VERIFICATION_STATUSES,
)


def add_next_fallback_evidence(
    *,
    profile: CanonicalCandidateProfile,
    tailoring_input: TailoringInput,
    match_result: CandidateJobMatchResult,
) -> TailoringInput:
    _validate_inputs(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
    )

    matched_skills = {
        skill.casefold()
        for skill in match_result.matched_skills
    }

    selected_project_ids = {
        project.id
        for project in tailoring_input.projects
    }

    project = _select_next_project(
        profile=profile,
        selected_project_ids=selected_project_ids,
        matched_skills=matched_skills,
        job_text=tailoring_input.job.description,
    )

    if project is not None:
        added_project_skills = tuple(
            project_skill
            for project_skill in profile.project_skills
            if project_skill.project_id == project.id
        )

        return replace(
            tailoring_input,
            projects=tailoring_input.projects + (project,),
            project_skills=(
                tailoring_input.project_skills
                + added_project_skills
            ),
        )

    selected_experience_ids = {
        experience.id
        for experience in tailoring_input.experiences
    }

    experience = _select_next_experience(
        profile=profile,
        selected_experience_ids=selected_experience_ids,
        matched_skills=matched_skills,
        job_text=tailoring_input.job.description,
    )

    if experience is not None:
        added_experience_skills = tuple(
            experience_skill
            for experience_skill in profile.experience_skills
            if experience_skill.experience_id == experience.id
        )

        return replace(
            tailoring_input,
            experiences=(
                tailoring_input.experiences
                + (experience,)
            ),
            experience_skills=(
                tailoring_input.experience_skills
                + added_experience_skills
            ),
        )

    return tailoring_input


def _select_next_project(
    *,
    profile: CanonicalCandidateProfile,
    selected_project_ids: set[int],
    matched_skills: set[str],
    job_text: str | None,
):
    eligible_projects = tuple(
        project
        for project in profile.projects
        if project.id not in selected_project_ids
        and _is_allowed_fact(
            project.verification_status,
            project.visibility,
        )
    )

    if not eligible_projects:
        return None

    exact_relevance = _build_skill_relevance(
        entity_ids=tuple(
            project.id
            for project in eligible_projects
        ),
        skill_links=profile.project_skills,
        matched_skills=matched_skills,
        entity_id_getter=lambda link: link.project_id,
    )

    semantic_relevance = _build_resume_relevance(
        entity_ids=tuple(
            project.id
            for project in eligible_projects
        ),
        skill_links=profile.project_skills,
        job_text=job_text,
        entity_id_getter=lambda link: link.project_id,
    )

    profile_order = {
        project.id: index
        for index, project in enumerate(profile.projects)
    }

    return min(
        eligible_projects,
        key=lambda project: (
            -(
                exact_relevance[project.id]
                + semantic_relevance[project.id]
            ),
            profile_order[project.id],
        ),
    )


def _select_next_experience(
    *,
    profile: CanonicalCandidateProfile,
    selected_experience_ids: set[int],
    matched_skills: set[str],
    job_text: str | None,
):
    eligible_experiences = tuple(
        experience
        for experience in profile.experiences
        if experience.id not in selected_experience_ids
        and _is_allowed_fact(
            experience.verification_status,
            experience.visibility,
        )
    )

    if not eligible_experiences:
        return None

    exact_relevance = _build_skill_relevance(
        entity_ids=tuple(
            experience.id
            for experience in eligible_experiences
        ),
        skill_links=profile.experience_skills,
        matched_skills=matched_skills,
        entity_id_getter=lambda link: link.experience_id,
    )

    semantic_relevance = _build_resume_relevance(
        entity_ids=tuple(
            experience.id
            for experience in eligible_experiences
        ),
        skill_links=profile.experience_skills,
        job_text=job_text,
        entity_id_getter=lambda link: link.experience_id,
    )

    profile_order = {
        experience.id: index
        for index, experience in enumerate(profile.experiences)
    }

    return min(
        eligible_experiences,
        key=lambda experience: (
            -(
                exact_relevance[experience.id]
                + semantic_relevance[experience.id]
            ),
            profile_order[experience.id],
        ),
    )


def _build_skill_relevance(
    *,
    entity_ids: tuple[int, ...],
    skill_links,
    matched_skills: set[str],
    entity_id_getter,
) -> dict[int, int]:
    entity_id_set = set(entity_ids)

    matched_evidence: dict[int, set[str]] = {
        entity_id: set()
        for entity_id in entity_ids
    }

    for skill_link in skill_links:
        entity_id = entity_id_getter(skill_link)

        if entity_id not in entity_id_set:
            continue

        normalized_name = (
            skill_link.skill.normalized_name.casefold()
        )

        if normalized_name in matched_skills:
            matched_evidence[entity_id].add(
                normalized_name
            )

    return {
        entity_id: len(skill_names)
        for entity_id, skill_names in matched_evidence.items()
    }


def _build_resume_relevance(
    *,
    entity_ids: tuple[int, ...],
    skill_links,
    job_text: str | None,
    entity_id_getter,
) -> dict[int, int]:
    entity_id_set = set(entity_ids)

    evidence_terms: dict[int, set[str]] = {
        entity_id: set()
        for entity_id in entity_ids
    }

    for skill_link in skill_links:
        entity_id = entity_id_getter(skill_link)

        if entity_id not in entity_id_set:
            continue

        evidence_terms[entity_id].add(
            skill_link.skill.normalized_name
        )

        evidence_terms[entity_id].add(
            skill_link.skill.canonical_name
        )

        if skill_link.usage_description:
            evidence_terms[entity_id].add(
                skill_link.usage_description
            )

    return {
        entity_id: score_resume_evidence(
            job_text=job_text,
            evidence_terms=terms,
        )
        for entity_id, terms in evidence_terms.items()
    }


def _is_allowed_fact(
    verification_status: str,
    visibility: str,
) -> bool:
    return (
        verification_status in APPROVED_VERIFICATION_STATUSES
        and visibility in ALLOWED_RESUME_VISIBILITIES
    )


def _validate_inputs(
    *,
    profile: CanonicalCandidateProfile,
    tailoring_input: TailoringInput,
    match_result: CandidateJobMatchResult,
) -> None:
    candidate_id = profile.identity.candidate_id

    if tailoring_input.candidate_id != candidate_id:
        raise ValueError(
            "Tailoring input candidate does not match candidate profile."
        )

    if match_result.candidate_id != candidate_id:
        raise ValueError(
            "Match result candidate does not match candidate profile."
        )

    if match_result.job_id != tailoring_input.job.job_id:
        raise ValueError(
            "Match result job does not match tailoring input."
        )