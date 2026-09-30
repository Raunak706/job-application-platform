import os
from datetime import date
from pathlib import Path

from google import genai

from src.candidate_profile.contracts import (
    CandidateContactRecord,
    CandidateCourseRecord,
    CandidateEducationRecord,
    CandidateExperienceRecord,
    CandidateIdentity,
    CandidateLinkRecord,
    CandidateProfileDetails,
    CandidateProjectRecord,
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


def make_skill(
    candidate_skill_id,
    skill_id,
    name,
    normalized_name,
    category,
):
    return CandidateSkillRecord(
        id=candidate_skill_id,
        skill=SkillRecord(
            skill_id=skill_id,
            canonical_name=name,
            normalized_name=normalized_name,
            category=category,
        ),
        proficiency_level=None,
        experience_months=None,
        last_used_date=None,
        notes=None,
        verification_status="manual",
        visibility="resume_safe",
    )


def main():
    experience_one = CandidateExperienceRecord(
        id=101,
        company="Synthetic Intelligence Systems",
        title="Artificial Intelligence Intern",
        employment_type="internship",
        department="Applied AI",
        location="New York, NY",
        country="US",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 8, 31),
        is_current=False,
        description=(
            "Designed and tested a computer vision system for virtual "
            "product visualization using Python and deep learning, "
            "supporting realistic image transformations across a large "
            "evaluation dataset. "
            "Built an NLP pipeline using Python, transformers, and large "
            "language models to convert technical documents into structured "
            "records for downstream analytics and validation. "
            "Developed automated preprocessing and validation workflows "
            "that reduced repetitive manual review and improved consistency "
            "across incoming datasets. "
            "Collaborated with engineers to containerize development "
            "workflows with Docker and integrate model outputs into "
            "existing backend services."
        ),
        verification_status="manual",
        visibility="resume_safe",
    )

    experience_two = CandidateExperienceRecord(
        id=102,
        company="Synthetic Cloud Technologies",
        title="Cloud Computing and Machine Learning Intern",
        employment_type="internship",
        department="Cloud Engineering",
        location="Jersey City, NJ",
        country="US",
        start_date=date(2023, 9, 1),
        end_date=date(2024, 1, 31),
        is_current=False,
        description=(
            "Collaborated with a cross-functional engineering team to "
            "develop a cloud-based analytics system using Python, SQL, "
            "relational databases, and containerized services. "
            "Built data-processing logic to identify anomalies and natural "
            "breakpoints across large collections of structured and "
            "unstructured records. "
            "Created reusable ETL components for ingestion, cleaning, "
            "transformation, and validation while improving reliability "
            "of downstream analytics workflows. "
            "Developed monitoring and quality checks that reduced manual "
            "review requirements and helped identify processing failures "
            "earlier in the pipeline."
        ),
        verification_status="manual",
        visibility="resume_safe",
    )

    project_one = CandidateProjectRecord(
        id=201,
        name="Synthetic End-to-End Job Application Platform",
        role="Developer",
        organization=None,
        description=(
            "Designed a multi-stage job application platform using Python, "
            "PostgreSQL, SQLAlchemy, Alembic, Docker, and pytest. "
            "Implemented API-based job ingestion with normalization, "
            "validation, deduplication, enrichment, and canonical storage. "
            "Built a multi-user candidate knowledge base with structured "
            "experience, project, education, skill, evidence, and "
            "application information. "
            "Developed deterministic candidate-job matching and a "
            "provider-neutral AI resume-tailoring pipeline with structured "
            "generation, validation, and deterministic LaTeX rendering."
        ),
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=date(2025, 9, 1),
        end_date=None,
        status="active",
        verification_status="manual",
        visibility="resume_safe",
    )

    project_two = CandidateProjectRecord(
        id=202,
        name="Synthetic Real-Time Machine Learning Analytics System",
        role="Machine Learning Developer",
        organization=None,
        description=(
            "Developed an end-to-end classification system using Python, "
            "pandas, NumPy, scikit-learn, and statistical feature "
            "engineering for real-time predictive analytics. "
            "Built preprocessing workflows for filtering, missing-value "
            "handling, normalization, feature extraction, and reproducible "
            "train-test evaluation. "
            "Trained and compared multiple supervised machine learning "
            "models using cross-validation and quantitative performance "
            "metrics. "
            "Created visualizations with Matplotlib to analyze model "
            "behavior, feature distributions, prediction errors, and "
            "experimental results."
        ),
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 5, 31),
        status="completed",
        verification_status="manual",
        visibility="resume_safe",
    )

    project_three = CandidateProjectRecord(
        id=203,
        name="Synthetic Multimodal Language Processing System",
        role="Machine Learning Developer",
        organization=None,
        description=(
            "Designed a multimodal language-processing workflow combining "
            "speech recognition, natural language processing, embeddings, "
            "and transformer-based models. "
            "Built a preprocessing pipeline to transform raw inputs into "
            "structured representations suitable for model inference and "
            "downstream evaluation. "
            "Evaluated multiple modeling approaches using reproducible "
            "experiments and quantitative metrics to compare system "
            "performance and failure modes. "
            "Explored semantic representations and embedding-based "
            "similarity methods for connecting information across "
            "different input modalities."
        ),
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=date(2024, 9, 1),
        end_date=date(2024, 12, 31),
        status="completed",
        verification_status="manual",
        visibility="resume_safe",
    )

    skills = (
        make_skill(301, 401, "Python", "python", "programming_language"),
        make_skill(302, 402, "SQL", "sql", "query_language"),
        make_skill(303, 403, "PostgreSQL", "postgresql", "database"),
        make_skill(304, 404, "SQLAlchemy", "sqlalchemy", "database"),
        make_skill(305, 405, "Alembic", "alembic", "database"),
        make_skill(306, 406, "Docker", "docker", "devops"),
        make_skill(307, 407, "Git", "git", "developer_tool"),
        make_skill(308, 408, "GitHub", "github", "developer_tool"),
        make_skill(309, 409, "Linux", "linux", "operating_system"),
        make_skill(310, 410, "REST API", "rest api", "backend"),
        make_skill(311, 411, "JSON", "json", "data_format"),
        make_skill(312, 412, "pytest", "pytest", "testing"),
        make_skill(313, 413, "pandas", "pandas", "data_science"),
        make_skill(314, 414, "NumPy", "numpy", "data_science"),
        make_skill(
            315,
            415,
            "scikit-learn",
            "scikit-learn",
            "machine_learning",
        ),
        make_skill(
            316,
            416,
            "Matplotlib",
            "matplotlib",
            "visualization",
        ),
        make_skill(
            317,
            417,
            "Machine Learning",
            "machine learning",
            "machine_learning",
        ),
        make_skill(
            318,
            418,
            "Statistical Modeling",
            "statistical modeling",
            "data_science",
        ),
        make_skill(
            319,
            419,
            "Feature Engineering",
            "feature engineering",
            "machine_learning",
        ),
        make_skill(
            320,
            420,
            "Data Pipelines",
            "data pipelines",
            "data_engineering",
        ),
        make_skill(321, 421, "ETL", "etl", "data_engineering"),
        make_skill(
            322,
            422,
            "Data Validation",
            "data validation",
            "data_engineering",
        ),
        make_skill(
            323,
            423,
            "Data Cleaning",
            "data cleaning",
            "data_engineering",
        ),
        make_skill(
            324,
            424,
            "Transformers",
            "transformers",
            "machine_learning",
        ),
        make_skill(325, 425, "NLP", "nlp", "machine_learning"),
        make_skill(326, 426, "LLMs", "llms", "machine_learning"),
        make_skill(
            327,
            427,
            "Embeddings",
            "embeddings",
            "machine_learning",
        ),
        make_skill(
            328,
            428,
            "Semantic Search",
            "semantic search",
            "machine_learning",
        ),
    )

    education_one = CandidateEducationRecord(
        id=501,
        institution="Synthetic State University",
        degree="Master of Science",
        field_of_study="Data Science",
        education_level="masters",
        location="New Brunswick, NJ",
        country="US",
        start_date=date(2024, 9, 1),
        end_date=None,
        graduation_date=date(2026, 5, 15),
        gpa="3.80",
        description=None,
        verification_status="manual",
        visibility="resume_safe",
    )

    education_two = CandidateEducationRecord(
        id=502,
        institution="Synthetic Institute of Technology",
        degree="Bachelor of Technology",
        field_of_study="Computer Science",
        education_level="bachelors",
        location="Synthetic City",
        country="US",
        start_date=date(2020, 8, 1),
        end_date=date(2024, 5, 15),
        graduation_date=date(2024, 5, 15),
        gpa="3.85",
        description=None,
        verification_status="manual",
        visibility="resume_safe",
    )

    courses = (
        CandidateCourseRecord(
            id=601,
            education_id=501,
            course_name="Machine Learning",
            course_code="DS 501",
            grade="A",
            description=None,
        ),
        CandidateCourseRecord(
            id=602,
            education_id=501,
            course_name="Natural Language Processing",
            course_code="DS 510",
            grade="A",
            description=None,
        ),
        CandidateCourseRecord(
            id=603,
            education_id=501,
            course_name="Database Management Systems",
            course_code="CS 520",
            grade="A",
            description=None,
        ),
        CandidateCourseRecord(
            id=604,
            education_id=501,
            course_name="Statistical Inference",
            course_code="STAT 530",
            grade="A",
            description=None,
        ),
        CandidateCourseRecord(
            id=605,
            education_id=501,
            course_name="Time Series Analysis",
            course_code="STAT 540",
            grade="A",
            description=None,
        ),
        CandidateCourseRecord(
            id=606,
            education_id=501,
            course_name="Probability",
            course_code="STAT 550",
            grade="A",
            description=None,
        ),
        CandidateCourseRecord(
            id=607,
            education_id=501,
            course_name="Artificial Intelligence",
            course_code="CS 560",
            grade="A",
            description=None,
        ),
    )

    tailoring_input = TailoringInput(
        candidate_id=999,
        job=TailoringJobContext(
            job_id=999,
            title="Data Engineer",
            company="Synthetic Technology Company",
            description=(
                "Seeking a data engineer with strong Python, SQL, "
                "PostgreSQL, ETL, data pipeline, Docker, analytics, "
                "machine learning, data validation, and cloud engineering "
                "experience. The engineer will design reliable data "
                "processing systems, build production pipelines, validate "
                "large datasets, develop backend integrations, support "
                "analytics workloads, and collaborate with data science "
                "and machine learning teams."
            ),
            location="New York, NY",
            country="US",
            workplace_type="hybrid",
            employment_type="full_time",
            department="Data Engineering",
        ),
        professional_headline="Data Engineer",
        professional_summary=(
            "Data engineer and computer science graduate focused on "
            "reliable data platforms, machine learning systems, analytics, "
            "and production-quality software engineering."
        ),
        experiences=(
            experience_one,
            experience_two,
        ),
        projects=(
            project_one,
            project_two,
            project_three,
        ),
        skills=skills,
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
                "Data engineer and computer science graduate focused on "
                "reliable data platforms, machine learning systems, "
                "analytics, and production-quality software engineering."
            ),
            current_location="New York, NY",
            current_country="US",
        ),
        contacts=(
            CandidateContactRecord(
                id=1,
                contact_type="email",
                contact_value="synthetic.candidate@example.com",
                label="Personal",
                is_primary=True,
            ),
            CandidateContactRecord(
                id=2,
                contact_type="phone",
                contact_value="+1 (555) 123-4567",
                label="Mobile",
                is_primary=True,
            ),
        ),
        links=(
            CandidateLinkRecord(
                id=1,
                link_type="linkedin",
                url="https://www.linkedin.com/in/synthetic-candidate",
                label="LinkedIn",
                is_primary=True,
            ),
            CandidateLinkRecord(
                id=2,
                link_type="github",
                url="https://github.com/synthetic-candidate",
                label="GitHub",
                is_primary=True,
            ),
        ),
        experiences=(
            experience_one,
            experience_two,
        ),
        projects=(
            project_one,
            project_two,
            project_three,
        ),
        project_links=(),
        skills=skills,
        experience_skills=(),
        project_skills=(),
        education=(
            education_one,
            education_two,
        ),
        courses=courses,
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