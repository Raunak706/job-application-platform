import os

from google import genai

from src.candidate_profile.contracts import (
    CandidateExperienceRecord,
    CandidateSkillRecord,
    SkillRecord,
)
from src.resume_tailoring.contracts import (
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.gemini_content_generator import (
    GeminiResumeContentGenerator,
)
from src.resume_tailoring.validation import validate_generated_content


def main():
    tailoring_input = TailoringInput(
        candidate_id=999,
        job=TailoringJobContext(
            job_id=999,
            title="Data Engineer",
            company="Synthetic Company",
            description=(
                "Looking for a data engineer with Python and SQL "
                "experience building reliable data pipelines."
            ),
            location="New York",
            country="US",
            workplace_type="hybrid",
            employment_type="full_time",
            department="Engineering",
        ),
        professional_headline="Data Engineer",
        professional_summary=(
            "Data engineer focused on reliable data processing systems."
        ),
        experiences=(
            CandidateExperienceRecord(
                id=101,
                company="Synthetic Analytics",
                title="Data Engineer",
                employment_type="full_time",
                department="Data",
                location="New York",
                country="US",
                start_date=None,
                end_date=None,
                is_current=True,
                description=(
                    "Built Python and SQL data pipelines for analytics "
                    "workloads."
                ),
                verification_status="manual",
                visibility="resume_safe",
            ),
        ),
        projects=(),
        skills=(
            CandidateSkillRecord(
                id=201,
                skill=SkillRecord(
                    skill_id=301,
                    canonical_name="Python",
                    normalized_name="python",
                    category="programming_language",
                ),
                proficiency_level=None,
                experience_months=None,
                last_used_date=None,
                notes=None,
                verification_status="manual",
                visibility="resume_safe",
            ),
            CandidateSkillRecord(
                id=202,
                skill=SkillRecord(
                    skill_id=302,
                    canonical_name="SQL",
                    normalized_name="sql",
                    category="query_language",
                ),
                proficiency_level=None,
                experience_months=None,
                last_used_date=None,
                notes=None,
                verification_status="manual",
                visibility="resume_safe",
            ),
        ),
        achievements=(),
    )

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"],
    )

    generator = GeminiResumeContentGenerator(
        client=client,
        model="gemini-3.5-flash-lite",
    )

    content = generator.generate(tailoring_input)

    validate_generated_content(
        tailoring_input,
        content,
    )

    print(content)


if __name__ == "__main__":
    main()