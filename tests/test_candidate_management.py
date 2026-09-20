import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from src.candidate_profile.management import CandidateManagementService
from src.database.models import Candidate, CandidateProfile
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


def test_create_candidate_creates_candidate_and_profile(session_factory):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="New Candidate",
    )

    with session_factory() as session:
        candidate = session.get(
            Candidate,
            candidate_id,
        )

        profile = session.scalar(
            select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
        )

    assert candidate is not None
    assert candidate.display_name == "New Candidate"
    assert candidate.status == "active"

    assert profile is not None
    assert profile.candidate_id == candidate_id