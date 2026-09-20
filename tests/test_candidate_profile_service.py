import pytest
from sqlalchemy.orm import sessionmaker

from src.candidate_profile.repository import (
    CandidateNotFoundError,
    CandidateProfileIntegrityError,
)
from src.candidate_profile.service import CandidateProfileService
from src.database.models import (
    Candidate,
    CandidateContact,
    CandidateProfile,
)
from src.database.session import engine


@pytest.fixture
def session_factory():
    connection = engine.connect()
    transaction = connection.begin()

    factory = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
    )

    try:
        yield factory
    finally:
        transaction.rollback()
        connection.close()


def create_candidate(
    session_factory,
    display_name: str = "Test Candidate",
) -> int:
    with session_factory() as session:
        candidate = Candidate(
            display_name=display_name,
            status="active",
        )
        session.add(candidate)
        session.flush()

        session.add(
            CandidateProfile(
                candidate_id=candidate.id,
            )
        )

        session.commit()

        return candidate.id


def test_get_profile_returns_candidate_profile(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Test Candidate",
            status="active",
        )
        session.add(candidate)
        session.flush()

        profile = CandidateProfile(
            candidate_id=candidate.id,
            professional_headline="Data Engineer",
            professional_summary="Test summary",
            current_location="New Jersey",
            current_country="US",
        )
        session.add(profile)
        session.commit()

        candidate_id = candidate.id

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.get_profile(candidate_id)

    assert result.identity.candidate_id == candidate_id
    assert result.identity.display_name == "Test Candidate"
    assert result.identity.status == "active"
    assert result.profile.professional_headline == "Data Engineer"
    assert result.profile.professional_summary == "Test summary"
    assert result.profile.current_location == "New Jersey"
    assert result.profile.current_country == "US"


def test_get_profile_raises_when_candidate_does_not_exist(
    session_factory,
):
    service = CandidateProfileService(
        session_factory=session_factory,
    )

    with pytest.raises(CandidateNotFoundError):
        service.get_profile(999999999)


def test_get_profile_raises_when_profile_row_is_missing(
    session_factory,
):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Profile Missing",
            status="active",
        )
        session.add(candidate)
        session.commit()

        candidate_id = candidate.id

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    with pytest.raises(CandidateProfileIntegrityError):
        service.get_profile(candidate_id)


def test_get_profile_isolates_candidate_data(session_factory):
    with session_factory() as session:
        candidate_a = Candidate(
            display_name="Candidate A",
            status="active",
        )
        candidate_b = Candidate(
            display_name="Candidate B",
            status="active",
        )

        session.add_all(
            [
                candidate_a,
                candidate_b,
            ]
        )
        session.flush()

        session.add_all(
            [
                CandidateProfile(
                    candidate_id=candidate_a.id,
                    professional_headline="Engineer A",
                ),
                CandidateProfile(
                    candidate_id=candidate_b.id,
                    professional_headline="Engineer B",
                ),
            ]
        )

        session.add_all(
            [
                CandidateContact(
                    candidate_id=candidate_a.id,
                    contact_type="email",
                    contact_value="a@example.com",
                ),
                CandidateContact(
                    candidate_id=candidate_b.id,
                    contact_type="email",
                    contact_value="b@example.com",
                ),
            ]
        )

        session.commit()

        candidate_a_id = candidate_a.id
        candidate_b_id = candidate_b.id

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.get_profile(candidate_a_id)
    profile_b = service.get_profile(candidate_b_id)

    assert profile_a.identity.display_name == "Candidate A"
    assert profile_b.identity.display_name == "Candidate B"

    assert [
        contact.contact_value
        for contact in profile_a.contacts
    ] == ["a@example.com"]

    assert [
        contact.contact_value
        for contact in profile_b.contacts
    ] == ["b@example.com"]


