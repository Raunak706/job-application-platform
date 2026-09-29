from dataclasses import FrozenInstanceError

import pytest

from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
)


def test_structured_resume_content_stores_generated_sections():
    content = StructuredResumeContent(
        professional_summary=(
            "Data engineer focused on reliable data pipelines."
        ),
        experiences=(
            GeneratedExperienceContent(
                experience_id=101,
                bullets=(
                    "Built Python and SQL data pipelines.",
                    "Reduced pipeline failures by 50%.",
                ),
            ),
        ),
        projects=(
            GeneratedProjectContent(
                project_id=201,
                bullets=(
                    "Built a Python data processing platform.",
                ),
            ),
        ),
        skills=(
            "Python",
            "SQL",
        ),
    )

    assert content.professional_summary.startswith("Data engineer")
    assert content.experiences[0].experience_id == 101
    assert content.experiences[0].bullets == (
        "Built Python and SQL data pipelines.",
        "Reduced pipeline failures by 50%.",
    )
    assert content.projects[0].project_id == 201
    assert content.skills == ("Python", "SQL")


def test_structured_resume_content_allows_missing_optional_sections():
    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    assert content.professional_summary is None
    assert content.experiences == ()
    assert content.projects == ()
    assert content.skills == ()


def test_structured_resume_content_is_immutable():
    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    with pytest.raises(FrozenInstanceError):
        content.professional_summary = "Changed"