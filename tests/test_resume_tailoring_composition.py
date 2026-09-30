from src.candidate_profile.contracts import (
    CandidateExperienceSkillRecord,
    CandidateProjectSkillRecord,
    SkillRecord,
)
from src.resume_tailoring.composition import (
    build_composition_plan,
    build_evidence_relevance,
)


def make_skill(
    skill_id: int,
    canonical_name: str,
    normalized_name: str,
) -> SkillRecord:
    return SkillRecord(
        skill_id=skill_id,
        canonical_name=canonical_name,
        normalized_name=normalized_name,
        category=None,
    )


def make_experience_skill(
    record_id: int,
    experience_id: int,
    skill: SkillRecord,
) -> CandidateExperienceSkillRecord:
    return CandidateExperienceSkillRecord(
        id=record_id,
        experience_id=experience_id,
        skill=skill,
        usage_description=None,
    )


def make_project_skill(
    record_id: int,
    project_id: int,
    skill: SkillRecord,
) -> CandidateProjectSkillRecord:
    return CandidateProjectSkillRecord(
        id=record_id,
        project_id=project_id,
        skill=skill,
        usage_description=None,
    )


def test_composition_plan_gives_selected_projects_at_least_two_bullets():
    plan = build_composition_plan(
        experience_ids=(),
        project_ids=(201, 202, 203),
        experience_relevance={},
        project_relevance={
            201: 3,
            202: 2,
            203: 1,
        },
    )

    assert tuple(
        allocation.project_id
        for allocation in plan.projects
    ) == (201, 202, 203)

    assert all(
        allocation.target_bullets >= 2
        for allocation in plan.projects
    )


def test_composition_plan_gives_more_relevant_project_more_space():
    plan = build_composition_plan(
        experience_ids=(),
        project_ids=(201, 202, 203),
        experience_relevance={},
        project_relevance={
            201: 4,
            202: 2,
            203: 1,
        },
    )

    allocations = {
        allocation.project_id: allocation.target_bullets
        for allocation in plan.projects
    }

    assert allocations[201] > allocations[202]
    assert allocations[201] > allocations[203]


def test_composition_plan_does_not_force_equal_project_allocations():
    plan = build_composition_plan(
        experience_ids=(),
        project_ids=(201, 202, 203),
        experience_relevance={},
        project_relevance={
            201: 5,
            202: 2,
            203: 1,
        },
    )

    bullet_counts = tuple(
        allocation.target_bullets
        for allocation in plan.projects
    )

    assert len(set(bullet_counts)) > 1


def test_composition_plan_caps_project_detail_at_four_bullets():
    plan = build_composition_plan(
        experience_ids=(),
        project_ids=(201,),
        experience_relevance={},
        project_relevance={
            201: 100,
        },
    )

    assert plan.projects[0].target_bullets == 4


def test_composition_plan_can_use_three_bullets_for_medium_priority_project():
    plan = build_composition_plan(
        experience_ids=(),
        project_ids=(201, 202, 203),
        experience_relevance={},
        project_relevance={
            201: 4,
            202: 3,
            203: 1,
        },
    )

    allocations = {
        allocation.project_id: allocation.target_bullets
        for allocation in plan.projects
    }

    assert allocations[201] == 4
    assert allocations[202] == 3
    assert allocations[203] == 2


def test_composition_plan_uses_two_bullets_when_project_relevance_is_tied():
    plan = build_composition_plan(
        experience_ids=(),
        project_ids=(201, 202, 203),
        experience_relevance={},
        project_relevance={
            201: 1,
            202: 1,
            203: 1,
        },
    )

    assert tuple(
        allocation.target_bullets
        for allocation in plan.projects
    ) == (2, 2, 2)


def test_composition_plan_preserves_selected_project_order():
    plan = build_composition_plan(
        experience_ids=(),
        project_ids=(203, 201, 202),
        experience_relevance={},
        project_relevance={
            201: 2,
            202: 1,
            203: 3,
        },
    )

    assert tuple(
        allocation.project_id
        for allocation in plan.projects
    ) == (203, 201, 202)


def test_composition_plan_allocates_experience_detail_by_relevance():
    plan = build_composition_plan(
        experience_ids=(101, 102),
        project_ids=(),
        experience_relevance={
            101: 4,
            102: 1,
        },
        project_relevance={},
    )

    allocations = {
        allocation.experience_id: allocation.target_bullets
        for allocation in plan.experiences
    }

    assert allocations[101] > allocations[102]


