from src.resume_tailoring.content_trimming import trim_generated_content
from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
)


def _content(
    *,
    experiences=(),
    projects=(),
    skills=("Python", "SQL"),
):
    return StructuredResumeContent(
        professional_summary="Data engineer focused on reliable systems.",
        experiences=tuple(
            GeneratedExperienceContent(
                experience_id=experience_id,
                bullets=tuple(bullets),
            )
            for experience_id, bullets in experiences
        ),
        projects=tuple(
            GeneratedProjectContent(
                project_id=project_id,
                bullets=tuple(bullets),
            )
            for project_id, bullets in projects
        ),
        skills=skills,
    )


def test_trims_last_bullet_from_lowest_relevance_project_first():
    content = _content(
        experiences=(
            (101, ("e101-1", "e101-2", "e101-3")),
        ),
        projects=(
            (201, ("p201-1", "p201-2", "p201-3")),
            (202, ("p202-1", "p202-2", "p202-3")),
        ),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={101: 1},
        project_relevance={201: 5, 202: 2},
    )

    assert trimmed.projects == (
        GeneratedProjectContent(
            project_id=201,
            bullets=("p201-1", "p201-2", "p201-3"),
        ),
        GeneratedProjectContent(
            project_id=202,
            bullets=("p202-1", "p202-2"),
        ),
    )


def test_trimming_preserves_earlier_project_bullets():
    content = _content(
        projects=(
            (
                201,
                (
                    "strongest",
                    "second",
                    "most expendable",
                ),
            ),
        ),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={},
        project_relevance={201: 5},
    )

    assert trimmed.projects[0].bullets == (
        "strongest",
        "second",
    )


def test_never_reduces_project_below_two_bullets():
    content = _content(
        projects=(
            (201, ("p201-1", "p201-2", "p201-3")),
            (202, ("p202-1", "p202-2")),
        ),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={},
        project_relevance={201: 5, 202: 1},
    )

    assert trimmed.projects == (
        GeneratedProjectContent(
            project_id=201,
            bullets=("p201-1", "p201-2"),
        ),
        GeneratedProjectContent(
            project_id=202,
            bullets=("p202-1", "p202-2"),
        ),
    )


def test_trims_experience_when_projects_cannot_reduce():
    content = _content(
        experiences=(
            (101, ("e101-1", "e101-2", "e101-3")),
            (102, ("e102-1", "e102-2", "e102-3")),
        ),
        projects=(
            (201, ("p201-1", "p201-2")),
        ),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={101: 2, 102: 5},
        project_relevance={201: 1},
    )

    assert trimmed.experiences == (
        GeneratedExperienceContent(
            experience_id=101,
            bullets=("e101-1", "e101-2"),
        ),
        GeneratedExperienceContent(
            experience_id=102,
            bullets=("e102-1", "e102-2", "e102-3"),
        ),
    )


def test_never_reduces_experience_below_two_bullets():
    content = _content(
        experiences=(
            (101, ("e101-1", "e101-2")),
        ),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={101: 5},
        project_relevance={},
    )

    assert trimmed == content


def test_trims_only_one_bullet_per_call():
    content = _content(
        experiences=(
            (101, ("e101-1", "e101-2", "e101-3", "e101-4")),
        ),
        projects=(
            (201, ("p201-1", "p201-2", "p201-3", "p201-4")),
            (202, ("p202-1", "p202-2", "p202-3", "p202-4")),
        ),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={101: 1},
        project_relevance={201: 5, 202: 2},
    )

    before = sum(
        len(item.bullets)
        for item in content.experiences + content.projects
    )
    after = sum(
        len(item.bullets)
        for item in trimmed.experiences + trimmed.projects
    )

    assert after == before - 1


def test_equal_relevance_uses_existing_order():
    content = _content(
        projects=(
            (201, ("p201-1", "p201-2", "p201-3")),
            (202, ("p202-1", "p202-2", "p202-3")),
        ),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={},
        project_relevance={201: 2, 202: 2},
    )

    assert trimmed.projects == (
        GeneratedProjectContent(
            project_id=201,
            bullets=("p201-1", "p201-2"),
        ),
        GeneratedProjectContent(
            project_id=202,
            bullets=("p202-1", "p202-2", "p202-3"),
        ),
    )


def test_returns_same_content_when_nothing_can_be_trimmed():
    content = _content(
        experiences=(
            (101, ("e101-1", "e101-2")),
        ),
        projects=(
            (201, ("p201-1", "p201-2")),
            (202, ("p202-1", "p202-2")),
        ),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={101: 5},
        project_relevance={201: 4, 202: 3},
    )

    assert trimmed == content


def test_trimming_preserves_summary_skills_and_record_order():
    content = _content(
        experiences=(
            (101, ("e101-1", "e101-2", "e101-3")),
            (102, ("e102-1", "e102-2", "e102-3")),
        ),
        projects=(
            (201, ("p201-1", "p201-2", "p201-3")),
        ),
        skills=("Python", "SQL", "PostgreSQL"),
    )

    trimmed = trim_generated_content(
        content=content,
        experience_relevance={101: 5, 102: 4},
        project_relevance={201: 1},
    )

    assert trimmed.professional_summary == content.professional_summary
    assert trimmed.skills == content.skills

    assert tuple(
        item.experience_id for item in trimmed.experiences
    ) == (101, 102)

    assert tuple(
        item.project_id for item in trimmed.projects
    ) == (201,)