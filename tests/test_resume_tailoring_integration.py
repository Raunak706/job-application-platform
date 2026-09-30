import pytest
from sqlalchemy.orm import sessionmaker

from src.candidate_profile.management import CandidateManagementService
from src.candidate_profile.population import CandidatePopulationService
from src.candidate_profile.service import CandidateProfileService
from src.database.models import Job
from src.database.session import engine
from src.matching.service import MatchingService
from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
)
from src.resume_tailoring.renderer import render_resume
from src.resume_tailoring.selector import build_tailoring_input
from src.resume_tailoring.validation import validate_generated_content


class FakeResumeContentGenerator:
    def generate(self, tailoring_input):
        experience = tailoring_input.experiences[0]
        project = tailoring_input.projects[0]

        return StructuredResumeContent(
            professional_summary=(
                "Data engineer focused on reliable data systems."
            ),
            experiences=(
                GeneratedExperienceContent(
                    experience_id=experience.id,
                    bullets=(
                        "Built Python and SQL data pipelines.",
                    ),
                ),
            ),
            projects=(
                GeneratedProjectContent(
                    project_id=project.id,
                    bullets=(
                        "Built a Python data processing platform.",
                    ),
                ),
            ),
            skills=tuple(
                skill.skill.canonical_name
                for skill in tailoring_input.skills
            ),
        )


@pytest.fixture
def session_factory():
    connection = engine.connect()
    transaction = connection.begin()

    factory = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield factory
    finally:
        transaction.rollback()
        connection.close()


def test_resume_tailoring_real_service_path(session_factory):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Resume Tailoring Candidate",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    population.populate_candidate(
        candidate_id=candidate_id,
        data={
            "profile": {
                "professional_headline": "Data Engineer",
                "professional_summary": (
                    "Builds reliable data systems."
                ),
                "current_location": "New Jersey",
                "current_country": "US",
            },
            "experiences": [
                {
                    "ref": "data_engineer_job",
                    "company": "Example Company",
                    "title": "Data Engineer",
                    "description": (
                        "Built Python and SQL data pipelines."
                    ),
                    "verification_status": "source_document",
                    "visibility": "internal",
                }
            ],
            "projects": [
                {
                    "ref": "data_platform",
                    "name": "Data Platform",
                    "description": (
                        "Built a Python data processing platform."
                    ),
                    "verification_status": "manual",
                    "visibility": "internal",
                }
            ],
            "skills": [
                {
                    "ref": "python",
                    "skill_name": "Python",
                    "category": "programming_language",
                    "verification_status": "source_document",
                    "visibility": "internal",
                },
                {
                    "ref": "sql",
                    "skill_name": "SQL",
                    "category": "query_language",
                    "verification_status": "source_document",
                    "visibility": "internal",
                },
                {
                    "ref": "spark",
                    "skill_name": "Apache Spark",
                    "category": "data_engineering",
                    "verification_status": "unverified",
                    "visibility": "internal",
                },
            ],
            "experience_skills": [
                {
                    "experience_ref": "data_engineer_job",
                    "skill_ref": "python",
                    "usage_description": (
                        "Used Python for data pipelines."
                    ),
                },
                {
                    "experience_ref": "data_engineer_job",
                    "skill_ref": "sql",
                    "usage_description": (
                        "Used SQL for data processing."
                    ),
                },
            ],
            "project_skills": [
                {
                    "project_ref": "data_platform",
                    "skill_ref": "python",
                    "usage_description": (
                        "Used Python to build the project."
                    ),
                }
            ],
            "achievements": [
                {
                    "ref": "pipeline_improvement",
                    "experience_ref": "data_engineer_job",
                    "title": "Pipeline Improvement",
                    "description": (
                        "Improved pipeline reliability."
                    ),
                    "metric_text": "Reduced failures by 50%.",
                    "verification_status": "source_document",
                    "visibility": "internal",
                }
            ],
        },
    )

    profile = CandidateProfileService(
        session_factory=session_factory,
    ).get_profile(candidate_id)

    job = Job(
        id=100,
        raw_job_posting_id=None,
        title="Data Engineer",
        company="Example Employer",
        location="New York, NY",
        country="US",
        workplace_type="hybrid",
        employment_type="full_time",
        department="Data",
        description=(
            "Build Python, SQL, and Apache Spark data pipelines."
        ),
        source="test",
        source_job_id="resume-tailoring-job",
        source_url=None,
        apply_url=None,
    )

    match_result = MatchingService().match(
        profile,
        job,
    )

    tailoring_input = build_tailoring_input(
        profile,
        job,
        match_result,
    )

    assert tailoring_input.candidate_id == candidate_id
    assert tailoring_input.job.job_id == 100

    assert len(tailoring_input.experiences) == 1
    assert tailoring_input.experiences[0].title == "Data Engineer"

    assert len(tailoring_input.projects) == 1
    assert tailoring_input.projects[0].name == "Data Platform"

    selected_skill_names = {
        skill.skill.normalized_name
        for skill in tailoring_input.skills
    }

    assert "python" in selected_skill_names
    assert "sql" in selected_skill_names
    assert "apache spark" not in selected_skill_names

    assert len(tailoring_input.achievements) == 1
    assert tailoring_input.achievements[0].metric_text == (
        "Reduced failures by 50%."
    )

    generator = FakeResumeContentGenerator()

    generated_content = generator.generate(
        tailoring_input,
    )

    validate_generated_content(
        tailoring_input,
        generated_content,
    )

    rendered_resume = render_resume(
        profile,
        generated_content,
    )

    assert r"\documentclass[10pt]{article}" in rendered_resume
    assert r"\textbf{Resume Tailoring Candidate}" in rendered_resume

    assert r"\section{Professional Summary}" in rendered_resume
    assert (
        "Data engineer focused on reliable data systems."
        in rendered_resume
    )

    assert r"\section{Experience}" in rendered_resume
    assert "Example Company" in rendered_resume
    assert "Data Engineer" in rendered_resume
    assert "Built Python and SQL data pipelines." in rendered_resume

    assert r"\section{Projects}" in rendered_resume
    assert "Data Platform" in rendered_resume
    assert (
        "Built a Python data processing platform."
        in rendered_resume
    )

    assert r"\section{Skills}" in rendered_resume
    assert "Python" in rendered_resume
    assert "SQL" in rendered_resume
    assert "Apache Spark" not in rendered_resume

    assert "{{HEADER}}" not in rendered_resume
    assert "{{EDUCATION}}" not in rendered_resume
    assert "{{PROFESSIONAL_SUMMARY}}" not in rendered_resume
    assert "{{EXPERIENCE}}" not in rendered_resume
    assert "{{PROJECTS}}" not in rendered_resume
    assert "{{SKILLS}}" not in rendered_resume