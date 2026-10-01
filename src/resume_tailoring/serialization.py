from typing import Any

from src.resume_tailoring.contracts import (
    ResumeGenerationInput,
    TailoringInput,
)


def serialize_generation_input(
    generation_input: ResumeGenerationInput,
) -> dict[str, Any]:
    result = serialize_tailoring_input(
        generation_input.tailoring_input,
    )

    result["composition_guidance"] = {
        "experiences": [
            {
                "experience_id": allocation.experience_id,
                "target_bullets": allocation.target_bullets,
            }
            for allocation in generation_input.composition_plan.experiences
        ],
        "projects": [
            {
                "project_id": allocation.project_id,
                "target_bullets": allocation.target_bullets,
            }
            for allocation in generation_input.composition_plan.projects
        ],
    }

    return result


def serialize_tailoring_input(
    tailoring_input: TailoringInput,
) -> dict[str, Any]:
    return {
        "job_context": {
            "job_id": tailoring_input.job.job_id,
            "title": tailoring_input.job.title,
            "company": tailoring_input.job.company,
            "description": tailoring_input.job.description,
            "location": tailoring_input.job.location,
            "country": tailoring_input.job.country,
            "workplace_type": tailoring_input.job.workplace_type,
            "employment_type": tailoring_input.job.employment_type,
            "department": tailoring_input.job.department,
        },
        "approved_candidate_facts": {
            "candidate_id": tailoring_input.candidate_id,
            "professional_headline": tailoring_input.professional_headline,
            "professional_summary": tailoring_input.professional_summary,
            "experiences": [
                {
                    "experience_id": experience.id,
                    "company": experience.company,
                    "title": experience.title,
                    "employment_type": experience.employment_type,
                    "department": experience.department,
                    "location": experience.location,
                    "country": experience.country,
                    "start_date": _serialize_date(experience.start_date),
                    "end_date": _serialize_date(experience.end_date),
                    "is_current": experience.is_current,
                    "description": experience.description,
                }
                for experience in tailoring_input.experiences
            ],
            "projects": [
                {
                    "project_id": project.id,
                    "name": project.name,
                    "role": project.role,
                    "organization": project.organization,
                    "description": project.description,
                    "problem": project.problem,
                    "solution": project.solution,
                    "architecture": project.architecture,
                    "outcome": project.outcome,
                    "start_date": _serialize_date(project.start_date),
                    "end_date": _serialize_date(project.end_date),
                    "status": project.status,
                }
                for project in tailoring_input.projects
            ],
            "skills": [
                {
                    "name": skill.skill.canonical_name,
                    "category": skill.skill.category,
                    "proficiency_level": skill.proficiency_level,
                    "experience_months": skill.experience_months,
                    "last_used_date": _serialize_date(skill.last_used_date),
                    "notes": skill.notes,
                }
                for skill in tailoring_input.skills
            ],
            "achievements": [
                {
                    "achievement_id": achievement.id,
                    "experience_id": achievement.experience_id,
                    "project_id": achievement.project_id,
                    "title": achievement.title,
                    "description": achievement.description,
                    "metric_text": achievement.metric_text,
                }
                for achievement in tailoring_input.achievements
            ],
            "experience_skills": [
                {
                    "experience_id": experience_skill.experience_id,
                    "skill_name": experience_skill.skill.canonical_name,
                    "normalized_name": (
                        experience_skill.skill.normalized_name
                    ),
                    "category": experience_skill.skill.category,
                    "usage_description": (
                        experience_skill.usage_description
                    ),
                }
                for experience_skill in tailoring_input.experience_skills
            ],
            "project_skills": [
                {
                    "project_id": project_skill.project_id,
                    "skill_name": project_skill.skill.canonical_name,
                    "normalized_name": (
                        project_skill.skill.normalized_name
                    ),
                    "category": project_skill.skill.category,
                    "usage_description": (
                        project_skill.usage_description
                    ),
                }
                for project_skill in tailoring_input.project_skills
            ],
        },
    }


def _serialize_date(value):
    if value is None:
        return None

    return value.isoformat()