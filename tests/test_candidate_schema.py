from sqlalchemy import UniqueConstraint

from src.database.models import (
    Candidate,
    CandidateContact,
    CandidateExperience,
    CandidateFact,
    CandidateProfile,
    CandidateProject,
    CandidateSourceDocument,
)


def test_candidate_root_model_exists():
    assert Candidate.__tablename__ == "candidates"


def test_candidate_profile_has_candidate_foreign_key():
    column = CandidateProfile.__table__.c.candidate_id

    foreign_keys = list(column.foreign_keys)

    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "candidates.id"


def test_candidate_profile_is_one_to_one():
    column = CandidateProfile.__table__.c.candidate_id

    assert column.unique is True


def test_candidate_owned_entities_reference_candidate():
    models = [
        CandidateContact,
        CandidateExperience,
        CandidateProject,
        CandidateFact,
        CandidateSourceDocument,
    ]

    for model in models:
        column = model.__table__.c.candidate_id
        foreign_keys = list(column.foreign_keys)

        assert len(foreign_keys) == 1
        assert foreign_keys[0].target_fullname == "candidates.id"


def test_candidate_contacts_prevent_exact_duplicates():
    constraints = [
        constraint
        for constraint in CandidateContact.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    constraint_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in constraints
    }

    assert (
        "candidate_id",
        "contact_type",
        "contact_value",
    ) in constraint_columns


def test_source_documents_are_candidate_owned():
    table = CandidateSourceDocument.__table__

    assert "candidate_id" in table.c
    assert "content_hash" in table.c
    assert "storage_uri" in table.c
    assert "document_type" in table.c


def test_generic_candidate_fact_supports_extensible_values():
    table = CandidateFact.__table__

    assert "category" in table.c
    assert "fact_key" in table.c
    assert "value_text" in table.c
    assert "value_json" in table.c
    assert "verification_status" in table.c
    assert "confidence" in table.c
    assert "visibility" in table.c
    assert "is_sensitive" in table.c