from src.resume_tailoring.contracts import (
    StructuredResumeContent,
    TailoringInput,
)


def validate_generated_content(
    tailoring_input: TailoringInput,
    content: StructuredResumeContent,
) -> None:
    allowed_experience_ids = {
        experience.id
        for experience in tailoring_input.experiences
    }

    allowed_project_ids = {
        project.id
        for project in tailoring_input.projects
    }

    allowed_skills = {
        skill.skill.canonical_name.casefold()
        for skill in tailoring_input.skills
    }

    for experience_content in content.experiences:
        if experience_content.experience_id not in allowed_experience_ids:
            raise ValueError(
                "Generated content references an unknown experience."
            )

        _validate_bullets(
            experience_content.bullets,
        )

    for project_content in content.projects:
        if project_content.project_id not in allowed_project_ids:
            raise ValueError(
                "Generated content references an unknown project."
            )

        _validate_bullets(
            project_content.bullets,
        )

    for skill in content.skills:
        if skill.casefold() not in allowed_skills:
            raise ValueError(
                "Generated content references an unapproved skill."
            )


def _validate_bullets(
    bullets: tuple[str, ...],
) -> None:
    for bullet in bullets:
        if not bullet.strip():
            raise ValueError(
                "Generated content contains a blank bullet."
            )