import os
from pathlib import Path

from google import genai

from src.candidate_profile.contracts import (
    CandidateContactRecord,
    CandidateExperienceRecord,
    CandidateIdentity,
    CandidateProfileDetails,
    CandidateSkillRecord,
    CanonicalCandidateProfile,
    SkillRecord,
)
from src.resume_tailoring.contracts import (
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.gemini_content_generator import (
    GeminiResumeContentGenerator,
)
from src.resume_tailoring.renderer import render_resume
from src.resume_tailoring.validation import validate_generated_content


def main():
    experience = CandidateExperienceRecord(
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
    )

    python_skill = CandidateSkillRecord(
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
    )

    sql_skill = CandidateSkillRecord(
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
    )

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
        experiences=(experience,),
        projects=(),
        skills=(python_skill, sql_skill),
        achievements=(),
    )

    profile = CanonicalCandidateProfile(
        identity=CandidateIdentity(
            candidate_id=999,
            display_name="Synthetic Candidate",
            status="active",
        ),
        profile=CandidateProfileDetails(
            profile_id=999,
            professional_headline="Data Engineer",
            professional_summary=(
                "Data engineer focused on reliable data processing systems."
            ),
            current_location="New York",
            current_country="US",
        ),
        contacts=(
            CandidateContactRecord(
                id=1,
                contact_type="email",
                contact_value="synthetic@example.com",
                label="Personal",
                is_primary=True,
            ),
        ),
        links=(),
        experiences=(experience,),
        projects=(),
        project_links=(),
        skills=(python_skill, sql_skill),
        experience_skills=(),
        project_skills=(),
        education=(),
        courses=(),
        certifications=(),
        awards=(),
        publications=(),
        activities=(),
        achievements=(),
        preferences=(),
        application_facts=(),
        stories=(),
        facts=(),
        evidence=(),
        tags=(),
        entity_tags=(),
        entity_relations=(),
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

    rendered_resume = render_resume(
        profile,
        content,
    )

    output_path = Path("/tmp/gemini_tailored_resume.tex")
    output_path.write_text(
        rendered_resume,
        encoding="utf-8",
    )

    print(content)
    print(f"\nRendered LaTeX: {output_path}")


if __name__ == "__main__":
    main()