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
