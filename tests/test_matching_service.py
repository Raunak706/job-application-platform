from src.candidate_profile.contracts import (
    CandidateIdentity,
    CandidateProfileDetails,
    CandidateSkillRecord,
    CanonicalCandidateProfile,
    SkillRecord,
)
from src.database.models import Job
from src.matching.service import MatchingService


def make_profile():
    python_skill = CandidateSkillRecord(
        id=1,
        skill=SkillRecord(
            skill_id=10,
            canonical_name="Python",
            normalized_name="python",
            category="programming_language",
        ),
        proficiency_level=None,
        experience_months=None,
        last_used_date=None,
        notes=None,
        verification_status="verified",
        visibility="internal",
    )

    sql_skill = CandidateSkillRecord(
        id=2,
        skill=SkillRecord(
            skill_id=11,
            canonical_name="SQL",
            normalized_name="sql",
            category="programming_language",
        ),
        proficiency_level=None,
        experience_months=None,
        last_used_date=None,
        notes=None,
        verification_status="verified",
        visibility="internal",
    )

    return CanonicalCandidateProfile(
        identity=CandidateIdentity(
            candidate_id=1,
            display_name="Test Candidate",
            status="active",
        ),
        profile=CandidateProfileDetails(
            profile_id=1,
            professional_headline="Data Engineer",
            professional_summary=None,
            current_location="New Brunswick, NJ",
            current_country="US",
        ),
        contacts=(),
        links=(),
        experiences=(),
        projects=(),
        project_links=(),
        skills=(
            python_skill,
            sql_skill,
        ),
        experience_skills=(),
        project_skills=(),
        education=(),
        courses=(),
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


def make_job():
    return Job(
        id=10,
        raw_job_posting_id=None,
        title="Data Engineer",
        company="Example Company",
        location="New York, NY",
        country="US",
        workplace_type="hybrid",
        employment_type="full_time",
        department="Data",
        description="Build Python and SQL data pipelines.",
        source="test",
        source_job_id="job-10",
        source_url=None,
        apply_url=None,
    )


def test_matching_service_returns_structured_result():
    service = MatchingService()

    result = service.match(
        make_profile(),
        make_job(),
    )

    assert result.candidate_id == 1
    assert result.job_id == 10
    assert result.matcher_version == "v1"

    assert 0.0 <= result.overall_score <= 1.0
    assert 0.0 <= result.skill_score <= 1.0
    assert 0.0 <= result.title_relevance_score <= 1.0
    assert 0.0 <= result.evidence_score <= 1.0
    assert 0.0 <= result.compatibility_score <= 1.0

    assert result.matched_skills == (
        "python",
        "sql",
    )

    assert result.compatibility == (
        "location:compatible",
        "workplace:unknown",
        "employment_type:unknown",
    )

    assert result.reasons


def test_matching_service_is_deterministic():
    service = MatchingService()

    profile = make_profile()
    job = make_job()

    first = service.match(
        profile,
        job,
    )

    second = service.match(
        profile,
        job,
    )

    assert first == second

def test_matching_service_handles_missing_optional_candidate_and_job_data():
    profile = make_profile()

    profile = CanonicalCandidateProfile(
        identity=profile.identity,
        profile=CandidateProfileDetails(
            profile_id=1,
            professional_headline=None,
            professional_summary=None,
            current_location=None,
            current_country=None,
        ),
        contacts=(),
        links=(),
        experiences=(),
        projects=(),
        project_links=(),
        skills=(),
        experience_skills=(),
        project_skills=(),
        education=(),
        courses=(),
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

    job = Job(
        id=20,
        raw_job_posting_id=None,
        title="Data Analyst",
        company="Example Company",
        location=None,
        country=None,
        workplace_type=None,
        employment_type=None,
        department=None,
        description=None,
        source="test",
        source_job_id="job-20",
        source_url=None,
        apply_url=None,
    )

    result = MatchingService().match(
        profile,
        job,
    )

    assert result.candidate_id == 1
    assert result.job_id == 20
    assert result.matched_skills == ()
    assert result.missing_skills == ()
    assert result.supporting_experience_ids == ()
    assert result.supporting_project_ids == ()
    assert result.compatibility == (
        "location:unknown",
        "workplace:unknown",
        "employment_type:unknown",
    )
    