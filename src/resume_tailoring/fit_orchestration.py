from dataclasses import dataclass
from typing import Callable

from src.resume_tailoring.composition import (
    ResumeCompositionPlan,
)
from src.resume_tailoring.fit_adjustment import (
    adjust_composition_plan,
)
from src.resume_tailoring.page_fit import (
    PageFitResult,
    classify_page_fit,
)


DEFAULT_MAX_FIT_ATTEMPTS = 10


class FitAdjustmentLimitError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FitCompositionResult:
    plan: ResumeCompositionPlan
    measurement: PageFitResult
    fit_status: str
    attempts: int
    adjustment_exhausted: bool = False


def fit_composition_plan(
    *,
    initial_plan: ResumeCompositionPlan,
    experience_relevance: dict[int, int],
    project_relevance: dict[int, int],
    measure_plan: Callable[
        [ResumeCompositionPlan],
        PageFitResult,
    ],
    max_attempts: int = DEFAULT_MAX_FIT_ATTEMPTS,
) -> FitCompositionResult:
    if max_attempts <= 0:
        raise ValueError(
            "Maximum fit attempts must be positive."
        )

    current_plan = initial_plan

    for attempt in range(1, max_attempts + 1):
        measurement = measure_plan(current_plan)
        fit_status = classify_page_fit(measurement)

        if fit_status == "target":
            return FitCompositionResult(
                plan=current_plan,
                measurement=measurement,
                fit_status=fit_status,
                attempts=attempt,
            )

        adjusted_plan = adjust_composition_plan(
            plan=current_plan,
            fit_status=fit_status,
            experience_relevance=experience_relevance,
            project_relevance=project_relevance,
        )

        if adjusted_plan == current_plan:
            return FitCompositionResult(
                plan=current_plan,
                measurement=measurement,
                fit_status=fit_status,
                attempts=attempt,
                adjustment_exhausted=True,
            )

        if attempt == max_attempts:
            raise FitAdjustmentLimitError(
                "Resume fit adjustment exceeded "
                "the maximum number of attempts."
            )

        current_plan = adjusted_plan

    raise FitAdjustmentLimitError(
        "Resume fit adjustment exceeded "
        "the maximum number of attempts."
    )