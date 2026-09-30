from datetime import date
from pathlib import Path

from src.candidate_profile.contracts import CanonicalCandidateProfile
from src.resume_tailoring.contracts import StructuredResumeContent


_TEMPLATE_PATH = (
    Path(__file__).parent
    / "templates"
    / "resume.tex"
)

_LATEX_ESCAPE_MAP = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_SKILL_DISPLAY_GROUPS = (
    (
        "Programming & Data",
        frozenset(
            {
                "programming_language",
                "database",
                "data_engineering",
                "data_processing",
                "data_platform",
                "analytics",
                "api",
                "data_format",
                "software_engineering",
            }
        ),
    ),
    (
        "ML & AI",
        frozenset(
            {
                "machine_learning",
                "data_science",
                "machine_learning_platform",
                "library",
            }
        ),
    ),
    (
        "Tools & Platforms",
        frozenset(
            {
                "cloud",
                "devops",
                "version_control",
                "operating_system",
                "testing",
                "tool",
                "database_tool",
            }
        ),
    ),
)


def escape_latex(value: str) -> str:
    return "".join(
        _LATEX_ESCAPE_MAP.get(character, character)
        for character in value
    )


def load_resume_template() -> str:
    return _TEMPLATE_PATH.read_text(encoding="utf-8")


def render_header(profile: CanonicalCandidateProfile) -> str:
    lines = [
        r"\begin{center}",
        (
            r"    {\Large \textbf{"
            + escape_latex(profile.identity.display_name)
            + r"}}\\[2pt]"
        ),
    ]

    if profile.profile.current_location:
        lines.append(
            "    "
            + escape_latex(profile.profile.current_location)
            + r"\\[-1pt]"
        )

    contact_items = []

    contacts = sorted(
        profile.contacts,
        key=lambda contact: (
            not contact.is_primary,
            contact.id,
        ),
    )

    for contact in contacts:
        value = escape_latex(contact.contact_value)

        if contact.contact_type.casefold() == "email":
            contact_items.append(
                rf"\href{{mailto:{value}}}{{{value}}}"
            )
        else:
            contact_items.append(value)

    links = sorted(
        profile.links,
        key=lambda link: (
            not link.is_primary,
            link.id,
        ),
    )

    for link in links:
        label = link.label or link.link_type.title()
        contact_items.append(
            rf"\href{{{link.url}}}{{{escape_latex(label)}}}"
        )

    if contact_items:
        lines.append(
            "    " + r" \,|\, ".join(contact_items)
        )

    lines.extend(
        (
            r"\end{center}",
            "",
            r"\vspace{0.3em}",
        )
    )

    return "\n".join(lines)


def render_education(profile: CanonicalCandidateProfile) -> str:
    if not profile.education:
        return ""

    lines = [r"\section{Education}"]

    for education in profile.education:
        degree = education.degree or ""
        field = education.field_of_study or ""

        if degree and field:
            degree_text = f"{degree} in {field}"
        else:
            degree_text = degree or field

        location = _format_location(
            education.location,
            education.country,
        )

        heading = (
            r"\textbf{"
            + escape_latex(education.institution)
            + "}"
        )

        if location:
            heading += ", " + escape_latex(location)

        if degree_text:
            heading += (
                r" \hfill "
                + escape_latex(degree_text)
            )

        lines.append(heading + r"\\")

    courses = list(profile.courses)

    if courses:
        course_text = ", ".join(
            _format_course(course)
            for course in courses
        )

        lines.append(r"\vspace{-2pt}")
        lines.append(
            r"\textbf{Relevant Coursework:} "
            + escape_latex(course_text)
        )

    return "\n".join(lines)


def render_professional_summary(
    content: StructuredResumeContent,
) -> str:
    return ""


def render_experience(
    profile: CanonicalCandidateProfile,
    content: StructuredResumeContent,
) -> str:
    if not content.experiences:
        return ""

    experiences_by_id = {
        experience.id: experience
        for experience in profile.experiences
    }

    lines = [r"\section{Professional Experience}"]

    for generated in content.experiences:
        experience = experiences_by_id.get(
            generated.experience_id
        )

        if experience is None:
            raise ValueError(
                "Generated experience is missing from "
                "canonical candidate profile."
            )

        location = _format_location(
            experience.location,
            experience.country,
        )

        heading = (
            r"\textbf{"
            + escape_latex(experience.company)
            + "}"
        )

        if location:
            heading += ", " + escape_latex(location)

        date_text = _format_date_range(
            experience.start_date,
            experience.end_date,
            experience.is_current,
        )

        if date_text:
            heading += (
                r" \hfill "
                + escape_latex(date_text)
            )

        lines.append(heading + r"\\")

        if experience.title:
            lines.append(
                r"\emph{"
                + escape_latex(experience.title)
                + "}"
            )

        lines.append(r"\begin{itemize}")

        for bullet in generated.bullets:
            lines.append(
                r"    \item " + escape_latex(bullet)
            )

        lines.append(r"\end{itemize}")

    return "\n".join(lines)


