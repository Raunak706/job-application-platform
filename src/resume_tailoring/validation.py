from src.resume_tailoring.contracts import (
    ResumeGenerationInput,
    StructuredResumeContent,
)


def validate_generated_content(
    generation_input: ResumeGenerationInput,
    content: StructuredResumeContent,
) -> None:
    tailoring_input = generation_input.tailoring_input
    composition_plan = generation_input.composition_plan

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

    expected_experience_bullets = {
        allocation.experience_id: allocation.target_bullets
        for allocation in composition_plan.experiences
    }

    expected_project_bullets = {
        allocation.project_id: allocation.target_bullets
        for allocation in composition_plan.projects
    }

    generated_experience_ids = [
        experience_content.experience_id
        for experience_content in content.experiences
    ]

    generated_project_ids = [
        project_content.project_id
        for project_content in content.projects
    ]

    for experience_id in generated_experience_ids:
        if experience_id not in allowed_experience_ids:
            raise ValueError(
                "Generated content references an unknown experience."
            )

    for project_id in generated_project_ids:
        if project_id not in allowed_project_ids:
            raise ValueError(
                "Generated content references an unknown project."
            )

    if len(generated_experience_ids) != len(set(generated_experience_ids)):
        raise ValueError(
            "Generated content contains a duplicate experience."
        )

    if len(generated_project_ids) != len(set(generated_project_ids)):
        raise ValueError(
            "Generated content contains a duplicate project."
        )

    if set(generated_experience_ids) != set(expected_experience_bullets):
        raise ValueError(
            "Generated content does not match the planned experiences."
        )

    if set(generated_project_ids) != set(expected_project_bullets):
        raise ValueError(
            "Generated content does not match the planned projects."
        )

    for experience_content in content.experiences:
        _validate_bullets(
            experience_content.bullets,
        )

        expected_count = expected_experience_bullets[
            experience_content.experience_id
        ]

        if len(experience_content.bullets) != expected_count:
            raise ValueError(
                "Generated experience bullet count does not match "
                "the composition plan."
            )

    for project_content in content.projects:
        _validate_bullets(
            project_content.bullets,
        )

        expected_count = expected_project_bullets[
            project_content.project_id
        ]

        if len(project_content.bullets) != expected_count:
            raise ValueError(
                "Generated project bullet count does not match "
                "the composition plan."
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