from datetime import date

from src.candidate_profile.contracts import (
    CandidateAchievementRecord,
    CandidateExperienceRecord,
    CandidateProjectRecord,
    CandidateSkillRecord,
    SkillRecord,
)
from src.resume_tailoring.contracts import (
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.serialization import serialize_tailoring_input


def test_serialize_tailoring_input_separates_job_and_candidate_facts():
    tailoring_input = TailoringInput(
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
    )

    result = serialize_tailoring_input(tailoring_input)

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