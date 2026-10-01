from dataclasses import dataclass
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
    build_fit_relevance,
)
from src.resume_tailoring.page_fit import (
    PageFitResult,
)
from src.resume_tailoring.validation import (
    validate_generated_content,
)


@dataclass(frozen=True, slots=True)
class FallbackGenerationResult:
    tailoring_input: TailoringInput
    fit_result: ContentFitResult
    generation_attempts: int
    fallback_used: bool


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
    first_fit = _generate_and_fit(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
        generator=generator,
        measure_content=measure_content,
    )

    if first_fit.fit_status != "underfilled":
        return FallbackGenerationResult(
            tailoring_input=tailoring_input,
            fit_result=first_fit,
            generation_attempts=1,
            fallback_used=False,
        )

    fallback_input = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
    )

    if fallback_input == tailoring_input:
        return FallbackGenerationResult(
            tailoring_input=tailoring_input,
            fit_result=first_fit,
            generation_attempts=1,
            fallback_used=False,
        )

    second_fit = _generate_and_fit(
        profile=profile,
        tailoring_input=fallback_input,
        match_result=match_result,
        generator=generator,
        measure_content=measure_content,
    )

    return FallbackGenerationResult(
        tailoring_input=fallback_input,
        fit_result=second_fit,
        generation_attempts=2,
        fallback_used=True,
    )


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
) -> ContentFitResult:
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

    return fit_generated_content(
        initial_content=generated_content,
        experience_relevance=relevance.experiences,
        project_relevance=relevance.projects,
        measure_content=measure_content,
    )