def test_composition_plan_caps_experience_detail_at_four_bullets():
    plan = build_composition_plan(
        experience_ids=(101,),
        project_ids=(),
        experience_relevance={
            101: 100,
        },
        project_relevance={},
    )

    assert plan.experiences[0].target_bullets == 4


def test_composition_plan_preserves_selected_experience_order():
    plan = build_composition_plan(
        experience_ids=(102, 101),
        project_ids=(),
        experience_relevance={
            101: 1,
            102: 3,
        },
        project_relevance={},
    )

    assert tuple(
        allocation.experience_id
        for allocation in plan.experiences
    ) == (102, 101)


def test_composition_plan_handles_no_selected_evidence():
    plan = build_composition_plan(
        experience_ids=(),
        project_ids=(),
        experience_relevance={},
        project_relevance={},
    )

    assert plan.experiences == ()
    assert plan.projects == ()


def test_composition_plan_is_deterministic():
    arguments = {
        "experience_ids": (101, 102),
        "project_ids": (201, 202, 203),
        "experience_relevance": {
            101: 3,
            102: 1,
        },
        "project_relevance": {
            201: 4,
            202: 2,
            203: 1,
        },
    }

    first = build_composition_plan(**arguments)
    second = build_composition_plan(**arguments)

    assert first == second


def test_build_evidence_relevance_counts_matched_experience_skills():
    python = make_skill(401, "Python", "python")
    sql = make_skill(402, "SQL", "sql")
    docker = make_skill(403, "Docker", "docker")

    experience_skills = (
        make_experience_skill(1, 101, python),
        make_experience_skill(2, 101, sql),
        make_experience_skill(3, 102, docker),
    )

    relevance = build_evidence_relevance(
        selected_ids=(101, 102),
        skill_links=experience_skills,
        matched_skills=("python", "sql"),
        entity_id_getter=lambda link: link.experience_id,
    )

    assert relevance == {
        101: 2,
        102: 0,
    }


def test_build_evidence_relevance_counts_matched_project_skills():
    python = make_skill(401, "Python", "python")
    sql = make_skill(402, "SQL", "sql")
    etl = make_skill(403, "ETL", "etl")

    project_skills = (
        make_project_skill(1, 201, python),
        make_project_skill(2, 201, sql),
        make_project_skill(3, 202, etl),
    )

    relevance = build_evidence_relevance(
        selected_ids=(201, 202),
        skill_links=project_skills,
        matched_skills=("python", "sql", "etl"),
        entity_id_getter=lambda link: link.project_id,
    )

    assert relevance == {
        201: 2,
        202: 1,
    }


def test_build_evidence_relevance_ignores_unmatched_skills():
    python = make_skill(401, "Python", "python")
    docker = make_skill(402, "Docker", "docker")

    project_skills = (
        make_project_skill(1, 201, python),
        make_project_skill(2, 201, docker),
    )

    relevance = build_evidence_relevance(
        selected_ids=(201,),
        skill_links=project_skills,
        matched_skills=("python",),
        entity_id_getter=lambda link: link.project_id,
    )

    assert relevance == {
        201: 1,
    }


def test_build_evidence_relevance_does_not_double_count_same_skill():
    python = make_skill(401, "Python", "python")

    project_skills = (
        make_project_skill(1, 201, python),
        make_project_skill(2, 201, python),
    )

    relevance = build_evidence_relevance(
        selected_ids=(201,),
        skill_links=project_skills,
        matched_skills=("python",),
        entity_id_getter=lambda link: link.project_id,
    )

    assert relevance == {
        201: 1,
    }


def test_build_evidence_relevance_ignores_unselected_entities():
    python = make_skill(401, "Python", "python")
    sql = make_skill(402, "SQL", "sql")

    project_skills = (
        make_project_skill(1, 201, python),
        make_project_skill(2, 999, python),
        make_project_skill(3, 999, sql),
    )

    relevance = build_evidence_relevance(
        selected_ids=(201,),
        skill_links=project_skills,
        matched_skills=("python", "sql"),
        entity_id_getter=lambda link: link.project_id,
    )

    assert relevance == {
        201: 1,
    }


def test_build_evidence_relevance_is_case_insensitive():
    python = make_skill(401, "Python", "PYTHON")

    project_skills = (
        make_project_skill(1, 201, python),
    )

    relevance = build_evidence_relevance(
        selected_ids=(201,),
        skill_links=project_skills,
        matched_skills=("Python",),
        entity_id_getter=lambda link: link.project_id,
    )

    assert relevance == {
        201: 1,
    }


