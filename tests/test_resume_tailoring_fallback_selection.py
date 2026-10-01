from src.candidate_profile.contracts import (
    CandidateExperienceRecord,
    CandidateExperienceSkillRecord,
    CandidateIdentity,
    CandidateProfileDetails,
    CandidateProjectRecord,
    CandidateProjectSkillRecord,
    CanonicalCandidateProfile,
    SkillRecord,
)
from src.matching.contracts import CandidateJobMatchResult
from src.resume_tailoring.contracts import (
    TailoringInput,
    TailoringJobContext,
)
from src.resume_tailoring.fallback_selection import (
    add_next_fallback_evidence,
)


def make_job_context(
    *,
    description="Build Python and SQL data pipelines.",
):
    return TailoringJobContext(
        job_id=100,
        title="Data Engineer",
        company="Example Employer",
        description=description,
        location="New York",
        country="US",
        workplace_type="hybrid",
        employment_type="full_time",
        department="Engineering",
    )


def make_match(
    *,
    matched_skills=("python", "sql"),
):
    return CandidateJobMatchResult(
        candidate_id=1,
        job_id=100,
        matcher_version="v1",
        overall_score=0.75,
        skill_score=0.75,
        title_relevance_score=0.75,
        evidence_score=0.75,
        compatibility_score=0.75,
        matched_skills=matched_skills,
        missing_skills=(),
        supporting_experience_ids=(),
        supporting_project_ids=(),
        compatibility=(),
        reasons=(),
    )


def make_project(
    project_id,
    name,
    *,
    verification_status="verified",
    visibility="resume_safe",
):
    return CandidateProjectRecord(
        id=project_id,
        name=name,
        role=None,
        organization=None,
        description=f"{name} description.",
        problem=None,
        solution=None,
        architecture=None,
        outcome=None,
        start_date=None,
        end_date=None,
        status="completed",
        verification_status=verification_status,
        visibility=visibility,
    )


def make_experience(
    experience_id,
    title,
    *,
    verification_status="verified",
    visibility="resume_safe",
):
    return CandidateExperienceRecord(
        id=experience_id,
        company="Example Company",
        title=title,
        employment_type="full_time",
        department=None,
        location="New York",
        country="US",
        start_date=None,
        end_date=None,
        is_current=False,
        description=f"{title} description.",
        verification_status=verification_status,
        visibility=visibility,
    )


def make_project_skill(
    record_id,
    project_id,
    skill_id,
    canonical_name,
    normalized_name,
):
    return CandidateProjectSkillRecord(
        id=record_id,
        project_id=project_id,
        skill=SkillRecord(
            skill_id=skill_id,
            canonical_name=canonical_name,
            normalized_name=normalized_name,
            category=None,
        ),
        usage_description=None,
    )


def make_experience_skill(
    record_id,
    experience_id,
    skill_id,
    canonical_name,
    normalized_name,
):
    return CandidateExperienceSkillRecord(
        id=record_id,
        experience_id=experience_id,
        skill=SkillRecord(
            skill_id=skill_id,
            canonical_name=canonical_name,
            normalized_name=normalized_name,
            category=None,
        ),
        usage_description=None,
    )


