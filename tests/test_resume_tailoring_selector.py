from datetime import date

import pytest

from src.candidate_profile.contracts import (
    CandidateAchievementRecord,
    CandidateExperienceRecord,
    CandidateIdentity,
    CandidateProfileDetails,
    CandidateProjectRecord,
    CandidateSkillRecord,
    CanonicalCandidateProfile,
    SkillRecord,
)

from src.database.models import Job
from src.matching.contracts import CandidateJobMatchResult
from src.resume_tailoring.selector import build_tailoring_input


def make_profile(
    *,
    candidate_id=1,
    experiences=(),
    projects=(),
    skills=(),
):
    return CanonicalCandidateProfile(
        identity=CandidateIdentity(
            candidate_id=candidate_id,
            display_name="Example Candidate",
            status="active",
        ),
        profile=CandidateProfileDetails(
            profile_id=10,
            professional_headline="Data Engineer",
            professional_summary="Builds reliable data systems.",
            current_location="New York",
            current_country="US",
        ),
        contacts=(),
        links=(),
        experiences=experiences,
        projects=projects,
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


def make_job(*, job_id=100, description="Build Python data pipelines."):
    job = Job()
    job.id = job_id
    job.title = "Data Engineer"
    job.company = "Example Employer"
    job.description = description
    job.location = "New York"
    job.country = "US"
    job.workplace_type = "hybrid"
    job.employment_type = "full_time"
    job.department = "Engineering"
    job.source = "test"
    job.source_job_id = str(job_id)
    return job


def make_match(
    *,
    candidate_id=1,
    job_id=100,
    matched_skills=(),
    supporting_experience_ids=(),
    supporting_project_ids=(),
):
    return CandidateJobMatchResult(
        candidate_id=candidate_id,
        job_id=job_id,
        matcher_version="v1",
        overall_score=0.75,
        skill_score=0.75,
        title_relevance_score=0.75,
        evidence_score=0.75,
        compatibility_score=0.75,
        matched_skills=matched_skills,
        missing_skills=(),
        supporting_experience_ids=supporting_experience_ids,
        supporting_project_ids=supporting_project_ids,
        compatibility=(),
        reasons=(),
    )


def test_build_tailoring_input_selects_supported_approved_facts():
    experience = CandidateExperienceRecord(
        id=101,
        company="Example Company",
        title="Data Engineer",
        employment_type="full_time",
        department=None,
        location="New York",
        country="US",
        start_date=date(2025, 1, 1),
        end_date=None,
        is_current=True,
        description="Built Python data pipelines.",
        verification_status="source_document",
        visibility="internal",
    )

    project = CandidateProjectRecord(
        id=201,
        name="Data Platform",
        role=None,
        organization=None,
        description="Built a data processing platform.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status="active",
        verification_status="manual",
        visibility="internal",
    )

    skill = CandidateSkillRecord(
        id=301,
        skill=SkillRecord(
            skill_id=401,
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

    result = build_tailoring_input(
        make_profile(
            experiences=(experience,),
            projects=(project,),
            skills=(skill,),
        ),
        make_job(),
        make_match(
            matched_skills=("python",),
            supporting_experience_ids=(101,),
            supporting_project_ids=(201,),
        ),
    )

    assert result.experiences == (experience,)
    assert result.projects == (project,)
    assert result.skills == (skill,)


def test_build_tailoring_input_excludes_unverified_facts():
    experience = CandidateExperienceRecord(
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
        description="Planned experience.",
        verification_status="unverified",
        visibility="internal",
    )

    project = CandidateProjectRecord(
        id=201,
        name="Planned Project",
        role=None,
        organization=None,
        description="Planned project work.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status=None,
        verification_status="unverified",
        visibility="internal",
    )

    skill = CandidateSkillRecord(
        id=301,
        skill=SkillRecord(
            skill_id=401,
            canonical_name="Apache Spark",
            normalized_name="apache spark",
            category=None,
        ),
        proficiency_level=None,
        experience_months=None,
        last_used_date=None,
        notes=None,
        verification_status="unverified",
        visibility="internal",
    )

    result = build_tailoring_input(
        make_profile(
            experiences=(experience,),
            projects=(project,),
            skills=(skill,),
        ),
        make_job(),
        make_match(
            matched_skills=("apache spark",),
            supporting_experience_ids=(101,),
            supporting_project_ids=(201,),
        ),
    )

    assert result.experiences == ()
    assert result.projects == ()
    assert result.skills == ()


def test_build_tailoring_input_selects_only_match_supported_records():
    relevant_experience = CandidateExperienceRecord(
        id=101,
        company="Relevant Company",
        title="Data Engineer",
        employment_type=None,
        department=None,
        location=None,
        country=None,
        start_date=None,
        end_date=None,
        is_current=False,
        description=None,
        verification_status="verified",
        visibility="internal",
    )

    unrelated_experience = CandidateExperienceRecord(
        id=102,
        company="Other Company",
        title="Other Role",
        employment_type=None,
        department=None,
        location=None,
        country=None,
        start_date=None,
        end_date=None,
        is_current=False,
        description=None,
        verification_status="verified",
        visibility="internal",
    )

    python_skill = CandidateSkillRecord(
        id=301,
        skill=SkillRecord(
            skill_id=401,
            canonical_name="Python",
            normalized_name="python",
            category=None,
        ),
        proficiency_level=None,
        experience_months=None,
        last_used_date=None,
        notes=None,
        verification_status="verified",
        visibility="internal",
    )

    sql_skill = CandidateSkillRecord(
        id=302,
        skill=SkillRecord(
            skill_id=402,
            canonical_name="SQL",
            normalized_name="sql",
            category=None,
        ),
        proficiency_level=None,
        experience_months=None,
        last_used_date=None,
        notes=None,
        verification_status="verified",
        visibility="internal",
    )

    result = build_tailoring_input(
        make_profile(
            experiences=(relevant_experience, unrelated_experience),
            skills=(python_skill, sql_skill),
        ),
        make_job(),
        make_match(
            matched_skills=("python",),
            supporting_experience_ids=(101,),
        ),
    )

    assert result.experiences == (relevant_experience,)
    assert result.skills == (python_skill,)


def test_build_tailoring_input_is_safe_with_missing_optional_job_data():
    result = build_tailoring_input(
        make_profile(),
        make_job(description=None),
        make_match(),
    )

    assert result.job.description is None
    assert result.experiences == ()
    assert result.projects == ()
    assert result.skills == ()


def test_build_tailoring_input_rejects_candidate_mismatch():
    with pytest.raises(ValueError, match="candidate"):
        build_tailoring_input(
            make_profile(candidate_id=1),
            make_job(),
            make_match(candidate_id=746),
        )


def test_build_tailoring_input_rejects_job_mismatch():
    with pytest.raises(ValueError, match="job"):
        build_tailoring_input(
            make_profile(),
            make_job(job_id=100),
            make_match(job_id=200),
        )

def test_build_tailoring_input_selects_achievements_for_selected_evidence():
    experience = CandidateExperienceRecord(
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
        description="Built data pipelines.",
        verification_status="source_document",
        visibility="internal",
    )

    achievement = CandidateAchievementRecord(
        id=501,
        experience_id=101,
        project_id=None,
        title="Pipeline Improvement",
        description="Improved pipeline reliability.",
        metric_text="Reduced failures by 50%.",
        verification_status="source_document",
        visibility="internal",
    )

    profile = make_profile(
        experiences=(experience,),
    )

    profile = CanonicalCandidateProfile(
        identity=profile.identity,
        profile=profile.profile,
        contacts=profile.contacts,
        links=profile.links,
        experiences=profile.experiences,
        projects=profile.projects,
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
        achievements=(achievement,),
        preferences=profile.preferences,
        application_facts=profile.application_facts,
        stories=profile.stories,
        facts=profile.facts,
        evidence=profile.evidence,
        tags=profile.tags,
        entity_tags=profile.entity_tags,
        entity_relations=profile.entity_relations,
    )

    result = build_tailoring_input(
        profile,
        make_job(),
        make_match(
            supporting_experience_ids=(101,),
        ),
    )

    assert result.achievements == (achievement,)


def test_build_tailoring_input_excludes_unverified_achievements():
    experience = CandidateExperienceRecord(
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
        description=None,
        verification_status="verified",
        visibility="internal",
    )

    achievement = CandidateAchievementRecord(
        id=501,
        experience_id=101,
        project_id=None,
        title="Unverified Metric",
        description="Unverified result.",
        metric_text="Improved performance by 900%.",
        verification_status="unverified",
        visibility="internal",
    )

    profile = make_profile(
        experiences=(experience,),
    )

    profile = CanonicalCandidateProfile(
        identity=profile.identity,
        profile=profile.profile,
        contacts=profile.contacts,
        links=profile.links,
        experiences=profile.experiences,
        projects=profile.projects,
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
        achievements=(achievement,),
        preferences=profile.preferences,
        application_facts=profile.application_facts,
        stories=profile.stories,
        facts=profile.facts,
        evidence=profile.evidence,
        tags=profile.tags,
        entity_tags=profile.entity_tags,
        entity_relations=profile.entity_relations,
    )

    result = build_tailoring_input(
        profile,
        make_job(),
        make_match(
            supporting_experience_ids=(101,),
        ),
    )

    assert result.achievements == ()


def test_build_tailoring_input_excludes_application_only_records():
    experience = CandidateExperienceRecord(
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
        description=None,
        verification_status="verified",
        visibility="application_only",
    )

    result = build_tailoring_input(
        make_profile(
            experiences=(experience,),
        ),
        make_job(),
        make_match(
            supporting_experience_ids=(101,),
        ),
    )

    assert result.experiences == ()