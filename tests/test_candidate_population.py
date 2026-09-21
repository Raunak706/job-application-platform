from datetime import date

import pytest
from sqlalchemy.orm import sessionmaker

from src.candidate_profile.management import CandidateManagementService
from src.candidate_profile.population import CandidatePopulationService
from src.candidate_profile.service import CandidateProfileService
from src.database.session import engine


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


def test_populate_candidate_from_structured_data(session_factory):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Population Test Candidate",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    data = {
        "profile": {
            "professional_headline": "Data Engineer",
            "professional_summary": "Builds data systems.",
            "current_location": "New Jersey",
            "current_country": "US",
        },
        "contacts": [
            {
                "contact_type": "email",
                "contact_value": "candidate@example.com",
                "label": "personal",
                "is_primary": True,
            }
        ],
        "links": [],
        "experiences": [],
        "projects": [],
        "education": [],
        "certifications": [],
        "awards": [],
        "publications": [],
        "activities": [],
        "skills": [],
        "preferences": [],
        "application_facts": [],
        "stories": [],
        "facts": [],
    }

    result = population.populate_candidate(
        candidate_id=candidate_id,
        data=data,
    )

    assert result.identity.candidate_id == candidate_id
    assert result.profile.professional_headline == "Data Engineer"
    assert result.profile.current_location == "New Jersey"

    assert len(result.contacts) == 1
    assert result.contacts[0].contact_value == (
        "candidate@example.com"
    )

    assert result.links == ()
    assert result.experiences == ()
    assert result.projects == ()


def test_population_parses_json_date_strings(session_factory):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Date Parsing Test",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    result = population.populate_candidate(
        candidate_id=candidate_id,
        data={
            "experiences": [
                {
                    "company": "Example Company",
                    "title": "Engineer",
                    "start_date": "2024-01-15",
                    "end_date": "2025-02-28",
                }
            ]
        },
    )

    assert result.experiences[0].start_date == date(
        2024,
        1,
        15,
    )

    assert result.experiences[0].end_date == date(
        2025,
        2,
        28,
    )


def test_population_rejects_invalid_date_strings(
    session_factory,
):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Invalid Date Test",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    with pytest.raises(ValueError):
        population.populate_candidate(
            candidate_id=candidate_id,
            data={
                "experiences": [
                    {
                        "company": "Example Company",
                        "title": "Engineer",
                        "start_date": "not-a-date",
                    }
                ]
            },
        )


def test_population_is_idempotent_for_experience(
    session_factory,
):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Idempotency Test",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    data = {
        "experiences": [
            {
                "company": "Example Company",
                "title": "Engineer",
                "start_date": "2024-01-01",
                "end_date": "2025-01-01",
            }
        ]
    }

    population.populate_candidate(
        candidate_id=candidate_id,
        data=data,
    )

    result = population.populate_candidate(
        candidate_id=candidate_id,
        data=data,
    )

    assert len(result.experiences) == 1


def test_population_failure_does_not_leave_partial_data(
    session_factory,
):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Atomic Population Test",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    with pytest.raises(ValueError):
        population.populate_candidate(
            candidate_id=candidate_id,
            data={
                "contacts": [
                    {
                        "contact_type": "email",
                        "contact_value": "partial@example.com",
                    }
                ],
                "experiences": [
                    {
                        "company": "Example Company",
                        "title": "Engineer",
                        "start_date": "invalid-date",
                    }
                ],
            },
        )

    profile_service = CandidateProfileService(
        session_factory=session_factory,
    )

    result = profile_service.get_profile(candidate_id)

    assert result.contacts == ()
    assert result.experiences == ()