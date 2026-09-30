from src.resume_tailoring.composition import (
    MAX_EXPERIENCE_BULLETS,
    MAX_PROJECT_BULLETS,
    MIN_EXPERIENCE_BULLETS,
    MIN_PROJECT_BULLETS,
    ExperienceContentAllocation,
    ProjectContentAllocation,
    ResumeCompositionPlan,
)


def adjust_composition_plan(
    *,
    plan: ResumeCompositionPlan,
    fit_status: str,
    experience_relevance: dict[int, int],
    project_relevance: dict[int, int],
) -> ResumeCompositionPlan:
    if fit_status == "target":
        return plan

    if fit_status == "overfull":
        return _reduce_plan(
            plan=plan,
            experience_relevance=experience_relevance,
            project_relevance=project_relevance,
        )

    if fit_status == "underfilled":
        return _expand_plan(
            plan=plan,
            experience_relevance=experience_relevance,
            project_relevance=project_relevance,
        )

    raise ValueError(
        f"Unsupported page fit status: {fit_status}"
    )


def _reduce_plan(
    *,
    plan: ResumeCompositionPlan,
    experience_relevance: dict[int, int],
    project_relevance: dict[int, int],
) -> ResumeCompositionPlan:
    project_index = _lowest_relevance_reducible_index(
        allocations=plan.projects,
        relevance=project_relevance,
        minimum=MIN_PROJECT_BULLETS,
        id_getter=lambda allocation: allocation.project_id,
    )

    if project_index is not None:
        projects = list(plan.projects)
        allocation = projects[project_index]

        projects[project_index] = ProjectContentAllocation(
            project_id=allocation.project_id,
            target_bullets=allocation.target_bullets - 1,
        )

        return ResumeCompositionPlan(
            experiences=plan.experiences,
            projects=tuple(projects),
        )

    experience_index = _lowest_relevance_reducible_index(
        allocations=plan.experiences,
        relevance=experience_relevance,
        minimum=MIN_EXPERIENCE_BULLETS,
        id_getter=lambda allocation: allocation.experience_id,
    )

    if experience_index is None:
        return plan

    experiences = list(plan.experiences)
    allocation = experiences[experience_index]

    experiences[experience_index] = ExperienceContentAllocation(
        experience_id=allocation.experience_id,
        target_bullets=allocation.target_bullets - 1,
    )

    return ResumeCompositionPlan(
        experiences=tuple(experiences),
        projects=plan.projects,
    )


def _expand_plan(
    *,
    plan: ResumeCompositionPlan,
    experience_relevance: dict[int, int],
    project_relevance: dict[int, int],
) -> ResumeCompositionPlan:
    project_index = _highest_relevance_expandable_index(
        allocations=plan.projects,
        relevance=project_relevance,
        maximum=MAX_PROJECT_BULLETS,
        id_getter=lambda allocation: allocation.project_id,
    )

    if project_index is not None:
        projects = list(plan.projects)
        allocation = projects[project_index]

        projects[project_index] = ProjectContentAllocation(
            project_id=allocation.project_id,
            target_bullets=allocation.target_bullets + 1,
        )

        return ResumeCompositionPlan(
            experiences=plan.experiences,
            projects=tuple(projects),
        )

    experience_index = _highest_relevance_expandable_index(
        allocations=plan.experiences,
        relevance=experience_relevance,
        maximum=MAX_EXPERIENCE_BULLETS,
        id_getter=lambda allocation: allocation.experience_id,
    )

    if experience_index is None:
        return plan

    experiences = list(plan.experiences)
    allocation = experiences[experience_index]

    experiences[experience_index] = ExperienceContentAllocation(
        experience_id=allocation.experience_id,
        target_bullets=allocation.target_bullets + 1,
    )

    return ResumeCompositionPlan(
        experiences=tuple(experiences),
        projects=plan.projects,
    )


def _lowest_relevance_reducible_index(
    *,
    allocations,
    relevance: dict[int, int],
    minimum: int,
    id_getter,
) -> int | None:
    candidates = [
        (
            relevance.get(id_getter(allocation), 0),
            index,
        )
        for index, allocation in enumerate(allocations)
        if allocation.target_bullets > minimum
    ]

    if not candidates:
        return None

    _, index = min(
        candidates,
        key=lambda candidate: (
            candidate[0],
            candidate[1],
        ),
    )

    return index


def _highest_relevance_expandable_index(
    *,
    allocations,
    relevance: dict[int, int],
    maximum: int,
    id_getter,
) -> int | None:
    candidates = [
        (
            relevance.get(id_getter(allocation), 0),
            index,
        )
        for index, allocation in enumerate(allocations)
        if allocation.target_bullets < maximum
    ]

    if not candidates:
        return None

    _, index = min(
        candidates,
        key=lambda candidate: (
            -candidate[0],
            candidate[1],
        ),
    )

    return index