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
    CandidateSkillRecord,
    CanonicalCandidateProfile,
    SkillRecord,
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


def make_candidate_skill(
    *,
    record_id,
    skill_id,
    name,
    category,
):
    return CandidateSkillRecord(
        id=record_id,
        skill=SkillRecord(
            skill_id=skill_id,
            canonical_name=name,
            normalized_name=name.casefold(),
            category=category,
        ),
        proficiency_level=None,
        experience_months=None,
        last_used_date=None,
        notes=None,
        verification_status="verified",
        visibility="internal",
    )


def make_profile(
    *,
    contacts=(),
    links=(),
    experiences=(),
    projects=(),
    skills=(),
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
        skills=skills,
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
    assert "{{EXPERIENCE}}" in template
    assert "{{PROJECTS}}" in template
    assert "{{SKILLS}}" in template


def test_render_resume_uses_original_resume_style_layout():
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
                degree="Master of Science",
                field_of_study="Data Science",
                education_level="masters",
                location="New York, NY",
                country="US",
                start_date=date(2024, 9, 1),
                end_date=None,
                graduation_date=date(2026, 5, 15),
                gpa="3.80",
                description=None,
                verification_status="verified",
                visibility="internal",
            ),
            CandidateEducationRecord(
                id=302,
                institution="Example Institute of Technology",
                degree="Bachelor of Technology",
                field_of_study="Computer Science",
                education_level="bachelors",
                location="Pune",
                country="India",
                start_date=date(2020, 8, 1),
                end_date=date(2024, 5, 1),
                graduation_date=date(2024, 5, 1),
                gpa="3.85",
                description=None,
                verification_status="verified",
                visibility="internal",
            ),
        ),
        courses=(
            CandidateCourseRecord(
                id=401,
                education_id=301,
                course_name="Machine Learning",
                course_code="DS501",
                grade="A",
                description=None,
            ),
            CandidateCourseRecord(
                id=402,
                education_id=301,
                course_name="Natural Language Processing",
                course_code="DS510",
                grade="A",
                description=None,
            ),
        ),
        experiences=(
            CandidateExperienceRecord(
                id=101,
                company="Example & Co.",
                title="Data Engineer Intern",
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
        skills=(
            make_candidate_skill(
                record_id=501,
                skill_id=601,
                name="Python",
                category="programming_language",
            ),
            make_candidate_skill(
                record_id=502,
                skill_id=602,
                name="SQL",
                category="programming_language",
            ),
            make_candidate_skill(
                record_id=503,
                skill_id=603,
                name="PostgreSQL",
                category="database",
            ),
            make_candidate_skill(
                record_id=504,
                skill_id=604,
                name="Machine Learning",
                category="machine_learning",
            ),
            make_candidate_skill(
                record_id=505,
                skill_id=605,
                name="Pandas",
                category="library",
            ),
            make_candidate_skill(
                record_id=506,
                skill_id=606,
                name="Docker",
                category="devops",
            ),
            make_candidate_skill(
                record_id=507,
                skill_id=607,
                name="Git",
                category="version_control",
            ),
            make_candidate_skill(
                record_id=508,
                skill_id=608,
                name="Azure",
                category="cloud",
            ),
            make_candidate_skill(
                record_id=509,
                skill_id=609,
                name="Excel",
                category="tool",
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
        skills=(
            "Python",
            "SQL",
            "PostgreSQL",
            "Machine Learning",
            "Pandas",
            "Docker",
            "Git",
            "Azure",
        ),
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
    assert (
        r"\href{https://github.com/example}{github.com/example}"
        in rendered
    )
    assert r"\section{Education}" in rendered
    assert (
        r"\textbf{Example University}, New York, NY"
        in rendered
    )
    assert (
        r"Master of Science in Data Science"
        in rendered
    )

    assert r"\hfill Sep 2024 -- May 2026" in rendered

    assert (
        r"\textbf{Example Institute of Technology}, Pune, India"
        in rendered
    )
    assert (
        r"Bachelor of Technology in Computer Science"
        in rendered
    )

    assert r"\hfill Aug 2020 -- May 2024" in rendered

    assert r"\textbf{Relevant Coursework:}" in rendered
    assert "DS501: Machine Learning" in rendered
    assert "DS510: Natural Language Processing" in rendered
    assert "GPA: 3.80" not in rendered
    assert "GPA: 3.85" not in rendered

    assert r"\section{Professional Summary}" not in rendered
    assert (
        "Data engineer focused on reliable data processing systems."
        in rendered
    )

    assert r"\section{Professional Experience}" in rendered
    assert (
        r"\textbf{Example \& Co.}, New York, NY"
        in rendered
    )
    assert r"\hfill Jan 2025 -- May 2025" in rendered
    assert r"\emph{Data Engineer Intern}" in rendered
    assert r"Built Python \& SQL data pipelines." in rendered
    assert "Validated production data." in rendered

    assert r"\section{Projects}" in rendered
    assert r"\textbf{Job Application Platform}" in rendered
    assert r"\hfill Jun 2025 -- Present" in rendered
    assert "Built a deterministic matching pipeline." in rendered

    assert r"\section{Technical and Other Skills}" in rendered

    assert (
        r"\textbf{Programming \& Data:} "
        r"Python, SQL, PostgreSQL"
        in rendered
    )
    assert (
        r"\textbf{ML \& AI:} "
        r"Machine Learning, Pandas"
        in rendered
    )
    assert (
        r"\textbf{Tools \& Platforms:} "
        r"Docker, Git, Azure"
        in rendered
    )

    assert "Excel" not in rendered

    assert "{{HEADER}}" not in rendered
    assert "{{EDUCATION}}" not in rendered
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
    assert r"\section{Professional Experience}" not in rendered
    assert r"\section{Projects}" not in rendered
    assert r"\section{Technical and Other Skills}" not in rendered

    assert "{{HEADER}}" not in rendered
    assert "{{EDUCATION}}" not in rendered
    assert "{{EXPERIENCE}}" not in rendered
    assert "{{PROJECTS}}" not in rendered
    assert "{{SKILLS}}" not in rendered

def test_render_resume_normalizes_markdown_email_contact():
    profile = make_profile(
        contacts=(
            CandidateContactRecord(
                id=1,
                contact_type="email",
                contact_value=(
                    "[candidate@example.com]"
                    "(mailto:candidate@example.com)"
                ),
                label="Personal",
                is_primary=True,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    rendered = render_resume(profile, content)

    assert (
        r"\href{mailto:candidate@example.com}"
        r"{candidate@example.com}"
        in rendered
    )

    assert "[candidate@example.com]" not in rendered
    assert "(mailto:candidate@example.com)" not in rendered

def test_render_education_uses_preserved_month_year_description():
    profile = make_profile(
        education=(
            CandidateEducationRecord(
                id=301,
                institution="Example University",
                degree="Master of Science",
                field_of_study="Data Science",
                education_level="masters",
                location=None,
                country=None,
                start_date=None,
                end_date=None,
                graduation_date=None,
                gpa=None,
                description="Sep 2024 – May 2026.",
                verification_status="verified",
                visibility="internal",
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    rendered = render_resume(profile, content)

    assert r"\hfill Sep 2024 -- May 2026" in rendered

def test_render_experiences_orders_newest_first_from_preserved_dates():
    older_experience = CandidateExperienceRecord(
        id=101,
        company="Older Company",
        title="Engineer",
        employment_type=None,
        department=None,
        location=None,
        country=None,
        start_date=None,
        end_date=None,
        is_current=False,
        description=(
            "Sep 2023 – Aug 2024. "
            "Built older systems."
        ),
        verification_status="verified",
        visibility="internal",
    )

    newer_experience = CandidateExperienceRecord(
        id=102,
        company="Newer Company",
        title="Engineer",
        employment_type=None,
        department=None,
        location=None,
        country=None,
        start_date=None,
        end_date=None,
        is_current=False,
        description=(
            "May 2025 – Aug 2025. "
            "Built newer systems."
        ),
        verification_status="verified",
        visibility="internal",
    )

    profile = make_profile(
        experiences=(
            older_experience,
            newer_experience,
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(
            GeneratedExperienceContent(
                experience_id=101,
                bullets=("Older bullet.",),
            ),
            GeneratedExperienceContent(
                experience_id=102,
                bullets=("Newer bullet.",),
            ),
        ),
        projects=(),
        skills=(),
    )

    rendered = render_resume(profile, content)

    assert rendered.index("Newer Company") < rendered.index(
        "Older Company"
    )
    assert r"\hfill May 2025 -- Aug 2025" in rendered
    assert r"\hfill Sep 2023 -- Aug 2024" in rendered


def test_render_projects_orders_newest_first_from_preserved_dates():
    older_project = CandidateProjectRecord(
        id=201,
        name="Older Project",
        role=None,
        organization=None,
        description="2023 project. Built older system.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status="completed",
        verification_status="verified",
        visibility="internal",
    )

    newer_project = CandidateProjectRecord(
        id=202,
        name="Newer Project",
        role=None,
        organization=None,
        description="2025 project. Built newer system.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status="completed",
        verification_status="verified",
        visibility="internal",
    )

    active_project = CandidateProjectRecord(
        id=203,
        name="Active Project",
        role=None,
        organization=None,
        description="Built active system.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status="active",
        verification_status="verified",
        visibility="internal",
    )

    profile = make_profile(
        projects=(
            older_project,
            newer_project,
            active_project,
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(
            GeneratedProjectContent(
                project_id=201,
                bullets=("Older bullet.",),
            ),
            GeneratedProjectContent(
                project_id=202,
                bullets=("Newer bullet.",),
            ),
            GeneratedProjectContent(
                project_id=203,
                bullets=("Active bullet.",),
            ),
        ),
        skills=(),
    )

    rendered = render_resume(profile, content)

    assert rendered.index("Active Project") < rendered.index(
        "Newer Project"
    )
    assert rendered.index("Newer Project") < rendered.index(
        "Older Project"
    )

    assert r"\hfill Present" in rendered
    assert r"\hfill 2025" in rendered
    assert r"\hfill 2023" in rendered


def test_render_header_skips_blank_links():
    profile = make_profile(
        links=(
            CandidateLinkRecord(
                id=1,
                link_type="linkedin",
                url="",
                label="LinkedIn",
                is_primary=True,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    rendered = render_resume(profile, content)

    assert "LinkedIn" not in rendered

def test_render_header_displays_link_url_and_keeps_it_clickable():
    profile = make_profile(
        links=(
            CandidateLinkRecord(
                id=1,
                link_type="linkedin",
                url="https://linkedin.com/in/raunaknair706",
                label="LinkedIn",
                is_primary=True,
            ),
        ),
    )

    content = StructuredResumeContent(
        professional_summary=None,
        experiences=(),
        projects=(),
        skills=(),
    )

    rendered = render_resume(profile, content)

    assert (
        r"\href{https://linkedin.com/in/raunaknair706}"
        r"{linkedin.com/in/raunaknair706}"
        in rendered
    )