def render_projects(
    profile: CanonicalCandidateProfile,
    content: StructuredResumeContent,
) -> str:
    if not content.projects:
        return ""

    projects_by_id = {
        project.id: project
        for project in profile.projects
    }

    lines = [r"\section{Projects}"]

    for generated in content.projects:
        project = projects_by_id.get(
            generated.project_id
        )

        if project is None:
            raise ValueError(
                "Generated project is missing from "
                "canonical candidate profile."
            )

        heading = (
            r"\textbf{"
            + escape_latex(project.name)
            + "}"
        )

        date_text = _format_date_range(
            project.start_date,
            project.end_date,
            project.status.casefold() == "active"
            if project.status
            else False,
        )

        if date_text:
            heading += (
                r" \hfill "
                + escape_latex(date_text)
            )

        lines.append(heading)
        lines.append(r"\begin{itemize}")

        for bullet in generated.bullets:
            lines.append(
                r"    \item " + escape_latex(bullet)
            )

        lines.append(r"\end{itemize}")

    return "\n".join(lines)


def render_skills(
    profile: CanonicalCandidateProfile,
    content: StructuredResumeContent,
) -> str:
    if not content.skills:
        return ""

    canonical_skills = {
        candidate_skill.skill.canonical_name.casefold(): (
            candidate_skill.skill
        )
        for candidate_skill in profile.skills
    }

    grouped_skills = {
        display_name: []
        for display_name, _ in _SKILL_DISPLAY_GROUPS
    }

    uncategorized_skills = []

    for selected_skill in content.skills:
        skill_record = canonical_skills.get(
            selected_skill.casefold()
        )

        if skill_record is None:
            uncategorized_skills.append(selected_skill)
            continue

        category = skill_record.category
        matched_group = None

        if category:
            for display_name, categories in _SKILL_DISPLAY_GROUPS:
                if category in categories:
                    matched_group = display_name
                    break

        if matched_group is None:
            uncategorized_skills.append(selected_skill)
        else:
            grouped_skills[matched_group].append(selected_skill)

    lines = [r"\section{Technical and Other Skills}"]

    for display_name, _ in _SKILL_DISPLAY_GROUPS:
        skills = grouped_skills[display_name]

        if not skills:
            continue

        lines.append(
            r"\textbf{"
            + escape_latex(display_name)
            + r":} "
            + escape_latex(", ".join(skills))
            + r"\\"
        )

    if uncategorized_skills:
        lines.append(
            r"\textbf{Other:} "
            + escape_latex(", ".join(uncategorized_skills))
        )

    return "\n".join(lines)


def render_resume(
    profile: CanonicalCandidateProfile,
    content: StructuredResumeContent,
) -> str:
    rendered = load_resume_template()

    replacements = {
        "{{HEADER}}": render_header(profile),
        "{{EDUCATION}}": render_education(profile),
        "{{PROFESSIONAL_SUMMARY}}": (
            render_professional_summary(content)
        ),
        "{{EXPERIENCE}}": render_experience(
            profile,
            content,
        ),
        "{{PROJECTS}}": render_projects(
            profile,
            content,
        ),
        "{{SKILLS}}": render_skills(
            profile,
            content,
        ),
    }

    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    return rendered


def _format_month_year(value: date | None) -> str:
    if value is None:
        return ""

    return value.strftime("%b %Y")


def _format_date_range(
    start_date: date | None,
    end_date: date | None,
    is_current: bool,
) -> str:
    start = _format_month_year(start_date)

    if is_current:
        end = "Present"
    else:
        end = _format_month_year(end_date)

    if start and end:
        return f"{start} -- {end}"

    return start or end


def _format_course(course) -> str:
    if course.course_code and course.course_name:
        return f"{course.course_code}: {course.course_name}"

    return course.course_code or course.course_name


def _format_location(
    location: str | None,
    country: str | None,
) -> str:
    if location and country:
        if country.casefold() in location.casefold():
            return location
        return f"{location}, {country}"

    return location or country or ""