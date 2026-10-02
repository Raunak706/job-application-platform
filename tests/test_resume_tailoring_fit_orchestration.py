from src.resume_tailoring.composition import (
    ExperienceContentAllocation,
    ProjectContentAllocation,
    ResumeCompositionPlan,
)
from src.resume_tailoring.fit_orchestration import (
    FitAdjustmentLimitError,
    fit_composition_plan,
)
from src.resume_tailoring.page_fit import PageFitResult


def _plan(
    *,
    experiences=(),
    projects=(),
):
    return ResumeCompositionPlan(
        experiences=tuple(
            ExperienceContentAllocation(
                experience_id=experience_id,
                target_bullets=target_bullets,
            )
            for experience_id, target_bullets in experiences
        ),
        projects=tuple(
            ProjectContentAllocation(
                project_id=project_id,
                target_bullets=target_bullets,
            )
            for project_id, target_bullets in projects
        ),
    )


def _fit(
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


def test_target_plan_is_returned_without_adjustment():
    plan = _plan(
        experiences=((101, 3), (102, 4)),
        projects=((201, 4), (202, 2), (203, 2)),
    )

    measured_plans = []

    def measure_plan(candidate_plan):
        measured_plans.append(candidate_plan)
        return _fit(
            content_height=705.0,
        )

    result = fit_composition_plan(
        initial_plan=plan,
        experience_relevance={
            101: 4,
            102: 5,
        },
        project_relevance={
            201: 5,
            202: 2,
            203: 1,
        },
        measure_plan=measure_plan,
    )

    assert result.plan == plan
    assert result.fit_status == "target"
    assert result.attempts == 1
    assert measured_plans == [plan]


def test_overfull_plan_is_reduced_until_target():
    plan = _plan(
        experiences=((101, 3), (102, 4)),
        projects=((201, 4), (202, 3), (203, 3)),
    )

    measured_plans = []

    def measure_plan(candidate_plan):
        measured_plans.append(candidate_plan)

        total_bullets = sum(
            allocation.target_bullets
            for allocation in (
                candidate_plan.experiences
                + candidate_plan.projects
            )
        )

        if total_bullets > 15:
            return _fit(
                page_count=2,
                content_height=700.0,
            )

        return _fit(
            page_count=1,
            content_height=705.0,
        )

    result = fit_composition_plan(
        initial_plan=plan,
        experience_relevance={
            101: 4,
            102: 5,
        },
        project_relevance={
            201: 5,
            202: 2,
            203: 1,
        },
        measure_plan=measure_plan,
    )

    assert result.plan == _plan(
        experiences=((101, 3), (102, 4)),
        projects=((201, 4), (202, 2), (203, 2)),
    )
    assert result.fit_status == "target"
    assert result.attempts == 3
    assert len(measured_plans) == 3


def test_underfilled_plan_is_expanded_until_target():
    plan = _plan(
        experiences=((101, 2), (102, 2)),
        projects=((201, 2), (202, 2)),
    )

    measured_plans = []

    def measure_plan(candidate_plan):
        measured_plans.append(candidate_plan)

        total_bullets = sum(
            allocation.target_bullets
            for allocation in (
                candidate_plan.experiences
                + candidate_plan.projects
            )
        )

        if total_bullets < 10:
            return _fit(
                content_height=600.0,
            )

        return _fit(
            content_height=705.0,
        )

    result = fit_composition_plan(
        initial_plan=plan,
        experience_relevance={
            101: 3,
            102: 4,
        },
        project_relevance={
            201: 5,
            202: 2,
        },
        measure_plan=measure_plan,
    )

    assert result.plan == _plan(
        experiences=((101, 2), (102, 2)),
        projects=((201, 4), (202, 2)),
    )
    assert result.fit_status == "target"
    assert result.attempts == 3


def test_each_attempt_measures_the_new_adjusted_plan():
    plan = _plan(
        projects=((201, 4), (202, 4), (203, 4)),
    )

    measured_plans = []

    def measure_plan(candidate_plan):
        measured_plans.append(candidate_plan)

        if len(measured_plans) < 3:
            return _fit(
                page_count=2,
                content_height=700.0,
            )

        return _fit(
            content_height=705.0,
        )

    result = fit_composition_plan(
        initial_plan=plan,
        experience_relevance={},
        project_relevance={
            201: 5,
            202: 3,
            203: 1,
        },
        measure_plan=measure_plan,
    )

    assert measured_plans == [
        _plan(
            projects=((201, 4), (202, 4), (203, 4)),
        ),
        _plan(
            projects=((201, 4), (202, 4), (203, 3)),
        ),
        _plan(
            projects=((201, 4), (202, 4), (203, 2)),
        ),
    ]

    assert result.plan == measured_plans[-1]


def test_stops_when_overfull_plan_cannot_be_reduced():
    plan = _plan(
        experiences=((101, 2),),
        projects=((201, 2), (202, 2)),
    )

    calls = []

    def measure_plan(candidate_plan):
        calls.append(candidate_plan)

        return _fit(
            page_count=2,
            content_height=700.0,
        )

    result = fit_composition_plan(
        initial_plan=plan,
        experience_relevance={
            101: 5,
        },
        project_relevance={
            201: 4,
            202: 3,
        },
        measure_plan=measure_plan,
    )

    assert result.plan == plan
    assert result.fit_status == "overfull"
    assert result.adjustment_exhausted is True
    assert result.attempts == 1
    assert calls == [plan]


def test_stops_when_underfilled_plan_cannot_be_expanded():
    plan = _plan(
        experiences=((101, 4),),
        projects=((201, 4),),
    )

    calls = []

    def measure_plan(candidate_plan):
        calls.append(candidate_plan)

        return _fit(
            content_height=500.0,
        )

    result = fit_composition_plan(
        initial_plan=plan,
        experience_relevance={
            101: 5,
        },
        project_relevance={
            201: 5,
        },
        measure_plan=measure_plan,
    )

    assert result.plan == plan
    assert result.fit_status == "underfilled"
    assert result.adjustment_exhausted is True
    assert result.attempts == 1


def test_adjustment_limit_prevents_infinite_loop():
    plan = _plan(
        projects=((201, 4), (202, 4), (203, 4)),
    )

    calls = []

    def measure_plan(candidate_plan):
        calls.append(candidate_plan)

        return _fit(
            page_count=2,
            content_height=700.0,
        )

    try:
        fit_composition_plan(
            initial_plan=plan,
            experience_relevance={},
            project_relevance={
                201: 5,
                202: 3,
                203: 1,
            },
            measure_plan=measure_plan,
            max_attempts=2,
        )
    except FitAdjustmentLimitError as error:
        assert str(error) == (
            "Resume fit adjustment exceeded "
            "the maximum number of attempts."
        )
    else:
        raise AssertionError(
            "Expected FitAdjustmentLimitError."
        )

    assert len(calls) == 2


def test_rejects_nonpositive_max_attempts():
    plan = _plan()

    try:
        fit_composition_plan(
            initial_plan=plan,
            experience_relevance={},
            project_relevance={},
            measure_plan=lambda candidate_plan: _fit(),
            max_attempts=0,
        )
    except ValueError as error:
        assert str(error) == (
            "Maximum fit attempts must be positive."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_result_preserves_final_measurement():
    plan = _plan(
        projects=((201, 4),),
    )

    measurement = _fit(
        content_height=705.0,
        usable_height=722.7,
    )

    result = fit_composition_plan(
        initial_plan=plan,
        experience_relevance={},
        project_relevance={
            201: 5,
        },
        measure_plan=lambda candidate_plan: measurement,
    )

    assert result.measurement == measurement
    assert result.fit_status == "target"
    assert result.adjustment_exhausted is False