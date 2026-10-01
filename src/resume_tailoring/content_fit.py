from dataclasses import dataclass
from typing import Callable

from src.resume_tailoring.content_trimming import (
    trim_generated_content,
)
from src.resume_tailoring.contracts import (
    StructuredResumeContent,
)
from src.resume_tailoring.fit_orchestration import (
    DEFAULT_MAX_FIT_ATTEMPTS,
)
from src.resume_tailoring.page_fit import (
    PageFitResult,
    classify_page_fit,
)


class ContentFitLimitError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ContentFitResult:
    content: StructuredResumeContent
    measurement: PageFitResult
    fit_status: str
    attempts: int
    adjustment_exhausted: bool = False


def fit_generated_content(
    *,
    initial_content: StructuredResumeContent,
    experience_relevance: dict[int, int],
    project_relevance: dict[int, int],
    measure_content: Callable[
        [StructuredResumeContent],
        PageFitResult,
    ],
    max_attempts: int = DEFAULT_MAX_FIT_ATTEMPTS,
) -> ContentFitResult:
    if max_attempts <= 0:
        raise ValueError(
            "Maximum fit attempts must be positive."
        )

    current_content = initial_content

    for attempt in range(1, max_attempts + 1):
        measurement = measure_content(
            current_content
        )
        fit_status = classify_page_fit(
            measurement
        )

        if fit_status == "target":
            return ContentFitResult(
                content=current_content,
                measurement=measurement,
                fit_status=fit_status,
                attempts=attempt,
            )

        if fit_status == "underfilled":
            return ContentFitResult(
                content=current_content,
                measurement=measurement,
                fit_status=fit_status,
                attempts=attempt,
                adjustment_exhausted=True,
            )

        trimmed_content = trim_generated_content(
            content=current_content,
            experience_relevance=experience_relevance,
            project_relevance=project_relevance,
        )

        if trimmed_content == current_content:
            return ContentFitResult(
                content=current_content,
                measurement=measurement,
                fit_status=fit_status,
                attempts=attempt,
                adjustment_exhausted=True,
            )

        if attempt == max_attempts:
            raise ContentFitLimitError(
                "Resume content fitting exceeded "
                "the maximum number of attempts."
            )

        current_content = trimmed_content

    raise ContentFitLimitError(
        "Resume content fitting exceeded "
        "the maximum number of attempts."
    )