from src.candidate_profile.contracts import CanonicalCandidateProfile
from src.database.models import Job
from src.matching.contracts import CandidateJobMatchResult
from src.resume_tailoring.contracts import (
    TailoringInput,
    TailoringJobContext,
)


APPROVED_VERIFICATION_STATUSES = {
    "verified",
    "source_document",
    "manual",
}

ALLOWED_RESUME_VISIBILITIES = {
    "internal",
    "resume_safe",
}


def build_tailoring_input(
    profile: CanonicalCandidateProfile,
    job: Job,
    match_result: CandidateJobMatchResult,
) -> TailoringInput:
    candidate_id = profile.identity.candidate_id

    if candidate_id != match_result.candidate_id:
        raise ValueError(
            "Match result candidate does not match candidate profile."
        )

    if job.id != match_result.job_id:
        raise ValueError(
            "Match result job does not match normalized job."
        )

    supporting_experience_ids = set(
        match_result.supporting_experience_ids
    )
    supporting_project_ids = set(
        match_result.supporting_project_ids
    )
    matched_skills = {
        skill.casefold()
        for skill in match_result.matched_skills
    }

    experiences = tuple(
        experience
        for experience in profile.experiences
        if experience.id in supporting_experience_ids
        and _is_allowed_fact(
            experience.verification_status,
            experience.visibility,
        )
    )

    projects = tuple(
        project
        for project in profile.projects
        if project.id in supporting_project_ids
        and _is_allowed_fact(
            project.verification_status,
            project.visibility,
        )
    )

    skills = tuple(
        candidate_skill
        for candidate_skill in profile.skills
        if candidate_skill.skill.normalized_name.casefold()
        in matched_skills
        and _is_allowed_fact(
            candidate_skill.verification_status,
            candidate_skill.visibility,
        )
    )

    selected_experience_ids = {
        experience.id
        for experience in experiences
    }
    selected_project_ids = {
        project.id
        for project in projects
    }

    achievements = tuple(
        achievement
        for achievement in profile.achievements
        if (
            achievement.experience_id in selected_experience_ids
            or achievement.project_id in selected_project_ids
        )
        and _is_allowed_fact(
            achievement.verification_status,
            achievement.visibility,
        )
    )

    job_context = TailoringJobContext(
        job_id=job.id,
        title=job.title,
        company=job.company,
        description=job.description,
        location=job.location,
        country=job.country,
        workplace_type=job.workplace_type,
        employment_type=job.employment_type,
        department=job.department,
    )

    return TailoringInput(
        candidate_id=candidate_id,
        job=job_context,
        professional_headline=profile.profile.professional_headline,
        professional_summary=profile.profile.professional_summary,
        experiences=experiences,
        projects=projects,
        skills=skills,
        achievements=achievements,
    )


def _is_allowed_fact(
    verification_status: str,
    visibility: str,
) -> bool:
    return (
        verification_status in APPROVED_VERIFICATION_STATUSES
        and visibility in ALLOWED_RESUME_VISIBILITIES
    )