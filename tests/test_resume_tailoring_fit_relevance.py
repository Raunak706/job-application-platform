from types import SimpleNamespace

from src.candidate_profile.contracts import (
    CandidateExperienceSkillRecord,
    CandidateProjectSkillRecord,
    SkillRecord,
)
from src.resume_tailoring.fit_relevance import (
    build_fit_relevance,
)


def _skill(
    *,
    skill_id,
    name,
):
    return SkillRecord(
        skill_id=skill_id,
        canonical_name=name,
        normalized_name=name.casefold(),
        category=None,
    )


def test_build_fit_relevance_uses_selected_evidence_and_matched_skills():
    python = _skill(
        skill_id=401,
        name="Python",
    )
    sql = _skill(
        skill_id=402,
        name="SQL",
    )
    etl = _skill(
        skill_id=403,
        name="ETL",
    )
    docker = _skill(
        skill_id=404,
        name="Docker",
    )

    profile = SimpleNamespace(
        experience_skills=(
            CandidateExperienceSkillRecord(
                id=1,
                experience_id=101,
                skill=python,
                usage_description=None,
            ),
            CandidateExperienceSkillRecord(
                id=2,
                experience_id=101,
                skill=sql,
                usage_description=None,
            ),
            CandidateExperienceSkillRecord(
                id=3,
                experience_id=102,
                skill=python,
                usage_description=None,
            ),
            CandidateExperienceSkillRecord(
                id=4,
                experience_id=999,
                skill=etl,
                usage_description=None,
            ),
        ),
        project_skills=(
            CandidateProjectSkillRecord(
                id=5,
                project_id=201,
                skill=python,
                usage_description=None,
            ),
            CandidateProjectSkillRecord(
                id=6,
                project_id=201,
                skill=sql,
                usage_description=None,
            ),
            CandidateProjectSkillRecord(
                id=7,
                project_id=201,
                skill=etl,
                usage_description=None,
            ),
            CandidateProjectSkillRecord(
                id=8,
                project_id=202,
                skill=python,
                usage_description=None,
            ),
            CandidateProjectSkillRecord(
                id=9,
                project_id=203,
                skill=docker,
                usage_description=None,
            ),
        ),
    )

    tailoring_input = SimpleNamespace(
        candidate_id=1,
        job=SimpleNamespace(
            job_id=100,
        ),
        experiences=(
            SimpleNamespace(id=101),
            SimpleNamespace(id=102),
        ),
        projects=(
            SimpleNamespace(id=201),
            SimpleNamespace(id=202),
            SimpleNamespace(id=203),
        ),
    )

    match_result = SimpleNamespace(
        candidate_id=1,
        job_id=100,
        matched_skills=(
            "python",
            "sql",
            "etl",
        ),
    )

    relevance = build_fit_relevance(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
    )

    assert relevance.experiences == {
        101: 2,
        102: 1,
    }

    assert relevance.projects == {
        201: 3,
        202: 1,
        203: 0,
    }


def test_build_fit_relevance_handles_no_selected_evidence():
    profile = SimpleNamespace(
        experience_skills=(),
        project_skills=(),
    )

    tailoring_input = SimpleNamespace(
        candidate_id=1,
        job=SimpleNamespace(
            job_id=100,
        ),
        experiences=(),
        projects=(),
    )

    match_result = SimpleNamespace(
        candidate_id=1,
        job_id=100,
        matched_skills=("python",),
    )

    relevance = build_fit_relevance(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
    )

    assert relevance.experiences == {}
    assert relevance.projects == {}


def test_build_fit_relevance_rejects_candidate_mismatch():
    profile = SimpleNamespace(
        experience_skills=(),
        project_skills=(),
    )

    tailoring_input = SimpleNamespace(
        candidate_id=1,
        job=SimpleNamespace(
            job_id=100,
        ),
        experiences=(),
        projects=(),
    )

    match_result = SimpleNamespace(
        candidate_id=2,
        job_id=100,
        matched_skills=(),
    )

    try:
        build_fit_relevance(
            profile=profile,
            tailoring_input=tailoring_input,
            match_result=match_result,
        )
    except ValueError as error:
        assert str(error) == (
            "Match result candidate does not match "
            "tailoring input."
        )
    else:
        raise AssertionError(
            "Expected candidate mismatch to fail."
        )


def test_build_fit_relevance_rejects_job_mismatch():
    profile = SimpleNamespace(
        experience_skills=(),
        project_skills=(),
    )

    tailoring_input = SimpleNamespace(
        candidate_id=1,
        job=SimpleNamespace(
            job_id=100,
        ),
        experiences=(),
        projects=(),
    )

    match_result = SimpleNamespace(
        candidate_id=1,
        job_id=200,
        matched_skills=(),
    )

    try:
        build_fit_relevance(
            profile=profile,
            tailoring_input=tailoring_input,
            match_result=match_result,
        )
    except ValueError as error:
        assert str(error) == (
            "Match result job does not match "
            "tailoring input."
        )
    else:
        raise AssertionError(
            "Expected job mismatch to fail."
        )

def test_build_fit_relevance_augments_project_score_with_semantic_relevance():
    whisper = _skill(
        skill_id=401,
        name="Whisper ASR",
    )
    marianmt = _skill(
        skill_id=402,
        name="MarianMT",
    )
    docker = _skill(
        skill_id=403,
        name="Docker",
    )

    profile = SimpleNamespace(
        experience_skills=(),
        project_skills=(
            CandidateProjectSkillRecord(
                id=1,
                project_id=201,
                skill=whisper,
                usage_description=None,
            ),
            CandidateProjectSkillRecord(
                id=2,
                project_id=201,
                skill=marianmt,
                usage_description=None,
            ),
            CandidateProjectSkillRecord(
                id=3,
                project_id=202,
                skill=docker,
                usage_description=None,
            ),
        ),
    )

    tailoring_input = SimpleNamespace(
        candidate_id=1,
        job=SimpleNamespace(
            job_id=100,
            description=(
                "Build systems for speech translation "
                "and multilingual language processing."
            ),
        ),
        experiences=(),
        projects=(
            SimpleNamespace(id=201),
            SimpleNamespace(id=202),
        ),
    )

    match_result = SimpleNamespace(
        candidate_id=1,
        job_id=100,
        matched_skills=(),
    )

    relevance = build_fit_relevance(
        profile=profile,
        tailoring_input=tailoring_input,
        match_result=match_result,
    )

    assert relevance.projects[201] > relevance.projects[202]
    assert relevance.projects[201] > 0
    assert relevance.projects[202] == 0