from pathlib import Path
from typing import Callable

from src.resume_tailoring.composition import (
    ResumeCompositionPlan,
)
from src.resume_tailoring.content_generator import (
    ResumeContentGenerator,
)
from src.resume_tailoring.contracts import (
    ResumeGenerationInput,
    TailoringInput,
)
from src.resume_tailoring.page_fit import (
    PageFitResult,
    build_page_fit_result_from_compilation,
)
from src.resume_tailoring.pdf_measurement import (
    LatexCompilationResult,
    compile_latex,
)
from src.resume_tailoring.renderer import (
    render_resume,
)
from src.resume_tailoring.validation import (
    validate_generated_content,
)


def create_plan_measurement_callback(
    *,
    profile,
    tailoring_input: TailoringInput,
    generator: ResumeContentGenerator,
    work_directory: Path,
    render_resume_fn: Callable = render_resume,
    compile_latex_fn: Callable = compile_latex,
) -> Callable[[ResumeCompositionPlan], PageFitResult]:
    attempt_number = 0

    def measure_plan(
        plan: ResumeCompositionPlan,
    ) -> PageFitResult:
        nonlocal attempt_number

        attempt_number += 1

        generation_input = ResumeGenerationInput(
            tailoring_input=tailoring_input,
            composition_plan=plan,
        )

        generated_content = generator.generate(
            generation_input,
        )

        validate_generated_content(
            generation_input,
            generated_content,
        )

        latex_source = render_resume_fn(
            profile,
            generated_content,
        )

        attempt_directory = (
            work_directory
            / f"attempt_{attempt_number}"
        )

        compilation: LatexCompilationResult = (
            compile_latex_fn(
                latex_source=latex_source,
                work_directory=attempt_directory,
            )
        )

        return build_page_fit_result_from_compilation(
            compilation
        )

    return measure_plan