def test_update_profile_details(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Update Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.update_profile_details(
        candidate_id,
        professional_headline="Analytics Engineer",
        professional_summary="Updated summary",
        current_location="New Brunswick",
        current_country="US",
    )

    assert result.profile.professional_headline == "Analytics Engineer"
    assert result.profile.professional_summary == "Updated summary"
    assert result.profile.current_location == "New Brunswick"
    assert result.profile.current_country == "US"


def test_add_contact(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Contact Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_contact(
        candidate_id,
        contact_type="email",
        contact_value="candidate@example.com",
        label="personal",
        is_primary=True,
    )

    assert len(result.contacts) == 1
    assert result.contacts[0].contact_type == "email"
    assert result.contacts[0].contact_value == "candidate@example.com"
    assert result.contacts[0].label == "personal"
    assert result.contacts[0].is_primary is True


def test_add_contact_is_idempotent(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Contact Idempotency Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    service.add_contact(
        candidate_id,
        contact_type="email",
        contact_value="same@example.com",
    )

    result = service.add_contact(
        candidate_id,
        contact_type="email",
        contact_value="same@example.com",
    )

    assert len(result.contacts) == 1


def test_add_link(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Link Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_link(
        candidate_id,
        link_type="github",
        url="https://github.com/example",
        label="GitHub",
        is_primary=True,
    )

    assert len(result.links) == 1
    assert result.links[0].link_type == "github"
    assert result.links[0].url == "https://github.com/example"
    assert result.links[0].label == "GitHub"
    assert result.links[0].is_primary is True


def test_add_link_is_idempotent(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Link Idempotency Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    service.add_link(
        candidate_id,
        link_type="linkedin",
        url="https://linkedin.com/in/example",
    )

    result = service.add_link(
        candidate_id,
        link_type="linkedin",
        url="https://linkedin.com/in/example",
    )

    assert len(result.links) == 1


def test_write_operations_do_not_cross_candidates(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Write Candidate A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Write Candidate B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    service.add_contact(
        candidate_a_id,
        contact_type="email",
        contact_value="only-a@example.com",
    )

    service.add_link(
        candidate_b_id,
        link_type="linkedin",
        url="https://linkedin.com/in/candidate-b",
    )

    profile_a = service.get_profile(candidate_a_id)
    profile_b = service.get_profile(candidate_b_id)

    assert [
        contact.contact_value
        for contact in profile_a.contacts
    ] == ["only-a@example.com"]

    assert profile_a.links == ()
    assert profile_b.contacts == ()

    assert [
        link.url
        for link in profile_b.links
    ] == ["https://linkedin.com/in/candidate-b"]


def test_add_experience(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Experience Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_experience(
        candidate_id,
        company="Example Company",
        title="Data Engineer",
        employment_type="full_time",
        location="New Jersey",
        country="US",
        description="Built data pipelines.",
        verification_status="verified",
        visibility="resume_safe",
    )

    assert len(result.experiences) == 1
    assert result.experiences[0].company == "Example Company"
    assert result.experiences[0].title == "Data Engineer"
    assert result.experiences[0].employment_type == "full_time"
    assert result.experiences[0].location == "New Jersey"
    assert result.experiences[0].country == "US"
    assert result.experiences[0].verification_status == "verified"
    assert result.experiences[0].visibility == "resume_safe"


def test_add_project(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Project Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_project(
        candidate_id,
        name="Job Application Platform",
        role="Developer",
        description="End-to-end job application system.",
        problem="Job application workflows were fragmented.",
        solution="Built a modular application platform.",
        architecture="PostgreSQL-backed modular Python services.",
        outcome="Created a reusable job application workflow.",
        status="active",
        verification_status="verified",
        visibility="resume_safe",
    )

    assert len(result.projects) == 1
    assert result.projects[0].name == "Job Application Platform"
    assert result.projects[0].role == "Developer"
    assert result.projects[0].status == "active"
    assert result.projects[0].verification_status == "verified"
    assert result.projects[0].visibility == "resume_safe"


def test_add_project_link(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Project Link Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile = service.add_project(
        candidate_id,
        name="Example Project",
    )

    project_id = profile.projects[0].id

    result = service.add_project_link(
        candidate_id,
        project_id=project_id,
        link_type="github",
        url="https://github.com/example/project",
        label="Repository",
    )

    assert len(result.project_links) == 1
    assert result.project_links[0].project_id == project_id
    assert result.project_links[0].link_type == "github"
    assert result.project_links[0].url == (
        "https://github.com/example/project"
    )


def test_project_link_rejects_other_candidates_project(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Project Link Candidate A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Project Link Candidate B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_project(
        candidate_a_id,
        name="Candidate A Project",
    )

    project_id = profile_a.projects[0].id

    with pytest.raises(CandidateProfileIntegrityError):
        service.add_project_link(
            candidate_b_id,
            project_id=project_id,
            link_type="github",
            url="https://github.com/invalid/project",
        )


def test_add_education(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Education Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_education(
        candidate_id,
        institution="Example University",
        degree="Bachelor of Science",
        field_of_study="Computer Science",
        education_level="bachelors",
        location="New Jersey",
        country="US",
        gpa="3.8",
        verification_status="verified",
        visibility="resume_safe",
    )

    assert len(result.education) == 1
    assert result.education[0].institution == "Example University"
    assert result.education[0].degree == "Bachelor of Science"
    assert result.education[0].field_of_study == "Computer Science"
    assert result.education[0].gpa == "3.8"
    assert result.education[0].verification_status == "verified"
    assert result.education[0].visibility == "resume_safe"


def test_add_course(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Course Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile = service.add_education(
        candidate_id,
        institution="Example University",
    )

    education_id = profile.education[0].id

    result = service.add_course(
        candidate_id,
        education_id=education_id,
        course_name="Database Systems",
        course_code="CS-401",
        grade="A",
        description="Relational database systems.",
    )

    assert len(result.courses) == 1
    assert result.courses[0].education_id == education_id
    assert result.courses[0].course_name == "Database Systems"
    assert result.courses[0].course_code == "CS-401"
    assert result.courses[0].grade == "A"


def test_course_rejects_other_candidates_education(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Course Candidate A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Course Candidate B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_education(
        candidate_a_id,
        institution="Candidate A University",
    )

    education_id = profile_a.education[0].id

    with pytest.raises(CandidateProfileIntegrityError):
        service.add_course(
            candidate_b_id,
            education_id=education_id,
            course_name="Invalid Course",
        )


def test_add_certification(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Certification Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_certification(
        candidate_id,
        name="Example Certification",
        issuer="Example Organization",
        credential_id="CERT-123",
        credential_url="https://example.com/certification",
        verification_status="verified",
        visibility="resume_safe",
    )

    assert len(result.certifications) == 1
    assert result.certifications[0].name == "Example Certification"
    assert result.certifications[0].issuer == "Example Organization"
    assert result.certifications[0].credential_id == "CERT-123"
    assert result.certifications[0].verification_status == "verified"


def test_add_award(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Award Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_award(
        candidate_id,
        name="Outstanding Project Award",
        issuer="Example University",
        description="Awarded for project work.",
        visibility="resume_safe",
    )

    assert len(result.awards) == 1
    assert result.awards[0].name == "Outstanding Project Award"
    assert result.awards[0].issuer == "Example University"
    assert result.awards[0].visibility == "resume_safe"


def test_add_publication(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Publication Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_publication(
        candidate_id,
        title="Example Publication",
        publication_type="paper",
        publisher="Example Publisher",
        url="https://example.com/publication",
        description="Example publication description.",
        visibility="resume_safe",
    )

    assert len(result.publications) == 1
    assert result.publications[0].title == "Example Publication"
    assert result.publications[0].publication_type == "paper"
    assert result.publications[0].publisher == "Example Publisher"


def test_add_activity(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Activity Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_activity(
        candidate_id,
        organization="Example Organization",
        role="Member",
        activity_type="student_organization",
        description="Participated in technical activities.",
        visibility="resume_safe",
    )

    assert len(result.activities) == 1
    assert result.activities[0].organization == "Example Organization"
    assert result.activities[0].role == "Member"
    assert result.activities[0].activity_type == "student_organization"


def test_add_achievement(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Achievement Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile = service.add_experience(
        candidate_id,
        company="Example Company",
        title="Data Engineer",
    )

    experience_id = profile.experiences[0].id

    result = service.add_achievement(
        candidate_id,
        experience_id=experience_id,
        title="Pipeline Improvement",
        description="Improved pipeline reliability.",
        metric_text="Reduced failures by 50%",
        verification_status="verified",
        visibility="resume_safe",
    )

    assert len(result.achievements) == 1
    assert result.achievements[0].experience_id == experience_id
    assert result.achievements[0].title == "Pipeline Improvement"
    assert result.achievements[0].metric_text == (
        "Reduced failures by 50%"
    )


def test_achievement_rejects_other_candidates_parent(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Achievement Candidate A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Achievement Candidate B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_experience(
        candidate_a_id,
        company="Candidate A Company",
        title="Engineer",
    )

    experience_id = profile_a.experiences[0].id

    with pytest.raises(CandidateProfileIntegrityError):
        service.add_achievement(
            candidate_b_id,
            experience_id=experience_id,
            description="Invalid cross-candidate achievement.",
        )


def test_add_preference(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Preference Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_preference(
        candidate_id,
        category="workplace",
        preference_key="workplace_types",
        value_json={
            "values": ["remote", "hybrid"],
        },
        priority="high",
    )

    assert len(result.preferences) == 1
    assert result.preferences[0].category == "workplace"
    assert result.preferences[0].preference_key == "workplace_types"
    assert result.preferences[0].value_json == {
        "values": ["remote", "hybrid"],
    }
    assert result.preferences[0].priority == "high"
    assert result.preferences[0].is_active is True


def test_add_preference_updates_existing_key(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Preference Update Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    service.add_preference(
        candidate_id,
        category="workplace",
        preference_key="workplace_types",
        value_json={
            "values": ["remote"],
        },
    )

    result = service.add_preference(
        candidate_id,
        category="workplace",
        preference_key="workplace_types",
        value_json={
            "values": ["hybrid"],
        },
        priority="high",
    )

    assert len(result.preferences) == 1
    assert result.preferences[0].value_json == {
        "values": ["hybrid"],
    }
    assert result.preferences[0].priority == "high"


def test_add_application_fact(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Application Fact Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_application_fact(
        candidate_id,
        fact_key="requires_sponsorship",
        category="work_authorization",
        question_text="Will you require sponsorship?",
        answer_text="No",
        is_sensitive=True,
        verification_status="verified",
        visibility="application_only",
    )

    assert len(result.application_facts) == 1
    assert result.application_facts[0].fact_key == (
        "requires_sponsorship"
    )
    assert result.application_facts[0].answer_text == "No"
    assert result.application_facts[0].is_sensitive is True
    assert result.application_facts[0].verification_status == "verified"


def test_add_application_fact_updates_existing_key(
    session_factory,
):
    candidate_id = create_candidate(
        session_factory,
        "Application Fact Update Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    service.add_application_fact(
        candidate_id,
        fact_key="example_fact",
        answer_text="Old answer",
    )

    result = service.add_application_fact(
        candidate_id,
        fact_key="example_fact",
        answer_text="Updated answer",
    )

    assert len(result.application_facts) == 1
    assert result.application_facts[0].answer_text == "Updated answer"


def test_add_story(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Story Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_story(
        candidate_id,
        title="Production Incident",
        story_type="star",
        situation="A production pipeline failed.",
        task="Restore processing safely.",
        action="Diagnosed and corrected the failure.",
        result="Processing recovered.",
        summary="Resolved a production pipeline incident.",
        verification_status="verified",
        visibility="internal",
    )

    assert len(result.stories) == 1
    assert result.stories[0].title == "Production Incident"
    assert result.stories[0].story_type == "star"
    assert result.stories[0].result == "Processing recovered."
    assert result.stories[0].verification_status == "verified"


def test_add_fact(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Fact Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_fact(
        candidate_id,
        category="eligibility",
        fact_key="work_authorization",
        value_text="Authorized to work in the United States",
        verification_status="verified",
        confidence=1.0,
        visibility="application_only",
        is_sensitive=True,
    )

    assert len(result.facts) == 1
    assert result.facts[0].category == "eligibility"
    assert result.facts[0].fact_key == "work_authorization"
    assert result.facts[0].verification_status == "verified"
    assert result.facts[0].confidence == 1.0
    assert result.facts[0].visibility == "application_only"
    assert result.facts[0].is_sensitive is True


def test_add_skill(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Skill Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_skill(
        candidate_id,
        skill_name="Python",
        category="programming_language",
        proficiency_level="advanced",
        experience_months=36,
        verification_status="verified",
        visibility="resume_safe",
    )

    assert len(result.skills) == 1
    assert result.skills[0].skill.canonical_name == "Python"
    assert result.skills[0].skill.normalized_name == "python"
    assert result.skills[0].proficiency_level == "advanced"
    assert result.skills[0].experience_months == 36
    assert result.skills[0].verification_status == "verified"


def test_add_skill_normalizes_and_reuses_existing_skill(
    session_factory,
):
    candidate_id = create_candidate(
        session_factory,
        "Skill Normalization Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    first = service.add_skill(
        candidate_id,
        skill_name="Python",
    )

    first_skill_id = first.skills[0].skill.skill_id

    result = service.add_skill(
        candidate_id,
        skill_name="  PYTHON  ",
        proficiency_level="advanced",
    )

    assert len(result.skills) == 1
    assert result.skills[0].skill.skill_id == first_skill_id
    assert result.skills[0].proficiency_level == "advanced"


def test_shared_skill_taxonomy_across_candidates(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Skill Candidate A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Skill Candidate B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_skill(
        candidate_a_id,
        skill_name="PostgreSQL",
    )

    profile_b = service.add_skill(
        candidate_b_id,
        skill_name="postgresql",
    )

    assert (
        profile_a.skills[0].skill.skill_id
        == profile_b.skills[0].skill.skill_id
    )


def test_add_experience_skill(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Experience Skill Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile = service.add_experience(
        candidate_id,
        company="Example Company",
        title="Engineer",
    )

    experience_id = profile.experiences[0].id

    profile = service.add_skill(
        candidate_id,
        skill_name="Python",
    )

    skill_id = profile.skills[0].skill.skill_id

    result = service.add_experience_skill(
        candidate_id,
        experience_id=experience_id,
        skill_id=skill_id,
        usage_description="Built Python data pipelines.",
    )

    assert len(result.experience_skills) == 1
    assert result.experience_skills[0].experience_id == experience_id
    assert result.experience_skills[0].skill.skill_id == skill_id
    assert result.experience_skills[0].usage_description == (
        "Built Python data pipelines."
    )


def test_experience_skill_rejects_other_candidates_experience(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Experience Skill Candidate A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Experience Skill Candidate B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_experience(
        candidate_a_id,
        company="Candidate A Company",
        title="Engineer",
    )

    experience_id = profile_a.experiences[0].id

    profile_b = service.add_skill(
        candidate_b_id,
        skill_name="Python",
    )

    skill_id = profile_b.skills[0].skill.skill_id

    with pytest.raises(CandidateProfileIntegrityError):
        service.add_experience_skill(
            candidate_b_id,
            experience_id=experience_id,
            skill_id=skill_id,
        )


def test_experience_skill_requires_candidate_skill(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Skill Owner A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Skill Owner B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_experience(
        candidate_a_id,
        company="Example Company",
        title="Engineer",
    )

    experience_id = profile_a.experiences[0].id

    profile_b = service.add_skill(
        candidate_b_id,
        skill_name="Python",
    )

    skill_id = profile_b.skills[0].skill.skill_id

    with pytest.raises(CandidateProfileIntegrityError):
        service.add_experience_skill(
            candidate_a_id,
            experience_id=experience_id,
            skill_id=skill_id,
        )


def test_add_project_skill(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Project Skill Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile = service.add_project(
        candidate_id,
        name="Example Project",
    )

    project_id = profile.projects[0].id

    profile = service.add_skill(
        candidate_id,
        skill_name="PostgreSQL",
    )

    skill_id = profile.skills[0].skill.skill_id

    result = service.add_project_skill(
        candidate_id,
        project_id=project_id,
        skill_id=skill_id,
        usage_description="Used PostgreSQL for persistence.",
    )

    assert len(result.project_skills) == 1
    assert result.project_skills[0].project_id == project_id
    assert result.project_skills[0].skill.skill_id == skill_id


def test_add_tag(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Tag Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = service.add_tag(
        candidate_id,
        name="data-engineering",
    )

    assert len(result.tags) == 1
    assert result.tags[0].name == "data-engineering"


def test_add_tag_is_idempotent(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Tag Idempotency Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    service.add_tag(
        candidate_id,
        name="backend",
    )

    result = service.add_tag(
        candidate_id,
        name="backend",
    )

    assert len(result.tags) == 1


def test_add_entity_tag(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Entity Tag Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile = service.add_project(
        candidate_id,
        name="Tagged Project",
    )

    project_id = profile.projects[0].id

    profile = service.add_tag(
        candidate_id,
        name="portfolio",
    )

    tag_id = profile.tags[0].id

    result = service.add_entity_tag(
        candidate_id,
        tag_id=tag_id,
        entity_type="project",
        entity_id=project_id,
    )

    assert len(result.entity_tags) == 1
    assert result.entity_tags[0].tag_id == tag_id
    assert result.entity_tags[0].entity_type == "project"
    assert result.entity_tags[0].entity_id == project_id


def test_entity_tag_rejects_other_candidates_entity(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Entity Tag Candidate A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Entity Tag Candidate B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_project(
        candidate_a_id,
        name="Candidate A Project",
    )

    project_id = profile_a.projects[0].id

    profile_b = service.add_tag(
        candidate_b_id,
        name="invalid",
    )

    tag_id = profile_b.tags[0].id

    with pytest.raises(CandidateProfileIntegrityError):
        service.add_entity_tag(
            candidate_b_id,
            tag_id=tag_id,
            entity_type="project",
            entity_id=project_id,
        )


def test_add_entity_relation(session_factory):
    candidate_id = create_candidate(
        session_factory,
        "Entity Relation Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile = service.add_experience(
        candidate_id,
        company="Example Company",
        title="Engineer",
    )

    experience_id = profile.experiences[0].id

    profile = service.add_project(
        candidate_id,
        name="Work Project",
    )

    project_id = profile.projects[0].id

    result = service.add_entity_relation(
        candidate_id,
        from_entity_type="experience",
        from_entity_id=experience_id,
        relation_type="includes_project",
        to_entity_type="project",
        to_entity_id=project_id,
        metadata_json={
            "source": "manual",
        },
    )

    assert len(result.entity_relations) == 1

    relation = result.entity_relations[0]

    assert relation.from_entity_type == "experience"
    assert relation.from_entity_id == experience_id
    assert relation.relation_type == "includes_project"
    assert relation.to_entity_type == "project"
    assert relation.to_entity_id == project_id
    assert relation.metadata_json == {
        "source": "manual",
    }


def test_entity_relation_rejects_cross_candidate_target(
    session_factory,
):
    candidate_a_id = create_candidate(
        session_factory,
        "Relation Candidate A",
    )
    candidate_b_id = create_candidate(
        session_factory,
        "Relation Candidate B",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_experience(
        candidate_a_id,
        company="Candidate A Company",
        title="Engineer",
    )

    experience_id = profile_a.experiences[0].id

    profile_b = service.add_project(
        candidate_b_id,
        name="Candidate B Project",
    )

    project_id = profile_b.projects[0].id

    with pytest.raises(CandidateProfileIntegrityError):
        service.add_entity_relation(
            candidate_a_id,
            from_entity_type="experience",
            from_entity_id=experience_id,
            relation_type="includes_project",
            to_entity_type="project",
            to_entity_id=project_id,
        )


def test_profile_can_load_multiple_canonical_domains(
    session_factory,
):
    candidate_id = create_candidate(
        session_factory,
        "Complete Profile Test",
    )

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    service.add_contact(
        candidate_id,
        contact_type="email",
        contact_value="complete@example.com",
    )

    service.add_link(
        candidate_id,
        link_type="github",
        url="https://github.com/complete",
    )

    service.add_experience(
        candidate_id,
        company="Example Company",
        title="Engineer",
    )

    service.add_project(
        candidate_id,
        name="Example Project",
    )

    service.add_education(
        candidate_id,
        institution="Example University",
    )

    service.add_certification(
        candidate_id,
        name="Example Certification",
    )

    service.add_award(
        candidate_id,
        name="Example Award",
    )

    service.add_publication(
        candidate_id,
        title="Example Publication",
    )

    service.add_activity(
        candidate_id,
        organization="Example Organization",
    )

    service.add_preference(
        candidate_id,
        category="role",
        preference_key="target_roles",
        value_json={
            "values": ["data engineer"],
        },
    )

    service.add_application_fact(
        candidate_id,
        fact_key="example_fact",
        answer_text="Example answer",
    )

    service.add_story(
        candidate_id,
        title="Example Story",
    )

    service.add_fact(
        candidate_id,
        category="general",
        fact_key="example",
        value_text="Example fact",
    )

    service.add_skill(
        candidate_id,
        skill_name="Python",
    )

    result = service.get_profile(candidate_id)

    assert len(result.contacts) == 1
    assert len(result.links) == 1
    assert len(result.experiences) == 1
    assert len(result.projects) == 1
    assert len(result.education) == 1
    assert len(result.certifications) == 1
    assert len(result.awards) == 1
    assert len(result.publications) == 1
    assert len(result.activities) == 1
    assert len(result.preferences) == 1
    assert len(result.application_facts) == 1
    assert len(result.stories) == 1
    assert len(result.facts) == 1
    assert len(result.skills) == 1