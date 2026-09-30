import pytest

from src.candidate_profile.contracts import (
    CandidateExperienceRecord,
    CandidateProjectRecord,
)
from src.resume_tailoring.composition import (
    ExperienceContentAllocation,
    ProjectContentAllocation,
    ResumeCompositionPlan,
)
from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    ResumeGenerationInput,
    StructuredResumeContent,
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.validation import validate_generated_content


def make_tailoring_input(
    *,
    experiences=(),
    projects=(),
):
    return TailoringInput(
        candidate_id=1,
        job=TailoringJobContext(
            job_id=10,
            title="Data Engineer",
            company="Example Employer",
            description="Build Python and SQL data pipelines.",
            location=None,
            country="US",
            workplace_type=None,
            employment_type=None,
            department=None,
        ),
        professional_headline="Data Engineer",
        professional_summary=None,
        experiences=experiences,
        projects=projects,
        skills=(),
        achievements=(),
    )


def make_experience(experience_id=1):
    return CandidateExperienceRecord(
        id=experience_id,
        company="Example Company",
        title="Data Engineer",
        employment_type=None,
        department=None,
        location=None,
        country=None,
        start_date=None,
        end_date=None,
        is_current=False,
        description="Built data pipelines.",
        verification_status="verified",
        visibility="internal",
    )


def make_project(project_id=2):
    return CandidateProjectRecord(
        id=project_id,
        name="Data Platform",
        role=None,
        organization=None,
        description="Built a data platform.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status=None,
        verification_status="verified",
        visibility="internal",
    )


def make_generation_input(
    *,
    experiences=(),
    projects=(),
    experience_allocations=(),
    project_allocations=(),
):
    return ResumeGenerationInput(
        tailoring_input=make_tailoring_input(
            experiences=experiences,
            projects=projects,
        ),
        composition_plan=ResumeCompositionPlan(
            experiences=experience_allocations,
            projects=project_allocations,
        ),
    )


def test_validate_generated_content_accepts_empty_safe_content():
    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    validate_generated_content(
        make_generation_input(),
        content,
    )


def test_validate_generated_content_accepts_exact_composition():
    experience = make_experience()
    project = make_project()

    generation_input = make_generation_input(
        experiences=(experience,),
        projects=(project,),
        experience_allocations=(
            ExperienceContentAllocation(
                experience_id=experience.id,
                target_bullets=3,
            ),
        ),
        project_allocations=(
            ProjectContentAllocation(
                project_id=project.id,
                target_bullets=2,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(
            GeneratedExperienceContent(
                experience_id=experience.id,
                bullets=(
                    "Built data pipelines.",
                    "Processed analytics data.",
                    "Maintained reliable workflows.",
                ),
            ),
        ),
        projects=(
            GeneratedProjectContent(
                project_id=project.id,
                bullets=(
                    "Built a data platform.",
                    "Implemented the approved project design.",
                ),
            ),
        ),
        skills=(),
    )

    validate_generated_content(
        generation_input,
        content,
    )


def test_validate_generated_content_rejects_unknown_experience_id():
    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(
            GeneratedExperienceContent(
                experience_id=999,
                bullets=("Built data pipelines.",),
            ),
        ),
        projects=(),
        skills=(),
    )

    with pytest.raises(ValueError, match="experience"):
        validate_generated_content(
            make_generation_input(),
            content,
        )


def test_validate_generated_content_rejects_unknown_project_id():
    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(
            GeneratedProjectContent(
                project_id=999,
                bullets=("Built a data platform.",),
            ),
        ),
        skills=(),
    )

    with pytest.raises(ValueError, match="project"):
        validate_generated_content(
            make_generation_input(),
            content,
        )


def test_validate_generated_content_rejects_unapproved_skill():
    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=("Apache Spark",),
    )

    with pytest.raises(ValueError, match="skill"):
        validate_generated_content(
            make_generation_input(),
            content,
        )


def test_validate_generated_content_rejects_blank_bullets():
    experience = make_experience()

    generation_input = make_generation_input(
        experiences=(experience,),
        experience_allocations=(
            ExperienceContentAllocation(
                experience_id=experience.id,
                target_bullets=2,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(
            GeneratedExperienceContent(
                experience_id=experience.id,
                bullets=(
                    "",
                    "Built data pipelines.",
                ),
            ),
        ),
        projects=(),
        skills=(),
    )

    with pytest.raises(ValueError, match="bullet"):
        validate_generated_content(
            generation_input,
            content,
        )


def test_validate_generated_content_rejects_missing_experience():
    experience = make_experience()

    generation_input = make_generation_input(
        experiences=(experience,),
        experience_allocations=(
            ExperienceContentAllocation(
                experience_id=experience.id,
                target_bullets=2,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    with pytest.raises(ValueError, match="experience"):
        validate_generated_content(
            generation_input,
            content,
        )


def test_validate_generated_content_rejects_missing_project():
    project = make_project()

    generation_input = make_generation_input(
        projects=(project,),
        project_allocations=(
            ProjectContentAllocation(
                project_id=project.id,
                target_bullets=2,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    with pytest.raises(ValueError, match="project"):
        validate_generated_content(
            generation_input,
            content,
        )


def test_validate_generated_content_rejects_duplicate_experience():
    experience = make_experience()

    generation_input = make_generation_input(
        experiences=(experience,),
        experience_allocations=(
            ExperienceContentAllocation(
                experience_id=experience.id,
                target_bullets=2,
            ),
        ),
    )

    generated_experience = GeneratedExperienceContent(
        experience_id=experience.id,
        bullets=(
            "Built data pipelines.",
            "Processed analytics data.",
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(
            generated_experience,
            generated_experience,
        ),
        projects=(),
        skills=(),
    )

    with pytest.raises(ValueError, match="experience"):
        validate_generated_content(
            generation_input,
            content,
        )


def test_validate_generated_content_rejects_duplicate_project():
    project = make_project()

    generation_input = make_generation_input(
        projects=(project,),
        project_allocations=(
            ProjectContentAllocation(
                project_id=project.id,
                target_bullets=2,
            ),
        ),
    )

    generated_project = GeneratedProjectContent(
        project_id=project.id,
        bullets=(
            "Built a data platform.",
            "Implemented the approved project design.",
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(
            generated_project,
            generated_project,
        ),
        skills=(),
    )

    with pytest.raises(ValueError, match="project"):
        validate_generated_content(
            generation_input,
            content,
        )


def test_validate_generated_content_rejects_wrong_experience_bullet_count():
    experience = make_experience()

    generation_input = make_generation_input(
        experiences=(experience,),
        experience_allocations=(
            ExperienceContentAllocation(
                experience_id=experience.id,
                target_bullets=3,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(
            GeneratedExperienceContent(
                experience_id=experience.id,
                bullets=(
                    "Built data pipelines.",
                    "Processed analytics data.",
                ),
            ),
        ),
        projects=(),
        skills=(),
    )

    with pytest.raises(ValueError, match="bullet"):
        validate_generated_content(
            generation_input,
            content,
        )


def test_validate_generated_content_rejects_wrong_project_bullet_count():
    project = make_project()

    generation_input = make_generation_input(
        projects=(project,),
        project_allocations=(
            ProjectContentAllocation(
                project_id=project.id,
                target_bullets=2,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(
            GeneratedProjectContent(
                project_id=project.id,
                bullets=("Built a data platform.",),
            ),
        ),
        skills=(),
    )

    with pytest.raises(ValueError, match="bullet"):
        validate_generated_content(
            generation_input,
            content,
        )