def test_build_evidence_relevance_handles_missing_skill_links():
    relevance = build_evidence_relevance(
        selected_ids=(201, 202),
        skill_links=(),
        matched_skills=("python", "sql"),
        entity_id_getter=lambda link: link.project_id,
    )

    assert relevance == {
        201: 0,
        202: 0,
    }

def test_build_composition_plan_from_profile_uses_selected_evidence_and_match():
    from src.candidate_profile.contracts import (
        CandidateExperienceRecord,
        CandidateIdentity,
        CandidateProfileDetails,
        CandidateProjectRecord,
        CanonicalCandidateProfile,
    )
    from src.matching.contracts import CandidateJobMatchResult
    from src.resume_tailoring.composition import (
        build_composition_plan_from_profile,
    )
    from src.resume_tailoring.contracts import (
        TailoringInput,
        TailoringJobContext,
    )

    python = make_skill(401, "Python", "python")
    sql = make_skill(402, "SQL", "sql")
    etl = make_skill(403, "ETL", "etl")

    experience_one = CandidateExperienceRecord(
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
        description="Built data systems.",
        verification_status="verified",
        visibility="resume_safe",
    )

    experience_two = CandidateExperienceRecord(
        id=102,
        company="Example Company",
        title="Software Engineer",
        employment_type=None,
        department=None,
        location=None,
        country=None,
        start_date=None,
        end_date=None,
        is_current=False,
        description="Built backend systems.",
        verification_status="verified",
        visibility="resume_safe",
    )

    project_one = CandidateProjectRecord(
        id=201,
        name="Data Platform",
        role=None,
        organization=None,
        description="Built a data platform.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status="completed",
        verification_status="verified",
        visibility="resume_safe",
    )

    project_two = CandidateProjectRecord(
        id=202,
        name="ETL Project",
        role=None,
        organization=None,
        description="Built an ETL project.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status="completed",
        verification_status="verified",
        visibility="resume_safe",
    )

    profile = CanonicalCandidateProfile(
        identity=CandidateIdentity(
            candidate_id=1,
            display_name="Example Candidate",
            status="active",
        ),
        profile=CandidateProfileDetails(
            profile_id=10,
            professional_headline="Data Engineer",
            professional_summary=None,
            current_location=None,
            current_country=None,
        ),
        contacts=(),
        links=(),
        experiences=(experience_one, experience_two),
        projects=(project_one, project_two),
        project_links=(),
        skills=(),
        experience_skills=(
            make_experience_skill(1, 101, python),
            make_experience_skill(2, 101, sql),
            make_experience_skill(3, 101, etl),
            make_experience_skill(4, 102, python),
        ),
        project_skills=(
            make_project_skill(5, 201, python),
            make_project_skill(6, 201, sql),
            make_project_skill(7, 201, etl),
            make_project_skill(8, 202, python),
        ),
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

    tailoring_input = TailoringInput(
        candidate_id=1,
        job=TailoringJobContext(
            job_id=100,
            title="Data Engineer",
            company="Example Employer",
            description="Build Python SQL ETL pipelines.",
            location=None,
            country=None,
            workplace_type=None,
            employment_type=None,
            department=None,
        ),
        professional_headline="Data Engineer",
        professional_summary=None,
        experiences=(experience_one, experience_two),
        projects=(project_one, project_two),
        skills=(),
    )

    match_result = CandidateJobMatchResult(
        candidate_id=1,
        job_id=100,
        matcher_version="v1",
        overall_score=0.8,
        skill_score=0.8,
        title_relevance_score=0.8,
        evidence_score=0.8,
        compatibility_score=0.8,
        matched_skills=("python", "sql", "etl"),
        missing_skills=(),
        supporting_experience_ids=(101, 102),
        supporting_project_ids=(201, 202),
        compatibility=(),
        reasons=(),
    )

    plan = build_composition_plan_from_profile(
        profile,
        tailoring_input,
        match_result,
    )

    experience_allocations = {
        allocation.experience_id: allocation.target_bullets
        for allocation in plan.experiences
    }

    project_allocations = {
        allocation.project_id: allocation.target_bullets
        for allocation in plan.projects
    }

    assert experience_allocations == {
        101: 4,
        102: 2,
    }

    assert project_allocations == {
        201: 4,
        202: 2,
    }