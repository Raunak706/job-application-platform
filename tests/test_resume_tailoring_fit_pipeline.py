from pathlib import Path
from types import SimpleNamespace

from src.resume_tailoring.composition import (
    ExperienceContentAllocation,
    ProjectContentAllocation,
    ResumeCompositionPlan,
)
from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.fit_pipeline import (
    create_plan_measurement_callback,
)
from src.resume_tailoring.pdf_measurement import (
    LatexCompilationResult,
)


class FakeResumeContentGenerator:
    def __init__(self):
        self.inputs = []

    def generate(self, generation_input):
        self.inputs.append(generation_input)

        return StructuredResumeContent(
            professional_summary=None,
            experiences=tuple(
                GeneratedExperienceContent(
                    experience_id=allocation.experience_id,
                    bullets=tuple(
                        f"Experience bullet {index + 1}"
                        for index in range(
                            allocation.target_bullets
                        )
                    ),
                )
                for allocation in (
                    generation_input.composition_plan.experiences
                )
            ),
            projects=tuple(
                GeneratedProjectContent(
                    project_id=allocation.project_id,
                    bullets=tuple(
                        f"Project bullet {index + 1}"
                        for index in range(
                            allocation.target_bullets
                        )
                    ),
                )
                for allocation in (
                    generation_input.composition_plan.projects
                )
            ),
            skills=("Python",),
        )


def _tailoring_input():
    return TailoringInput(
        candidate_id=999,
        job=TailoringJobContext(
            job_id=100,
            title="Data Engineer",
            company="Example Employer",
            description="Build Python data pipelines.",
            location="New York, NY",
            country="US",
            workplace_type="hybrid",
            employment_type="full_time",
            department="Data",
        ),
        professional_headline="Data Engineer",
        professional_summary=None,
        experiences=(
            SimpleNamespace(
                id=101,
            ),
        ),
        projects=(
            SimpleNamespace(
                id=201,
            ),
        ),
        skills=(
            SimpleNamespace(
                skill=SimpleNamespace(
                    canonical_name="Python",
                ),
            ),
        ),
        achievements=(),
    )


def _plan(
    *,
    experience_bullets=3,
    project_bullets=2,
):
    return ResumeCompositionPlan(
        experiences=(
            ExperienceContentAllocation(
                experience_id=101,
                target_bullets=experience_bullets,
            ),
        ),
        projects=(
            ProjectContentAllocation(
                project_id=201,
                target_bullets=project_bullets,
            ),
        ),
    )


def test_measurement_callback_uses_supplied_composition_plan(
    tmp_path,
):
    generator = FakeResumeContentGenerator()
    tailoring_input = _tailoring_input()
    profile = object()

    rendered_contents = []

    def render_resume_fn(candidate_profile, content):
        assert candidate_profile is profile
        rendered_contents.append(content)
        return "rendered latex"

    compiled_sources = []

    def compile_latex_fn(
        *,
        latex_source,
        work_directory,
    ):
        compiled_sources.append(
            (
                latex_source,
                work_directory,
            )
        )

        return LatexCompilationResult(
            page_count=1,
            pdf_path=work_directory / "resume.pdf",
            compiler_output=(
                "RESUME_CONTENT_HEIGHT_POINTS=650.0\n"
                "RESUME_USABLE_HEIGHT_POINTS=720.0\n"
            ),
        )

    measure_plan = create_plan_measurement_callback(
        profile=profile,
        tailoring_input=tailoring_input,
        generator=generator,
        work_directory=tmp_path,
        render_resume_fn=render_resume_fn,
        compile_latex_fn=compile_latex_fn,
    )

    plan = _plan(
        experience_bullets=3,
        project_bullets=2,
    )

    result = measure_plan(plan)

    assert len(generator.inputs) == 1

    generation_input = generator.inputs[0]

    assert generation_input.tailoring_input is tailoring_input
    assert generation_input.composition_plan == plan

    assert len(rendered_contents) == 1
    assert len(rendered_contents[0].experiences[0].bullets) == 3
    assert len(rendered_contents[0].projects[0].bullets) == 2

    assert compiled_sources == [
        (
            "rendered latex",
            tmp_path / "attempt_1",
        )
    ]

    assert result.page_count == 1
    assert result.content_height_points == 650.0
    assert result.usable_height_points == 720.0


