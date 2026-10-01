from types import SimpleNamespace

from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.fallback_orchestration import (
    generate_and_fit_with_fallback,
)
from src.resume_tailoring.page_fit import PageFitResult


def _experience(experience_id):
    return SimpleNamespace(
        id=experience_id,
        verification_status="verified",
        visibility="resume_safe",
    )


def _project(project_id):
    return SimpleNamespace(
        id=project_id,
        verification_status="verified",
        visibility="resume_safe",
    )


def _profile(
    *,
    experiences=(),
    projects=(),
):
    return SimpleNamespace(
        identity=SimpleNamespace(
            candidate_id=1,
        ),
        experiences=tuple(experiences),
        projects=tuple(projects),
        experience_skills=(),
        project_skills=(),
    )


def _tailoring_input(
    *,
    experiences=(),
    projects=(),
):
    return TailoringInput(
        candidate_id=1,
        job=TailoringJobContext(
            job_id=100,
            title="Data Engineer",
            company="Example Employer",
            description="Build data systems.",
            location=None,
            country=None,
            workplace_type=None,
            employment_type=None,
            department=None,
        ),
        professional_headline="Data Engineer",
        professional_summary=None,
        experiences=tuple(experiences),
        projects=tuple(projects),
        skills=(),
    )


def _match_result():
    return SimpleNamespace(
        candidate_id=1,
        job_id=100,
        matched_skills=(),
    )


def _generated_content(generation_input):
    return StructuredResumeContent(
        professional_summary=None,
        experiences=tuple(
            GeneratedExperienceContent(
                experience_id=allocation.experience_id,
                bullets=(
                    "experience bullet 1",
                    "experience bullet 2",
                    "experience bullet 3",
                    "experience bullet 4",
                ),
            )
            for allocation
            in generation_input.composition_plan.experiences
        ),
        projects=tuple(
            GeneratedProjectContent(
                project_id=allocation.project_id,
                bullets=(
                    "project bullet 1",
                    "project bullet 2",
                    "project bullet 3",
                    "project bullet 4",
                ),
            )
            for allocation
            in generation_input.composition_plan.projects
        ),
        skills=(),
    )


def _measurement(
    *,
    page_count=1,
    content_height=650.0,
):
    return PageFitResult(
        page_count=page_count,
        content_height_points=content_height,
        usable_height_points=720.0,
    )


class RecordingGenerator:
    def __init__(self):
        self.inputs = []

    def generate(self, generation_input):
        self.inputs.append(generation_input)
        return _generated_content(generation_input)


def test_target_strict_generation_uses_provider_once():
    experience = _experience(101)

    profile = _profile(
        experiences=(experience,),
    )
    tailoring_input = _tailoring_input(
        experiences=(experience,),
    )
    generator = RecordingGenerator()

    result = generate_and_fit_with_fallback(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=_match_result(),
        generator=generator,
        measure_content=lambda content: _measurement(),
    )

    assert len(generator.inputs) == 1
    assert result.generation_attempts == 1
    assert result.fallback_used is False
    assert result.tailoring_input == tailoring_input
    assert result.fit_result.fit_status == "target"


def test_local_overfull_trimming_does_not_regenerate():
    project = _project(201)

    profile = _profile(
        projects=(project,),
    )
    tailoring_input = _tailoring_input(
        projects=(project,),
    )
    generator = RecordingGenerator()

    measured_counts = []

    def measure_content(content):
        bullet_count = len(
            content.projects[0].bullets
        )
        measured_counts.append(bullet_count)

        if bullet_count > 2:
            return _measurement(
                page_count=2,
                content_height=730.0,
            )

        return _measurement()

    result = generate_and_fit_with_fallback(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=_match_result(),
        generator=generator,
        measure_content=measure_content,
    )

    assert measured_counts == [4, 3, 2]
    assert len(generator.inputs) == 1
    assert result.generation_attempts == 1
    assert result.fallback_used is False
    assert result.fit_result.fit_status == "target"


def test_underfill_broadens_evidence_and_uses_second_generation():
    selected_experience = _experience(101)
    fallback_project = _project(201)

    profile = _profile(
        experiences=(selected_experience,),
        projects=(fallback_project,),
    )
    tailoring_input = _tailoring_input(
        experiences=(selected_experience,),
    )
    generator = RecordingGenerator()

    measurement_calls = 0

    def measure_content(content):
        nonlocal measurement_calls
        measurement_calls += 1

        if measurement_calls == 1:
            return _measurement(
                content_height=400.0,
            )

        return _measurement()

    result = generate_and_fit_with_fallback(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=_match_result(),
        generator=generator,
        measure_content=measure_content,
    )

    assert len(generator.inputs) == 2
    assert result.generation_attempts == 2
    assert result.fallback_used is True

    assert tuple(
        project.id
        for project in result.tailoring_input.projects
    ) == (201,)

    assert result.fit_result.fit_status == "target"


def test_underfill_without_available_fallback_does_not_regenerate():
    experience = _experience(101)

    profile = _profile(
        experiences=(experience,),
    )
    tailoring_input = _tailoring_input(
        experiences=(experience,),
    )
    generator = RecordingGenerator()

    result = generate_and_fit_with_fallback(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=_match_result(),
        generator=generator,
        measure_content=lambda content: _measurement(
            content_height=400.0,
        ),
    )

    assert len(generator.inputs) == 1
    assert result.generation_attempts == 1
    assert result.fallback_used is False
    assert result.fit_result.fit_status == "underfilled"
    assert result.fit_result.adjustment_exhausted is True


def test_fallback_generation_is_limited_to_one_additional_provider_call():
    selected_experience = _experience(101)
    fallback_project = _project(201)

    profile = _profile(
        experiences=(selected_experience,),
        projects=(fallback_project,),
    )
    tailoring_input = _tailoring_input(
        experiences=(selected_experience,),
    )
    generator = RecordingGenerator()

    result = generate_and_fit_with_fallback(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=_match_result(),
        generator=generator,
        measure_content=lambda content: _measurement(
            content_height=400.0,
        ),
    )

    assert len(generator.inputs) == 2
    assert result.generation_attempts == 2
    assert result.fallback_used is True
    assert result.fit_result.fit_status == "underfilled"
    assert result.fit_result.adjustment_exhausted is True