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

def test_population_is_idempotent_across_repeatable_domains(
    session_factory,
):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Broad Idempotency Test",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    data = {
        "projects": [
            {
                "name": "Example Project",
                "role": "Developer",
                "start_date": "2024-01-01",
                "end_date": "2024-06-01",
            }
        ],
        "education": [
            {
                "institution": "Example University",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
            }
        ],
        "certifications": [
            {
                "name": "Example Certification",
                "issuer": "Example Issuer",
            }
        ],
        "awards": [
            {
                "name": "Example Award",
                "issuer": "Example University",
            }
        ],
        "publications": [
            {
                "title": "Example Publication",
                "publisher": "Example Publisher",
            }
        ],
        "activities": [
            {
                "organization": "Example Organization",
                "role": "Member",
                "activity_type": "student_organization",
            }
        ],
        "stories": [
            {
                "title": "Example Story",
                "story_type": "star",
            }
        ],
        "facts": [
            {
                "category": "general",
                "fact_key": "example_fact",
                "value_text": "Example value",
            }
        ],
    }

    population.populate_candidate(
        candidate_id=candidate_id,
        data=data,
    )

    result = population.populate_candidate(
        candidate_id=candidate_id,
        data=data,
    )

    assert len(result.projects) == 1
    assert len(result.education) == 1
    assert len(result.certifications) == 1
    assert len(result.awards) == 1
    assert len(result.publications) == 1
    assert len(result.activities) == 1
    assert len(result.stories) == 1
    assert len(result.facts) == 1

def test_population_resolves_project_reference_for_project_link(
    session_factory,
):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Project Reference Test",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    result = population.populate_candidate(
        candidate_id=candidate_id,
        data={
            "projects": [
                {
                    "ref": "job_application_platform",
                    "name": "Job Application Platform",
                }
            ],
            "project_links": [
                {
                    "project_ref": "job_application_platform",
                    "link_type": "github",
                    "url": "https://github.com/example/project",
                    "label": "Repository",
                }
            ],
        },
    )

    assert len(result.projects) == 1
    assert len(result.project_links) == 1
    assert (
        result.project_links[0].project_id
        == result.projects[0].id
    )

def test_population_resolves_education_reference_for_course(
    session_factory,
):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Education Reference Test",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    result = population.populate_candidate(
        candidate_id=candidate_id,
        data={
            "education": [
                {
                    "ref": "rutgers_bs_cs",
                    "institution": "Rutgers University",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                }
            ],
            "courses": [
                {
                    "education_ref": "rutgers_bs_cs",
                    "course_code": "CS101",
                    "course_name": "Introduction to Computer Science",
                }
            ],
        },
    )

    assert len(result.education) == 1
    assert len(result.courses) == 1
    assert (
        result.courses[0].education_id
        == result.education[0].id
    )

def test_population_resolves_remaining_nested_references(
    session_factory,
):
    management = CandidateManagementService(
        session_factory=session_factory,
    )

    candidate_id = management.create_candidate(
        display_name="Nested Reference Test",
    )

    population = CandidatePopulationService(
        session_factory=session_factory,
    )

    data = {
        "experiences": [
            {
                "ref": "example_job",
                "company": "Example Company",
                "title": "Data Engineer",
            }
        ],
        "projects": [
            {
                "ref": "example_project",
                "name": "Example Project",
            }
        ],
        "skills": [
            {
                "ref": "python",
                "skill_name": "Python",
                "category": "programming_language",
            }
        ],
        "experience_skills": [
            {
                "experience_ref": "example_job",
                "skill_ref": "python",
                "usage_description": (
                    "Used Python for data engineering."
                ),
            }
        ],
        "project_skills": [
            {
                "project_ref": "example_project",
                "skill_ref": "python",
                "usage_description": (
                    "Used Python to build the project."
                ),
            }
        ],
        "achievements": [
            {
                "ref": "job_achievement",
                "experience_ref": "example_job",
                "title": "Automation",
                "description": (
                    "Automated a recurring data workflow."
                ),
            },
            {
                "ref": "project_achievement",
                "project_ref": "example_project",
                "title": "Project Delivery",
                "description": (
                    "Completed the project successfully."
                ),
            },
        ],
        "tags": [
            {
                "ref": "data_engineering",
                "name": "data-engineering",
            }
        ],
        "entity_tags": [
            {
                "tag_ref": "data_engineering",
                "entity_type": "experience",
                "entity_ref": "example_job",
            },
            {
                "tag_ref": "data_engineering",
                "entity_type": "project",
                "entity_ref": "example_project",
            },
        ],
        "entity_relations": [
            {
                "from_entity_type": "experience",
                "from_entity_ref": "example_job",
                "relation_type": "related_to",
                "to_entity_type": "project",
                "to_entity_ref": "example_project",
            }
        ],
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
    assert len(result.projects) == 1
    assert len(result.skills) == 1

    assert len(result.experience_skills) == 1
    assert len(result.project_skills) == 1

    assert len(result.achievements) == 2

    assert len(result.tags) == 1
    assert len(result.entity_tags) == 2
    assert len(result.entity_relations) == 1