def test_each_measurement_attempt_uses_fresh_generation_input(
    tmp_path,
):
    generator = FakeResumeContentGenerator()
    tailoring_input = _tailoring_input()

    compile_calls = []

    def compile_latex_fn(
        *,
        latex_source,
        work_directory,
    ):
        compile_calls.append(work_directory)

        return LatexCompilationResult(
            page_count=1,
            pdf_path=work_directory / "resume.pdf",
            compiler_output=(
                "RESUME_CONTENT_HEIGHT_POINTS=690.0\n"
                "RESUME_USABLE_HEIGHT_POINTS=720.0\n"
            ),
        )

    measure_plan = create_plan_measurement_callback(
        profile=object(),
        tailoring_input=tailoring_input,
        generator=generator,
        work_directory=tmp_path,
        render_resume_fn=lambda profile, content: "latex",
        compile_latex_fn=compile_latex_fn,
    )

    first_plan = _plan(
        experience_bullets=3,
        project_bullets=3,
    )

    second_plan = _plan(
        experience_bullets=3,
        project_bullets=2,
    )

    measure_plan(first_plan)
    measure_plan(second_plan)

    assert len(generator.inputs) == 2

    assert (
        generator.inputs[0].composition_plan
        == first_plan
    )
    assert (
        generator.inputs[1].composition_plan
        == second_plan
    )

    assert compile_calls == [
        tmp_path / "attempt_1",
        tmp_path / "attempt_2",
    ]


def test_generated_content_is_validated_before_rendering(
    tmp_path,
):
    tailoring_input = _tailoring_input()

    class InvalidGenerator:
        def generate(self, generation_input):
            return StructuredResumeContent(
                professional_summary=None,
                experiences=(
                    GeneratedExperienceContent(
                        experience_id=101,
                        bullets=("Only one bullet",),
                    ),
                ),
                projects=(
                    GeneratedProjectContent(
                        project_id=201,
                        bullets=(
                            "Project bullet 1",
                            "Project bullet 2",
                        ),
                    ),
                ),
                skills=("Python",),
            )

    render_called = False

    def render_resume_fn(profile, content):
        nonlocal render_called
        render_called = True
        return "latex"

    measure_plan = create_plan_measurement_callback(
        profile=object(),
        tailoring_input=tailoring_input,
        generator=InvalidGenerator(),
        work_directory=tmp_path,
        render_resume_fn=render_resume_fn,
        compile_latex_fn=lambda **kwargs: None,
    )

    try:
        measure_plan(
            _plan(
                experience_bullets=3,
                project_bullets=2,
            )
        )
    except ValueError as error:
        assert str(error) == (
            "Generated experience bullet count does not match "
            "the composition plan."
        )
    else:
        raise AssertionError(
            "Expected generated content validation to fail."
        )

    assert render_called is False


def test_compilation_result_is_converted_to_page_fit_result(
    tmp_path,
):
    def compile_latex_fn(
        *,
        latex_source,
        work_directory,
    ):
        return LatexCompilationResult(
            page_count=2,
            pdf_path=work_directory / "resume.pdf",
            compiler_output=(
                "RESUME_CONTENT_HEIGHT_POINTS=25.0\n"
                "RESUME_USABLE_HEIGHT_POINTS=722.7\n"
            ),
        )

    measure_plan = create_plan_measurement_callback(
        profile=object(),
        tailoring_input=_tailoring_input(),
        generator=FakeResumeContentGenerator(),
        work_directory=tmp_path,
        render_resume_fn=lambda profile, content: "latex",
        compile_latex_fn=compile_latex_fn,
    )

    result = measure_plan(_plan())

    assert result.page_count == 2
    assert result.content_height_points == 25.0
    assert result.usable_height_points == 722.7
    assert result.fits_one_page is False