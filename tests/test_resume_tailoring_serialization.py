from datetime import date

from src.candidate_profile.contracts import (
    CandidateAchievementRecord,
    CandidateExperienceRecord,
    CandidateExperienceSkillRecord,
    CandidateProjectRecord,
    CandidateProjectSkillRecord,
    CandidateSkillRecord,
    SkillRecord,
)
from src.resume_tailoring.composition import (
    ExperienceContentAllocation,
    ProjectContentAllocation,
    ResumeCompositionPlan,
)
from src.resume_tailoring.contracts import (
    ResumeGenerationInput,
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.serialization import (
    serialize_generation_input,
    serialize_tailoring_input,
)


def make_tailoring_input():
    python_skill = SkillRecord(
        skill_id=401,
        canonical_name="Python",
        normalized_name="python",
        category="programming_language",
    )

    return TailoringInput(
        candidate_id=1,
        job=TailoringJobContext(
            job_id=100,
            title="Data Engineer",
            company="Example Employer",
            description="Looking for Python and Spark experience.",
            location="New York",
            country="US",
            workplace_type="hybrid",
            employment_type="full_time",
            department="Engineering",
        ),
        professional_headline="Data Engineer",
        professional_summary="Builds reliable data systems.",
        experiences=(
            CandidateExperienceRecord(
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
                description="Built Python data pipelines.",
                verification_status="source_document",
                visibility="internal",
            ),
        ),
        projects=(
            CandidateProjectRecord(
                id=201,
                name="Data Platform",
                role=None,
                organization=None,
                description="Built a Python data processing platform.",
                problem=None,
                solution=None,
                architecture=None,
                outcome=None,
                start_date=None,
                end_date=None,
                status="active",
                verification_status="manual",
                visibility="internal",
            ),
        ),
        skills=(
            CandidateSkillRecord(
                id=301,
                skill=python_skill,
                proficiency_level=None,
                experience_months=None,
                last_used_date=None,
                notes=None,
                verification_status="verified",
                visibility="internal",
            ),
        ),
        achievements=(
            CandidateAchievementRecord(
                id=501,
                experience_id=101,
                project_id=None,
                title="Pipeline Reliability",
                description="Improved pipeline reliability.",
                metric_text="Reduced failures by 50%.",
                verification_status="source_document",
                visibility="internal",
            ),
        ),
        experience_skills=(
            CandidateExperienceSkillRecord(
                id=601,
                experience_id=101,
                skill=python_skill,
                usage_description="Used Python to build data pipelines.",
            ),
        ),
        project_skills=(
            CandidateProjectSkillRecord(
                id=602,
                project_id=201,
                skill=python_skill,
                usage_description="Used Python for project implementation.",
            ),
        ),
    )


def test_serialize_tailoring_input_separates_job_and_candidate_facts():
    result = serialize_tailoring_input(make_tailoring_input())

    assert result["job_context"]["description"] == (
        "Looking for Python and Spark experience."
    )

    candidate_facts = result["approved_candidate_facts"]

    assert candidate_facts["professional_headline"] == "Data Engineer"
    assert candidate_facts["experiences"][0]["experience_id"] == 101
    assert candidate_facts["experiences"][0]["description"] == (
        "Built Python data pipelines."
    )
    assert candidate_facts["projects"][0]["project_id"] == 201
    assert candidate_facts["skills"][0]["name"] == "Python"
    assert candidate_facts["achievements"][0]["metric_text"] == (
        "Reduced failures by 50%."
    )

    assert "Spark" not in candidate_facts["skills"]


def test_serialize_tailoring_input_includes_selected_skill_relationships():
    result = serialize_tailoring_input(make_tailoring_input())

    candidate_facts = result["approved_candidate_facts"]

    assert candidate_facts["experience_skills"] == [
        {
            "experience_id": 101,
            "skill_name": "Python",
            "normalized_name": "python",
            "category": "programming_language",
            "usage_description": "Used Python to build data pipelines.",
        },
    ]

    assert candidate_facts["project_skills"] == [
        {
            "project_id": 201,
            "skill_name": "Python",
            "normalized_name": "python",
            "category": "programming_language",
            "usage_description": "Used Python for project implementation.",
        },
    ]


def test_serialize_tailoring_input_handles_missing_optional_data():
    tailoring_input = TailoringInput(
        candidate_id=1,
        job=TailoringJobContext(
            job_id=100,
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
        achievements=(),
    )

    result = serialize_tailoring_input(tailoring_input)

    assert result["job_context"]["description"] is None
    assert result["job_context"]["location"] is None

    candidate_facts = result["approved_candidate_facts"]

    assert candidate_facts["professional_headline"] is None
    assert candidate_facts["professional_summary"] is None
    assert candidate_facts["experiences"] == []
    assert candidate_facts["projects"] == []
    assert candidate_facts["skills"] == []
    assert candidate_facts["achievements"] == []
    assert candidate_facts["experience_skills"] == []
    assert candidate_facts["project_skills"] == []


def test_serialize_generation_input_keeps_composition_guidance_separate():
    tailoring_input = make_tailoring_input()

    generation_input = ResumeGenerationInput(
        tailoring_input=tailoring_input,
        composition_plan=ResumeCompositionPlan(
            experiences=(
                ExperienceContentAllocation(
                    experience_id=101,
                    target_bullets=4,
                ),
            ),
            projects=(
                ProjectContentAllocation(
                    project_id=201,
                    target_bullets=2,
                ),
            ),
        ),
    )

    result = serialize_generation_input(generation_input)

    assert result["job_context"]["job_id"] == 100
    assert result["approved_candidate_facts"]["candidate_id"] == 1

    assert result["composition_guidance"] == {
        "experiences": [
            {
                "experience_id": 101,
                "target_bullets": 4,
            },
        ],
        "projects": [
            {
                "project_id": 201,
                "target_bullets": 2,
            },
        ],
    }

    assert (
        "composition_guidance"
        not in result["approved_candidate_facts"]
    )


def test_serialize_generation_input_handles_empty_composition_plan():
    generation_input = ResumeGenerationInput(
        tailoring_input=make_tailoring_input(),
        composition_plan=ResumeCompositionPlan(
            experiences=(),
            projects=(),
        ),
    )

    result = serialize_generation_input(generation_input)

    assert result["composition_guidance"] == {
        "experiences": [],
        "projects": [],
    }