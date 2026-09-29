import pytest

from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
    TailoringInput,
    TailoringJobContext,
)
from src.candidate_profile.contracts import CandidateExperienceRecord
from src.resume_tailoring.validation import validate_generated_content


def make_tailoring_input():
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
        experiences=(),
        projects=(),
        skills=(),
        achievements=(),
    )


def test_validate_generated_content_accepts_empty_safe_content():
    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    validate_generated_content(
        make_tailoring_input(),
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
            make_tailoring_input(),
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
            make_tailoring_input(),
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
            make_tailoring_input(),
            content,
        )


def test_validate_generated_content_rejects_blank_bullets():
    tailoring_input = TailoringInput(
        candidate_id=1,
        job=make_tailoring_input().job,
        professional_headline="Data Engineer",
        professional_summary=None,
        experiences=(
            CandidateExperienceRecord(
                id=1,
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
            ),
        ),
        projects=(),
        skills=(),
        achievements=(),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(
            GeneratedExperienceContent(
                experience_id=1,
                bullets=("",),
            ),
        ),
        projects=(),
        skills=(),
    )

    with pytest.raises(ValueError, match="bullet"):
        validate_generated_content(
            tailoring_input,
            content,
        )