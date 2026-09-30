from src.resume_tailoring.composition import (
    ExperienceContentAllocation,
    ProjectContentAllocation,
    ResumeCompositionPlan,
)
from src.resume_tailoring.fit_adjustment import (
    adjust_composition_plan,
)


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


def test_target_fit_keeps_plan_unchanged():
    plan = _plan(
        experiences=((101, 3), (102, 4)),
        projects=((201, 4), (202, 2), (203, 2)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="target",
        experience_relevance={
            101: 4,
            102: 5,
        },
        project_relevance={
            201: 5,
            202: 2,
            203: 1,
        },
    )

    assert adjusted == plan


def test_overfull_reduces_lowest_relevance_project_first():
    plan = _plan(
        experiences=((101, 3), (102, 4)),
        projects=((201, 4), (202, 3), (203, 3)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="overfull",
        experience_relevance={
            101: 4,
            102: 5,
        },
        project_relevance={
            201: 5,
            202: 2,
            203: 1,
        },
    )

    assert adjusted.projects == (
        ProjectContentAllocation(201, 4),
        ProjectContentAllocation(202, 3),
        ProjectContentAllocation(203, 2),
    )


def test_overfull_never_reduces_project_below_two_bullets():
    plan = _plan(
        projects=((201, 4), (202, 2), (203, 2)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="overfull",
        experience_relevance={},
        project_relevance={
            201: 5,
            202: 2,
            203: 1,
        },
    )

    assert adjusted.projects == (
        ProjectContentAllocation(201, 3),
        ProjectContentAllocation(202, 2),
        ProjectContentAllocation(203, 2),
    )


def test_overfull_reduces_experience_when_projects_cannot_reduce():
    plan = _plan(
        experiences=((101, 3), (102, 4)),
        projects=((201, 2), (202, 2)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="overfull",
        experience_relevance={
            101: 2,
            102: 5,
        },
        project_relevance={
            201: 4,
            202: 3,
        },
    )

    assert adjusted.experiences == (
        ExperienceContentAllocation(101, 2),
        ExperienceContentAllocation(102, 4),
    )


def test_overfull_reduces_only_one_bullet_per_adjustment():
    plan = _plan(
        experiences=((101, 4), (102, 4)),
        projects=((201, 4), (202, 4), (203, 4)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="overfull",
        experience_relevance={
            101: 2,
            102: 5,
        },
        project_relevance={
            201: 5,
            202: 3,
            203: 1,
        },
    )

    before = sum(
        allocation.target_bullets
        for allocation in plan.experiences + plan.projects
    )
    after = sum(
        allocation.target_bullets
        for allocation in adjusted.experiences
        + adjusted.projects
    )

    assert after == before - 1


def test_overfull_returns_same_plan_when_nothing_can_reduce():
    plan = _plan(
        experiences=((101, 2),),
        projects=((201, 2), (202, 2)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="overfull",
        experience_relevance={
            101: 5,
        },
        project_relevance={
            201: 4,
            202: 3,
        },
    )

    assert adjusted == plan


def test_underfilled_expands_highest_relevance_project_first():
    plan = _plan(
        experiences=((101, 2), (102, 2)),
        projects=((201, 3), (202, 2), (203, 2)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="underfilled",
        experience_relevance={
            101: 4,
            102: 3,
        },
        project_relevance={
            201: 5,
            202: 2,
            203: 1,
        },
    )

    assert adjusted.projects == (
        ProjectContentAllocation(201, 4),
        ProjectContentAllocation(202, 2),
        ProjectContentAllocation(203, 2),
    )


def test_underfilled_expands_experience_when_projects_are_at_maximum():
    plan = _plan(
        experiences=((101, 2), (102, 3)),
        projects=((201, 4), (202, 4)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="underfilled",
        experience_relevance={
            101: 2,
            102: 5,
        },
        project_relevance={
            201: 5,
            202: 4,
        },
    )

    assert adjusted.experiences == (
        ExperienceContentAllocation(101, 2),
        ExperienceContentAllocation(102, 4),
    )


def test_underfilled_adds_only_one_bullet_per_adjustment():
    plan = _plan(
        experiences=((101, 2), (102, 2)),
        projects=((201, 2), (202, 2), (203, 2)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="underfilled",
        experience_relevance={
            101: 4,
            102: 5,
        },
        project_relevance={
            201: 5,
            202: 3,
            203: 1,
        },
    )

    before = sum(
        allocation.target_bullets
        for allocation in plan.experiences + plan.projects
    )
    after = sum(
        allocation.target_bullets
        for allocation in adjusted.experiences
        + adjusted.projects
    )

    assert after == before + 1


def test_underfilled_never_exceeds_four_bullets():
    plan = _plan(
        experiences=((101, 4),),
        projects=((201, 4),),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="underfilled",
        experience_relevance={
            101: 5,
        },
        project_relevance={
            201: 5,
        },
    )

    assert adjusted == plan


def test_equal_relevance_uses_existing_order_for_reduction():
    plan = _plan(
        projects=((201, 4), (202, 3), (203, 3)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="overfull",
        experience_relevance={},
        project_relevance={
            201: 5,
            202: 2,
            203: 2,
        },
    )

    assert adjusted.projects == (
        ProjectContentAllocation(201, 4),
        ProjectContentAllocation(202, 2),
        ProjectContentAllocation(203, 3),
    )


def test_equal_relevance_uses_existing_order_for_expansion():
    plan = _plan(
        projects=((201, 3), (202, 2), (203, 2)),
    )

    adjusted = adjust_composition_plan(
        plan=plan,
        fit_status="underfilled",
        experience_relevance={},
        project_relevance={
            201: 5,
            202: 2,
            203: 2,
        },
    )

    assert adjusted.projects == (
        ProjectContentAllocation(201, 4),
        ProjectContentAllocation(202, 2),
        ProjectContentAllocation(203, 2),
    )