from datetime import date

import pytest

from src.candidate_profile.contracts import (
    CandidateContactRecord,
    CandidateCourseRecord,
    CandidateEducationRecord,
    CandidateExperienceRecord,
    CandidateIdentity,
    CandidateLinkRecord,
    CandidateProfileDetails,
    CandidateProjectRecord,
    CanonicalCandidateProfile,
)
from src.resume_tailoring.contracts import (
    GeneratedExperienceContent,
    GeneratedProjectContent,
    StructuredResumeContent,
)
from src.resume_tailoring.renderer import (
    escape_latex,
    load_resume_template,
    render_resume,
)


def make_profile(
    *,
    contacts=(),
    links=(),
    experiences=(),
    projects=(),
    education=(),
    courses=(),
):
    return CanonicalCandidateProfile(
        identity=CandidateIdentity(
            candidate_id=1,
            display_name="Example Candidate",
            status="active",
        ),
        profile=CandidateProfileDetails(
            profile_id=10,
            professional_headline="Data Engineer",
            professional_summary="Builds reliable data systems.",
            current_location="New York, NY",
            current_country="US",
        ),
        contacts=contacts,
        links=links,
        experiences=experiences,
        projects=projects,
        project_links=(),
        skills=(),
        experience_skills=(),
        project_skills=(),
        education=education,
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


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        ("R&D", r"R\&D"),
        ("50%", r"50\%"),
        ("cost $100", r"cost \$100"),
        ("data_engineer", r"data\_engineer"),
        ("C# developer", r"C\# developer"),
        ("{Python}", r"\{Python\}"),
        (r"C:\Users", r"C:\textbackslash{}Users"),
        ("A~B", r"A\textasciitilde{}B"),
        ("x^2", r"x\textasciicircum{}2"),
    ),
)
def test_escape_latex_escapes_special_characters(value, expected):
    assert escape_latex(value) == expected


def test_load_resume_template_loads_master_template():
    template = load_resume_template()

    assert r"\documentclass[10pt]{article}" in template
    assert "{{HEADER}}" in template
    assert "{{EDUCATION}}" in template
    assert "{{PROFESSIONAL_SUMMARY}}" in template
    assert "{{EXPERIENCE}}" in template
    assert "{{PROJECTS}}" in template
    assert "{{SKILLS}}" in template


def test_render_resume_renders_all_resume_sections():
    profile = make_profile(
        contacts=(
            CandidateContactRecord(
                id=1,
                contact_type="email",
                contact_value="candidate@example.com",
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
                link_type="github",
                url="https://github.com/example",
                label="GitHub",
                is_primary=True,
            ),
        ),
        education=(
            CandidateEducationRecord(
                id=301,
                institution="Example University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                education_level="bachelors",
                location="Example City",
                country="US",
                start_date=date(2022, 9, 1),
                end_date=None,
                graduation_date=date(2026, 5, 15),
                gpa="3.80",
                description=None,
                verification_status="verified",
                visibility="internal",
            ),
        ),
        courses=(
            CandidateCourseRecord(
                id=401,
                education_id=301,
                course_name="Introduction to Computer Science",
                course_code="CS101",
                grade="A",
                description=None,
            ),
        ),
        experiences=(
            CandidateExperienceRecord(
                id=101,
                company="Example & Co.",
                title="Data Engineer",
                employment_type="internship",
                department=None,
                location="New York, NY",
                country="US",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 5, 1),
                is_current=False,
                description="Built data systems.",
                verification_status="verified",
                visibility="internal",
            ),
        ),
        projects=(
            CandidateProjectRecord(
                id=201,
                name="Job Application Platform",
                role=None,
                organization=None,
                description="Job platform.",
                problem=None,
                solution=None,
                architecture=None,
                outcome=None,
                start_date=date(2025, 6, 1),
                end_date=None,
                status="active",
                verification_status="verified",
                visibility="internal",
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=(
            "Data engineer focused on reliable data processing systems."
        ),
        experiences=(
            GeneratedExperienceContent(
                experience_id=101,
                bullets=(
                    "Built Python & SQL data pipelines.",
                    "Validated production data.",
                ),
            ),
        ),
        projects=(
            GeneratedProjectContent(
                project_id=201,
                bullets=(
                    "Built a deterministic matching pipeline.",
                ),
            ),
        ),
        skills=("Python", "SQL", "PostgreSQL"),
    )

    rendered = render_resume(profile, content)

    assert r"\textbf{Example Candidate}" in rendered
    assert "New York, NY" in rendered
    assert "+1 (555) 123-4567" in rendered
    assert (
        r"\href{mailto:candidate@example.com}"
        r"{candidate@example.com}"
        in rendered
    )
    assert r"\href{https://github.com/example}{GitHub}" in rendered

    assert r"\section{Education}" in rendered
    assert "Example University" in rendered
    assert "Bachelor of Science in Computer Science" in rendered
    assert "May 2026" in rendered
    assert "GPA: 3.80" in rendered
    assert "CS101: Introduction to Computer Science" in rendered

    assert r"\section{Professional Summary}" in rendered
    assert (
        "Data engineer focused on reliable data processing systems."
        in rendered
    )

    assert r"\section{Experience}" in rendered
    assert r"Example \& Co." in rendered
    assert "Data Engineer" in rendered
    assert "Jan 2025 -- May 2025" in rendered
    assert r"Built Python \& SQL data pipelines." in rendered
    assert "Validated production data." in rendered

    assert r"\section{Projects}" in rendered
    assert "Job Application Platform" in rendered
    assert "Built a deterministic matching pipeline." in rendered

    assert r"\section{Skills}" in rendered
    assert "Python, SQL, PostgreSQL" in rendered

    assert "{{HEADER}}" not in rendered
    assert "{{EDUCATION}}" not in rendered
    assert "{{PROFESSIONAL_SUMMARY}}" not in rendered
    assert "{{EXPERIENCE}}" not in rendered
    assert "{{PROJECTS}}" not in rendered
    assert "{{SKILLS}}" not in rendered


def test_render_resume_omits_empty_optional_sections():
    profile = make_profile()

    content = StructuredResumeContent(
        professional_summary="",
        experiences=(),
        projects=(),
        skills=(),
    )

    rendered = render_resume(profile, content)

    assert r"\textbf{Example Candidate}" in rendered
    assert r"\section{Education}" not in rendered
    assert r"\section{Professional Summary}" not in rendered
    assert r"\section{Experience}" not in rendered
    assert r"\section{Projects}" not in rendered
    assert r"\section{Skills}" not in rendered

    assert "{{HEADER}}" not in rendered
    assert "{{EDUCATION}}" not in rendered
    assert "{{PROFESSIONAL_SUMMARY}}" not in rendered
    assert "{{EXPERIENCE}}" not in rendered
    assert "{{PROJECTS}}" not in rendered
    assert "{{SKILLS}}" not in rendered