from src.candidate_profile.contracts import (
    CandidateIdentity,
    CandidateProfileDetails,
    CandidateSkillRecord,
    CanonicalCandidateProfile,
    SkillRecord,
)
from src.matching.candidate_features import extract_candidate_features


def make_profile(
    *,
    candidate_id=1,
    skills=(),
):
    return CanonicalCandidateProfile(
        identity=CandidateIdentity(
            candidate_id=candidate_id,
            display_name="Test Candidate",
            status="active",
        ),
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
        skills=skills,
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


def test_extract_candidate_features_normalizes_skills():
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

    profile = make_profile(
        skills=(python_skill, sql_skill),
    )

    result = extract_candidate_features(profile)

    assert result.candidate_id == 1
    assert result.skills == ("python", "sql")


def test_extract_candidate_features_handles_no_skills():
    profile = make_profile(
        candidate_id=2,
    )

    result = extract_candidate_features(profile)

    assert result.candidate_id == 2
    assert result.skills == ()

def test_extract_candidate_features_includes_experience_and_project_evidence():
    from src.candidate_profile.contracts import (
        CandidateExperienceRecord,
        CandidateProjectRecord,
    )

    profile = make_profile(
        candidate_id=3,
    )

    profile = CanonicalCandidateProfile(
        identity=profile.identity,
        profile=profile.profile,
        contacts=profile.contacts,
        links=profile.links,
        experiences=(
            CandidateExperienceRecord(
                id=101,
                company="Example Company",
                title="Data Engineer",
                employment_type=None,
                department=None,
                location=None,
                country=None,
                start_date=None,
                end_date=None,
                is_current=False,
                description="Built Python and SQL data pipelines.",
                verification_status="verified",
                visibility="internal",
            ),
        ),
        projects=(
            CandidateProjectRecord(
                id=201,
                name="Analytics Platform",
                role=None,
                organization=None,
                description="Built a PostgreSQL analytics workflow.",
                problem=None,
                solution=None,
                architecture=None,
                outcome=None,
                start_date=None,
                end_date=None,
                status=None,
                verification_status="verified",
                visibility="internal",
            ),
        ),
        project_links=profile.project_links,
        skills=profile.skills,
        experience_skills=profile.experience_skills,
        project_skills=profile.project_skills,
        education=profile.education,
        courses=profile.courses,
        certifications=profile.certifications,
        awards=profile.awards,
        publications=profile.publications,
        activities=profile.activities,
        achievements=profile.achievements,
        preferences=profile.preferences,
        application_facts=profile.application_facts,
        stories=profile.stories,
        facts=profile.facts,
        evidence=profile.evidence,
        tags=profile.tags,
        entity_tags=profile.entity_tags,
        entity_relations=profile.entity_relations,
    )

    result = extract_candidate_features(profile)

    assert result.experiences == (
        (
            101,
            "Data Engineer",
            "Built Python and SQL data pipelines.",
        ),
    )

    assert result.projects == (
        (
            201,
            "Analytics Platform",
            "Built a PostgreSQL analytics workflow.",
        ),
    )

def test_extract_candidate_features_includes_location_and_active_preferences():
    from src.candidate_profile.contracts import CandidatePreferenceRecord

    base_profile = make_profile(
        candidate_id=4,
    )

    profile = CanonicalCandidateProfile(
        identity=base_profile.identity,
        profile=CandidateProfileDetails(
            profile_id=1,
            professional_headline=None,
            professional_summary=None,
            current_location="New Brunswick, NJ",
            current_country="US",
        ),
        contacts=base_profile.contacts,
        links=base_profile.links,
        experiences=base_profile.experiences,
        projects=base_profile.projects,
        project_links=base_profile.project_links,
        skills=base_profile.skills,
        experience_skills=base_profile.experience_skills,
        project_skills=base_profile.project_skills,
        education=base_profile.education,
        courses=base_profile.courses,
        certifications=base_profile.certifications,
        awards=base_profile.awards,
        publications=base_profile.publications,
        activities=base_profile.activities,
        achievements=base_profile.achievements,
        preferences=(
            CandidatePreferenceRecord(
                id=1,
                category="workplace",
                preference_key="workplace_types",
                value_json={
                    "values": ["remote", "hybrid"],
                },
                priority="high",
                is_active=True,
            ),
            CandidatePreferenceRecord(
                id=2,
                category="workplace",
                preference_key="ignored",
                value_json={
                    "values": ["onsite"],
                },
                priority=None,
                is_active=False,
            ),
        ),
        application_facts=base_profile.application_facts,
        stories=base_profile.stories,
        facts=base_profile.facts,
        evidence=base_profile.evidence,
        tags=base_profile.tags,
        entity_tags=base_profile.entity_tags,
        entity_relations=base_profile.entity_relations,
    )

    result = extract_candidate_features(profile)

    assert result.current_location == "new brunswick, nj"
    assert result.current_country == "us"
    assert result.preferences == (
        (
            "workplace",
            "workplace_types",
            {
                "values": ["remote", "hybrid"],
            },
            "high",
        ),
    )