def make_profile(
    *,
    experiences=(),
    projects=(),
    experience_skills=(),
    project_skills=(),
):
    return CanonicalCandidateProfile(
        identity=CandidateIdentity(
            candidate_id=1,
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
        skills=(),
        experience_skills=experience_skills,
        project_skills=project_skills,
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


def make_tailoring_input(
    *,
    experiences=(),
    projects=(),
    experience_skills=(),
    project_skills=(),
    job_description="Build Python and SQL data pipelines.",
):
    return TailoringInput(
        candidate_id=1,
        job=make_job_context(
            description=job_description,
        ),
        professional_headline="Data Engineer",
        professional_summary="Builds reliable data systems.",
        experiences=experiences,
        projects=projects,
        skills=(),
        achievements=(),
        experience_skills=experience_skills,
        project_skills=project_skills,
    )


def test_add_next_fallback_evidence_adds_highest_relevance_project():
    project_one = make_project(201, "Python Project")
    project_two = make_project(202, "Python SQL Project")

    project_skills = (
        make_project_skill(
            1,
            201,
            401,
            "Python",
            "python",
        ),
        make_project_skill(
            2,
            202,
            401,
            "Python",
            "python",
        ),
        make_project_skill(
            3,
            202,
            402,
            "SQL",
            "sql",
        ),
    )

    profile = make_profile(
        projects=(
            project_one,
            project_two,
        ),
        project_skills=project_skills,
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(),
        match_result=make_match(),
    )

    assert result.projects == (project_two,)
    assert result.experiences == ()
    assert result.project_skills == (
        project_skills[1],
        project_skills[2],
    )


def test_add_next_fallback_evidence_adds_only_one_record_per_step():
    project_one = make_project(201, "Project One")
    project_two = make_project(202, "Project Two")

    profile = make_profile(
        projects=(
            project_one,
            project_two,
        ),
        project_skills=(
            make_project_skill(
                1,
                201,
                401,
                "Python",
                "python",
            ),
            make_project_skill(
                2,
                202,
                401,
                "Python",
                "python",
            ),
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(),
        match_result=make_match(
            matched_skills=("python",),
        ),
    )

    assert result.projects == (project_one,)


def test_add_next_fallback_evidence_never_duplicates_selected_project():
    project_one = make_project(201, "Already Selected")
    project_two = make_project(202, "Fallback Project")

    selected_skill = make_project_skill(
        1,
        201,
        401,
        "Python",
        "python",
    )

    fallback_skill = make_project_skill(
        2,
        202,
        402,
        "SQL",
        "sql",
    )

    profile = make_profile(
        projects=(
            project_one,
            project_two,
        ),
        project_skills=(
            selected_skill,
            fallback_skill,
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(
            projects=(project_one,),
            project_skills=(selected_skill,),
        ),
        match_result=make_match(),
    )

    assert result.projects == (
        project_one,
        project_two,
    )
    assert result.project_skills == (
        selected_skill,
        fallback_skill,
    )


def test_add_next_fallback_evidence_excludes_unapproved_projects():
    unverified_project = make_project(
        201,
        "Unverified Project",
        verification_status="unverified",
    )

    application_only_project = make_project(
        202,
        "Application Only Project",
        visibility="application_only",
    )

    approved_project = make_project(
        203,
        "Approved Project",
    )

    profile = make_profile(
        projects=(
            unverified_project,
            application_only_project,
            approved_project,
        ),
        project_skills=(
            make_project_skill(
                1,
                201,
                401,
                "Python",
                "python",
            ),
            make_project_skill(
                2,
                202,
                401,
                "Python",
                "python",
            ),
            make_project_skill(
                3,
                203,
                401,
                "Python",
                "python",
            ),
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(),
        match_result=make_match(
            matched_skills=("python",),
        ),
    )

    assert result.projects == (approved_project,)


def test_add_next_fallback_evidence_uses_profile_order_for_project_ties():
    project_two = make_project(202, "Second ID")
    project_one = make_project(201, "First ID")

    profile = make_profile(
        projects=(
            project_two,
            project_one,
        ),
        project_skills=(
            make_project_skill(
                1,
                202,
                401,
                "Python",
                "python",
            ),
            make_project_skill(
                2,
                201,
                401,
                "Python",
                "python",
            ),
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(),
        match_result=make_match(
            matched_skills=("python",),
        ),
    )

    assert result.projects == (project_two,)


def test_add_next_fallback_evidence_uses_experience_when_no_project_available():
    experience_one = make_experience(
        101,
        "Data Engineer",
    )

    experience_two = make_experience(
        102,
        "Software Engineer",
    )

    experience_skills = (
        make_experience_skill(
            1,
            101,
            401,
            "Python",
            "python",
        ),
        make_experience_skill(
            2,
            101,
            402,
            "SQL",
            "sql",
        ),
        make_experience_skill(
            3,
            102,
            401,
            "Python",
            "python",
        ),
    )

    profile = make_profile(
        experiences=(
            experience_one,
            experience_two,
        ),
        experience_skills=experience_skills,
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(),
        match_result=make_match(),
    )

    assert result.projects == ()
    assert result.experiences == (experience_one,)
    assert result.experience_skills == (
        experience_skills[0],
        experience_skills[1],
    )


def test_add_next_fallback_evidence_excludes_unapproved_experiences():
    unverified_experience = make_experience(
        101,
        "Unverified Role",
        verification_status="unverified",
    )

    application_only_experience = make_experience(
        102,
        "Application Only Role",
        visibility="application_only",
    )

    approved_experience = make_experience(
        103,
        "Approved Role",
    )

    profile = make_profile(
        experiences=(
            unverified_experience,
            application_only_experience,
            approved_experience,
        ),
        experience_skills=(
            make_experience_skill(
                1,
                101,
                401,
                "Python",
                "python",
            ),
            make_experience_skill(
                2,
                102,
                401,
                "Python",
                "python",
            ),
            make_experience_skill(
                3,
                103,
                401,
                "Python",
                "python",
            ),
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(),
        match_result=make_match(
            matched_skills=("python",),
        ),
    )

    assert result.experiences == (approved_experience,)


def test_add_next_fallback_evidence_returns_input_when_nothing_is_available():
    project = make_project(
        201,
        "Already Selected",
    )

    project_skill = make_project_skill(
        1,
        201,
        401,
        "Python",
        "python",
    )

    tailoring_input = make_tailoring_input(
        projects=(project,),
        project_skills=(project_skill,),
    )

    profile = make_profile(
        projects=(project,),
        project_skills=(project_skill,),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=make_match(
            matched_skills=("python",),
        ),
    )

    assert result is tailoring_input


def test_fallback_recognizes_whisper_as_speech_recognition():
    generic_project = make_project(
        201,
        "Generic Project",
    )

    speech_project = make_project(
        202,
        "Speech Project",
    )

    profile = make_profile(
        projects=(
            generic_project,
            speech_project,
        ),
        project_skills=(
            make_project_skill(
                1,
                201,
                401,
                "Python",
                "python",
            ),
            make_project_skill(
                2,
                202,
                402,
                "Whisper ASR",
                "whisper asr",
            ),
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(
            job_description=(
                "Build automatic speech recognition "
                "and audio processing systems."
            ),
        ),
        match_result=make_match(
            matched_skills=(),
        ),
    )

    assert result.projects == (speech_project,)


def test_fallback_recognizes_marianmt_as_machine_translation():
    generic_project = make_project(
        201,
        "Generic Project",
    )

    translation_project = make_project(
        202,
        "Translation Project",
    )

    profile = make_profile(
        projects=(
            generic_project,
            translation_project,
        ),
        project_skills=(
            make_project_skill(
                1,
                201,
                401,
                "Python",
                "python",
            ),
            make_project_skill(
                2,
                202,
                402,
                "MarianMT",
                "marianmt",
            ),
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(
            job_description=(
                "Develop machine translation "
                "and multilingual NLP systems."
            ),
        ),
        match_result=make_match(
            matched_skills=(),
        ),
    )

    assert result.projects == (translation_project,)


def test_fallback_recognizes_eeg_fft_as_signal_processing():
    generic_project = make_project(
        201,
        "Generic Project",
    )

    signal_project = make_project(
        202,
        "EEG Project",
    )

    profile = make_profile(
        projects=(
            generic_project,
            signal_project,
        ),
        project_skills=(
            make_project_skill(
                1,
                201,
                401,
                "Python",
                "python",
            ),
            make_project_skill(
                2,
                202,
                402,
                "EEG",
                "eeg",
            ),
            make_project_skill(
                3,
                202,
                403,
                "Fast Fourier Transform",
                "fft",
            ),
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(
            job_description=(
                "Work on signal processing "
                "and frequency-domain analysis."
            ),
        ),
        match_result=make_match(
            matched_skills=(),
        ),
    )

    assert result.projects == (signal_project,)


def test_fallback_recognizes_postgres_mongodb_as_heterogeneous_data_integration():
    generic_project = make_project(
        201,
        "Generic Project",
    )

    federated_project = make_project(
        202,
        "Federated Database Project",
    )

    profile = make_profile(
        projects=(
            generic_project,
            federated_project,
        ),
        project_skills=(
            make_project_skill(
                1,
                201,
                401,
                "Python",
                "python",
            ),
            make_project_skill(
                2,
                202,
                402,
                "PostgreSQL",
                "postgresql",
            ),
            make_project_skill(
                3,
                202,
                403,
                "MongoDB",
                "mongodb",
            ),
        ),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(
            job_description=(
                "Design heterogeneous data integration "
                "across relational and document databases."
            ),
        ),
        match_result=make_match(
            matched_skills=(),
        ),
    )

    assert result.projects == (federated_project,)

def test_fallback_prioritizes_second_professional_experience_before_project():
    selected_experience = make_experience(
        101,
        "Data Engineer",
    )

    fallback_experience = make_experience(
        102,
        "Machine Learning Engineer",
    )

    fallback_project = make_project(
        201,
        "Data Platform Project",
    )

    selected_experience_skill = make_experience_skill(
        1,
        101,
        401,
        "Python",
        "python",
    )

    fallback_experience_skill = make_experience_skill(
        2,
        102,
        402,
        "SQL",
        "sql",
    )

    fallback_project_skill = make_project_skill(
        3,
        201,
        402,
        "SQL",
        "sql",
    )

    profile = make_profile(
        experiences=(
            selected_experience,
            fallback_experience,
        ),
        projects=(fallback_project,),
        experience_skills=(
            selected_experience_skill,
            fallback_experience_skill,
        ),
        project_skills=(fallback_project_skill,),
    )

    result = add_next_fallback_evidence(
        profile=profile,
        tailoring_input=make_tailoring_input(
            experiences=(selected_experience,),
            experience_skills=(selected_experience_skill,),
        ),
        match_result=make_match(),
    )

    assert result.experiences == (
        selected_experience,
        fallback_experience,
    )
    assert result.experience_skills == (
        selected_experience_skill,
        fallback_experience_skill,
    )
    assert result.projects == ()