from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from src.candidate_profile.contracts import (
    CandidateExperienceRecord,
    CandidateProjectRecord,
    CandidateSkillRecord,
    SkillRecord,
)
from src.resume_tailoring.contracts import (
    TailoringInput,
    TailoringJobContext,
)


def test_tailoring_input_stores_selected_canonical_facts():
    experience = CandidateExperienceRecord(
        id=101,
        company="Example Company",
        title="Data Engineer",
        employment_type="full_time",
        department=None,
        location="New York",
        country="US",
        start_date=date(2025, 1, 1),
        end_date=None,
        is_current=True,
        description="Built data pipelines.",
        verification_status="verified",
        visibility="resume",
    )

    project = CandidateProjectRecord(
        id=201,
        name="Job Application Platform",
        role=None,
        organization=None,
        description="Built a job application platform.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status="active",
        verification_status="verified",
        visibility="resume",
    )

    skill = CandidateSkillRecord(
        id=301,
        skill=SkillRecord(
            skill_id=401,
            canonical_name="Python",
            normalized_name="python",
            category="programming_language",
        ),
        proficiency_level=None,
        experience_months=None,
        last_used_date=None,
        notes=None,
        verification_status="verified",
        visibility="resume",
    )

    job = TailoringJobContext(
        job_id=10,
        title="Data Engineer",
        company="Example Employer",
        description="Build reliable Python data pipelines.",
        location="New York",
        country="US",
        workplace_type="hybrid",
        employment_type="full_time",
        department="Engineering",
    )

    tailoring_input = TailoringInput(
        candidate_id=1,
        job=job,
        professional_headline="Data Engineer",
        professional_summary="Data-focused software engineer.",
        experiences=(experience,),
        projects=(project,),
        skills=(skill,),
    )

    assert tailoring_input.candidate_id == 1
    assert tailoring_input.job.job_id == 10
    assert tailoring_input.job.title == "Data Engineer"
    assert tailoring_input.experiences == (experience,)
    assert tailoring_input.projects == (project,)
    assert tailoring_input.skills == (skill,)


def test_tailoring_input_allows_missing_optional_data():
    tailoring_input = TailoringInput(
        candidate_id=746,
        job=TailoringJobContext(
            job_id=20,
            title="Data Analyst",
            company="Example Employer",
            description=None,
            location=None,
            country=None,
            workplace_type=None,
            employment_type=None,
            department=None,
        ),
        professional_headline=None,
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    assert tailoring_input.professional_headline is None
    assert tailoring_input.professional_summary is None
    assert tailoring_input.job.description is None
    assert tailoring_input.experiences == ()
    assert tailoring_input.projects == ()
    assert tailoring_input.skills == ()


def test_tailoring_input_is_immutable():
    tailoring_input = TailoringInput(
        candidate_id=1,
        job=TailoringJobContext(
            job_id=10,
            title="Data Engineer",
            company="Example Employer",
            description=None,
            location=None,
            country=None,
            workplace_type=None,
            employment_type=None,
            department=None,
        ),
        professional_headline=None,
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    with pytest.raises(FrozenInstanceError):
        tailoring_input.candidate_id = 2