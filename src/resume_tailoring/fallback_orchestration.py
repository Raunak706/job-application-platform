from dataclasses import dataclass, replace
from typing import Callable

from src.candidate_profile.contracts import (
    CanonicalCandidateProfile,
)
from src.matching.contracts import (
    CandidateJobMatchResult,
)
from src.resume_tailoring.composition import (
    build_rich_composition_plan,
)
from src.resume_tailoring.content_fit import (
    ContentFitResult,
    fit_generated_content,
)
from src.resume_tailoring.content_generator import (
    ResumeContentGenerator,
)
from src.resume_tailoring.contracts import (
    ResumeGenerationInput,
    StructuredResumeContent,
    TailoringInput,
)
from src.resume_tailoring.fallback_selection import (
    add_next_fallback_evidence,
)
from src.resume_tailoring.fit_relevance import (
    FitRelevance,
    build_fit_relevance,
)
from src.resume_tailoring.page_fit import (
    PageFitResult,
)
from src.resume_tailoring.validation import (
    validate_generated_content,
)


_MAX_FALLBACK_EXPERIENCES = 2
_MAX_FALLBACK_PROJECTS = 3


@dataclass(frozen=True, slots=True)
class FallbackGenerationResult:
    tailoring_input: TailoringInput
    fit_result: ContentFitResult
    generation_attempts: int
    fallback_used: bool


@dataclass(frozen=True, slots=True)
class _GeneratedFitAttempt:
    generated_content: StructuredResumeContent
    fit_result: ContentFitResult
    relevance: FitRelevance


def generate_and_fit_with_fallback(
    *,
    profile: CanonicalCandidateProfile,
    tailoring_input: TailoringInput,
    match_result: CandidateJobMatchResult,
    generator: ResumeContentGenerator,
    measure_content: Callable[
        [StructuredResumeContent],
        PageFitResult,
    ],
) -> FallbackGenerationResult:
    first_attempt = _generate_and_fit(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
        generator=generator,
        measure_content=measure_content,
    )

    if first_attempt.fit_result.fit_status != "underfilled":
        return FallbackGenerationResult(
            tailoring_input=tailoring_input,
            fit_result=first_attempt.fit_result,
            generation_attempts=1,
            fallback_used=False,
        )

    fallback_input = _build_fallback_input(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
    )

    if fallback_input == tailoring_input:
        summary_fit = _fit_with_generated_summary(
            attempt=first_attempt,
            measure_content=measure_content,
        )

        return FallbackGenerationResult(
            tailoring_input=tailoring_input,
            fit_result=summary_fit,
            generation_attempts=1,
            fallback_used=False,
        )

    second_attempt = _generate_and_fit(
        profile=profile,
        tailoring_input=fallback_input,
        match_result=match_result,
        generator=generator,
        measure_content=measure_content,
    )

    second_fit = second_attempt.fit_result

    if second_fit.fit_status == "underfilled":
        second_fit = _fit_with_generated_summary(
            attempt=second_attempt,
            measure_content=measure_content,
        )

    return FallbackGenerationResult(
        tailoring_input=fallback_input,
        fit_result=second_fit,
        generation_attempts=2,
        fallback_used=True,
    )


def _build_fallback_input(
    *,
    profile: CanonicalCandidateProfile,
    tailoring_input: TailoringInput,
    match_result: CandidateJobMatchResult,
) -> TailoringInput:
    current_input = tailoring_input

    while True:
        if (
            len(current_input.experiences)
            >= _MAX_FALLBACK_EXPERIENCES
            and len(current_input.projects)
            >= _MAX_FALLBACK_PROJECTS
        ):
            return current_input

        next_input = add_next_fallback_evidence(
            profile=profile,
            tailoring_input=current_input,
            match_result=match_result,
        )

        if next_input == current_input:
            return current_input

        if (
            len(next_input.experiences)
            > _MAX_FALLBACK_EXPERIENCES
            or len(next_input.projects)
            > _MAX_FALLBACK_PROJECTS
        ):
            return current_input

        current_input = next_input


def _generate_and_fit(
    *,
    profile: CanonicalCandidateProfile,
    tailoring_input: TailoringInput,
    match_result: CandidateJobMatchResult,
    generator: ResumeContentGenerator,
    measure_content: Callable[
        [StructuredResumeContent],
        PageFitResult,
    ],
) -> _GeneratedFitAttempt:
    composition_plan = build_rich_composition_plan(
        tailoring_input
    )

    generation_input = ResumeGenerationInput(
        tailoring_input=tailoring_input,
        composition_plan=composition_plan,
    )

    generated_content = generator.generate(
        generation_input
    )

    validate_generated_content(
        generation_input,
        generated_content,
    )

    relevance = build_fit_relevance(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
    )

    content_without_summary = replace(
        generated_content,
        professional_summary=None,
    )

    fit_result = fit_generated_content(
        initial_content=content_without_summary,
        experience_relevance=relevance.experiences,
        project_relevance=relevance.projects,
        measure_content=measure_content,
    )

    return _GeneratedFitAttempt(
        generated_content=generated_content,
        fit_result=fit_result,
        relevance=relevance,
    )


def _fit_with_generated_summary(
    *,
    attempt: _GeneratedFitAttempt,
    measure_content: Callable[
        [StructuredResumeContent],
        PageFitResult,
    ],
) -> ContentFitResult:
    professional_summary = (
        attempt.generated_content.professional_summary
    )

    if not professional_summary:
        return attempt.fit_result

    content_with_summary = replace(
        attempt.fit_result.content,
        professional_summary=professional_summary,
    )

    return fit_generated_content(
        initial_content=content_with_summary,
        experience_relevance=attempt.relevance.experiences,
        project_relevance=attempt.relevance.projects,
        measure_content=measure_content,
    )