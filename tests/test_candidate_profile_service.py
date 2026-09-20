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
    CandidateLink,
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

        session.add_all([candidate_a, candidate_b])
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

    assert [contact.contact_value for contact in profile_a.contacts] == [
        "a@example.com"
    ]
    assert [contact.contact_value for contact in profile_b.contacts] == [
        "b@example.com"
    ]


def test_update_profile_details(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Update Test",
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

        candidate_id = candidate.id

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
    with session_factory() as session:
        candidate = Candidate(
            display_name="Contact Test",
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

        candidate_id = candidate.id

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


def test_add_link(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Link Test",
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

        candidate_id = candidate.id

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


def test_write_operations_do_not_cross_candidates(session_factory):
    with session_factory() as session:
        candidate_a = Candidate(
            display_name="Write Candidate A",
            status="active",
        )
        candidate_b = Candidate(
            display_name="Write Candidate B",
            status="active",
        )

        session.add_all([candidate_a, candidate_b])
        session.flush()

        session.add_all(
            [
                CandidateProfile(candidate_id=candidate_a.id),
                CandidateProfile(candidate_id=candidate_b.id),
            ]
        )

        session.commit()

        candidate_a_id = candidate_a.id
        candidate_b_id = candidate_b.id

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

    assert [contact.contact_value for contact in profile_a.contacts] == [
        "only-a@example.com"
    ]
    assert profile_a.links == ()

    assert profile_b.contacts == ()
    assert [link.url for link in profile_b.links] == [
        "https://linkedin.com/in/candidate-b"
    ]

def test_add_experience(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Experience Test",
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

        candidate_id = candidate.id

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
    with session_factory() as session:
        candidate = Candidate(
            display_name="Project Test",
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

        candidate_id = candidate.id

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

def test_add_education(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Education Test",
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

        candidate_id = candidate.id

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


def test_add_certification(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Certification Test",
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

        candidate_id = candidate.id

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


def test_add_achievement(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Achievement Test",
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

        candidate_id = candidate.id

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
    assert result.achievements[0].metric_text == "Reduced failures by 50%"


def test_achievement_rejects_other_candidates_parent(
    session_factory,
):
    with session_factory() as session:
        candidate_a = Candidate(
            display_name="Achievement Candidate A",
            status="active",
        )
        candidate_b = Candidate(
            display_name="Achievement Candidate B",
            status="active",
        )

        session.add_all([candidate_a, candidate_b])
        session.flush()

        session.add_all(
            [
                CandidateProfile(candidate_id=candidate_a.id),
                CandidateProfile(candidate_id=candidate_b.id),
            ]
        )

        session.commit()

        candidate_a_id = candidate_a.id
        candidate_b_id = candidate_b.id

    service = CandidateProfileService(
        session_factory=session_factory,
    )

    profile_a = service.add_experience(
        candidate_a_id,
        company="Candidate A Company",
        title="Engineer",
    )

    experience_a_id = profile_a.experiences[0].id

    with pytest.raises(CandidateProfileIntegrityError):
        service.add_achievement(
            candidate_b_id,
            experience_id=experience_a_id,
            description="Invalid cross-candidate achievement.",
        )


def test_add_preference(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Preference Test",
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

        candidate_id = candidate.id

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


def test_add_story(session_factory):
    with session_factory() as session:
        candidate = Candidate(
            display_name="Story Test",
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

        candidate_id = candidate.id

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
    with session_factory() as session:
        candidate = Candidate(
            display_name="Fact Test",
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

        candidate_id = candidate.id

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
