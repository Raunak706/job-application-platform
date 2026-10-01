from dataclasses import replace

from src.resume_tailoring.contracts import StructuredResumeContent


MIN_EXPERIENCE_BULLETS = 2
MIN_PROJECT_BULLETS = 2


def trim_generated_content(
    *,
    content: StructuredResumeContent,
    experience_relevance: dict[int, int],
    project_relevance: dict[int, int],
) -> StructuredResumeContent:
    project_index = _lowest_relevance_reducible_index(
        items=content.projects,
        relevance=project_relevance,
        minimum_bullets=MIN_PROJECT_BULLETS,
        id_attribute="project_id",
    )

    if project_index is not None:
        projects = list(content.projects)
        project = projects[project_index]
        projects[project_index] = replace(
            project,
            bullets=project.bullets[:-1],
        )
        return replace(
            content,
            projects=tuple(projects),
        )

    experience_index = _lowest_relevance_reducible_index(
        items=content.experiences,
        relevance=experience_relevance,
        minimum_bullets=MIN_EXPERIENCE_BULLETS,
        id_attribute="experience_id",
    )

    if experience_index is not None:
        experiences = list(content.experiences)
        experience = experiences[experience_index]
        experiences[experience_index] = replace(
            experience,
            bullets=experience.bullets[:-1],
        )
        return replace(
            content,
            experiences=tuple(experiences),
        )

    return content


def _lowest_relevance_reducible_index(
    *,
    items,
    relevance: dict[int, int],
    minimum_bullets: int,
    id_attribute: str,
) -> int | None:
    candidates = [
        (
            relevance.get(getattr(item, id_attribute), 0),
            index,
        )
        for index, item in enumerate(items)
        if len(item.bullets) > minimum_bullets
    ]

    if not candidates:
        return None

    _, index = min(candidates)
    return index