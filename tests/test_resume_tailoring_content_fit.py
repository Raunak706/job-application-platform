from src.resume_tailoring.content_fit import (
    ContentFitLimitError,
    fit_generated_content,
)
from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
)
from src.resume_tailoring.page_fit import PageFitResult


def _content(
    *,
    experiences=(),
    projects=(),
):
    return StructuredResumeContent(
        professional_summary=None,
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
        skills=("Python",),
    )


def _measurement(
    *,
    page_count=1,
    content_height=705.0,
    usable_height=720.0,
):
    return PageFitResult(
        page_count=page_count,
        content_height_points=content_height,
        usable_height_points=usable_height,
    )


def test_target_content_is_returned_unchanged():
    content = _content(
        experiences=(
            (101, ("e1", "e2", "e3")),
        ),
    )

    result = fit_generated_content(
        initial_content=content,
        experience_relevance={101: 5},
        project_relevance={},
        measure_content=lambda supplied_content: _measurement(
            content_height=705.0,
        ),
    )

    assert result.content == content
    assert result.fit_status == "target"
    assert result.attempts == 1
    assert result.adjustment_exhausted is False


def test_overfull_content_is_trimmed_and_remeasured():
    content = _content(
        projects=(
            (201, ("p1", "p2", "p3")),
        ),
    )

    measured_contents = []

    def measure_content(supplied_content):
        measured_contents.append(supplied_content)

        if len(supplied_content.projects[0].bullets) == 3:
            return _measurement(
                page_count=2,
                content_height=730.0,
            )

        return _measurement(
            page_count=1,
            content_height=705.0,
        )

    result = fit_generated_content(
        initial_content=content,
        experience_relevance={},
        project_relevance={201: 5},
        measure_content=measure_content,
    )

    assert len(measured_contents) == 2

    assert measured_contents[0] == content

    assert measured_contents[1].projects[0].bullets == (
        "p1",
        "p2",
    )

    assert result.content.projects[0].bullets == (
        "p1",
        "p2",
    )
    assert result.fit_status == "target"
    assert result.attempts == 2


def test_each_overfull_attempt_trims_only_existing_content():
    content = _content(
        projects=(
            (201, ("p1", "p2", "p3", "p4")),
        ),
    )

    measured_bullet_counts = []

    def measure_content(supplied_content):
        bullet_count = len(
            supplied_content.projects[0].bullets
        )
        measured_bullet_counts.append(bullet_count)

        if bullet_count > 2:
            return _measurement(
                page_count=2,
                content_height=730.0,
            )

        return _measurement(
            page_count=1,
            content_height=705.0,
        )

    result = fit_generated_content(
        initial_content=content,
        experience_relevance={},
        project_relevance={201: 5},
        measure_content=measure_content,
    )

    assert measured_bullet_counts == [4, 3, 2]
    assert result.attempts == 3
    assert result.fit_status == "target"


def test_underfilled_content_returns_exhausted_without_expansion():
    content = _content(
        experiences=(
            (101, ("e1", "e2", "e3")),
        ),
    )

    measure_calls = []

    def measure_content(supplied_content):
        measure_calls.append(supplied_content)
        return _measurement(
            page_count=1,
            content_height=400.0,
        )

    result = fit_generated_content(
        initial_content=content,
        experience_relevance={101: 5},
        project_relevance={},
        measure_content=measure_content,
    )

    assert measure_calls == [content]
    assert result.content == content
    assert result.fit_status == "underfilled"
    assert result.attempts == 1
    assert result.adjustment_exhausted is True


def test_overfull_returns_exhausted_when_nothing_can_be_trimmed():
    content = _content(
        experiences=(
            (101, ("e1", "e2")),
        ),
        projects=(
            (201, ("p1", "p2")),
        ),
    )

    result = fit_generated_content(
        initial_content=content,
        experience_relevance={101: 5},
        project_relevance={201: 4},
        measure_content=lambda supplied_content: _measurement(
            page_count=2,
            content_height=730.0,
        ),
    )

    assert result.content == content
    assert result.fit_status == "overfull"
    assert result.attempts == 1
    assert result.adjustment_exhausted is True


def test_result_preserves_final_measurement():
    content = _content(
        experiences=(
            (101, ("e1", "e2")),
        ),
    )

    measurement = _measurement(
        page_count=1,
        content_height=680.0,
        usable_height=720.0,
    )

    result = fit_generated_content(
        initial_content=content,
        experience_relevance={101: 5},
        project_relevance={},
        measure_content=lambda supplied_content: measurement,
    )

    assert result.measurement is measurement


def test_rejects_nonpositive_max_attempts():
    content = _content()

    try:
        fit_generated_content(
            initial_content=content,
            experience_relevance={},
            project_relevance={},
            measure_content=lambda supplied_content: _measurement(),
            max_attempts=0,
        )
    except ValueError as error:
        assert str(error) == (
            "Maximum fit attempts must be positive."
        )
    else:
        raise AssertionError(
            "Expected nonpositive maximum attempts to fail."
        )


def test_raises_when_overfull_trimming_exceeds_attempt_limit():
    content = _content(
        projects=(
            (201, ("p1", "p2", "p3", "p4")),
        ),
    )

    try:
        fit_generated_content(
            initial_content=content,
            experience_relevance={},
            project_relevance={201: 5},
            measure_content=lambda supplied_content: _measurement(
                page_count=2,
                content_height=730.0,
            ),
            max_attempts=2,
        )
    except ContentFitLimitError as error:
        assert str(error) == (
            "Resume content fitting exceeded "
            "the maximum number of attempts."
        )
    else:
        raise AssertionError(
            "Expected content fitting attempt limit to fail."
        )