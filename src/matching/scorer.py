import re

from dataclasses import dataclass

from src.matching.candidate_features import CandidateFeatures
from src.matching.job_features import JobFeatures


KNOWN_SKILLS = (
    "python",
    "r",
    "c++",
    "sql",
    "postgresql",
    "sqlalchemy",
    "alembic",
    "azure",
    "databricks",
    "apache spark",
    "pyspark",
    "delta lake",
    "mlflow",
    "docker",
    "git",
    "github",
    "linux",
    "rest api",
    "api integration",
    "json",
    "jsonb",
    "pytest",
    "data pipelines",
    "etl",
    "data engineering",
    "data analysis",
    "data cleaning",
    "data transformation",
    "data validation",
    "data modeling",
    "database design",
    "data deduplication",
    "matlab",
    "excel",
    "machine learning",
    "statistical modeling",
    "time series analysis",
    "predictive modeling",
    "feature engineering",
    "transformers",
    "computer vision",
    "natural language processing",
    "large language models",
    "pandas",
    "numpy",
    "scikit-learn",
    "pytorch",
    "tensorflow",
    "hugging face transformers",
    "spacy",
    "nltk",
    "opencv",
    "xgboost",
    "openai api",
    "embeddings",
    "semantic search",
    "latex",
)


TITLE_ROLE_GROUPS = (
    (
        "data scientist",
        "machine learning engineer",
        "ml engineer",
        "applied scientist",
    ),
    (
        "data analyst",
        "analytics engineer",
        "business intelligence analyst",
    ),
    (
        "data engineer",
        "analytics engineer",
    ),
    (
        "ai engineer",
        "artificial intelligence engineer",
        "machine learning engineer",
        "ml engineer",
    ),
)


@dataclass(frozen=True, slots=True)
class SkillMatchResult:
    score: float
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvidenceMatchResult:
    score: float
    supporting_experience_ids: tuple[int, ...]
    supporting_project_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class TitleRelevanceResult:
    score: float
    supporting_experience_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CompatibilityResult:
    score: float
    statuses: tuple[str, ...]


def _contains_skill(
    text: str,
    skill: str,
) -> bool:
    pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None


def _job_text(
    job: JobFeatures,
) -> str:
    parts = (
        job.title,
        job.department,
        job.description,
    )

    return " ".join(
        part
        for part in parts
        if part
    ).casefold()


def _evidence_text(
    title: str,
    description: str | None,
) -> str:
    return " ".join(
        part
        for part in (
            title,
            description,
        )
        if part
    ).casefold()


def _detected_job_skills(
    job: JobFeatures,
) -> tuple[str, ...]:
    text = _job_text(job)

    return tuple(
        sorted(
            skill
            for skill in KNOWN_SKILLS
            if _contains_skill(text, skill)
        )
    )


def _normalized_title(
    title: str,
) -> str:
    return " ".join(
        title.strip().casefold().split()
    )


def _title_groups(
    title: str,
) -> set[int]:
    normalized_title = _normalized_title(title)

    return {
        index
        for index, group in enumerate(TITLE_ROLE_GROUPS)
        if any(
            role in normalized_title
            for role in group
        )
    }


def _preference_values(
    candidate: CandidateFeatures,
    category: str,
    preference_key: str,
) -> set[str]:
    for (
        stored_category,
        stored_key,
        value_json,
        _,
    ) in candidate.preferences:
        if (
            stored_category == category
            and stored_key == preference_key
        ):
            values = value_json.get("values")

            if isinstance(values, list):
                return {
                    str(value).strip().casefold()
                    for value in values
                }

    return set()


def score_skill_match(
    candidate: CandidateFeatures,
    job: JobFeatures,
) -> SkillMatchResult:
    detected_job_skills = _detected_job_skills(job)

    if not detected_job_skills:
        return SkillMatchResult(
            score=0.0,
            matched_skills=(),
            missing_skills=(),
        )

    candidate_skills = set(candidate.skills)

    matched_skills = tuple(
        skill
        for skill in detected_job_skills
        if skill in candidate_skills
    )

    missing_skills = tuple(
        skill
        for skill in detected_job_skills
        if skill not in candidate_skills
    )

    score = len(matched_skills) / len(detected_job_skills)

    return SkillMatchResult(
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )


def score_evidence_match(
    candidate: CandidateFeatures,
    job: JobFeatures,
) -> EvidenceMatchResult:
    detected_job_skills = set(
        _detected_job_skills(job)
    )

    candidate_skills = set(candidate.skills)

    relevant_skills = detected_job_skills & candidate_skills

    if not relevant_skills:
        return EvidenceMatchResult(
            score=0.0,
            supporting_experience_ids=(),
            supporting_project_ids=(),
        )

    supported_skills: set[str] = set()
    supporting_experience_ids: list[int] = []
    supporting_project_ids: list[int] = []

    for experience_id, title, description in candidate.experiences:
        text = _evidence_text(
            title,
            description,
        )

        evidence_skills = {
            skill
            for skill in relevant_skills
            if _contains_skill(text, skill)
        }

        if evidence_skills:
            supporting_experience_ids.append(
                experience_id
            )
            supported_skills.update(
                evidence_skills
            )

    for project_id, name, description in candidate.projects:
        text = _evidence_text(
            name,
            description,
        )

        evidence_skills = {
            skill
            for skill in relevant_skills
            if _contains_skill(text, skill)
        }

        if evidence_skills:
            supporting_project_ids.append(
                project_id
            )
            supported_skills.update(
                evidence_skills
            )

    score = len(supported_skills) / len(relevant_skills)

    return EvidenceMatchResult(
        score=score,
        supporting_experience_ids=tuple(
            supporting_experience_ids
        ),
        supporting_project_ids=tuple(
            supporting_project_ids
        ),
    )


def score_title_relevance(
    candidate: CandidateFeatures,
    job: JobFeatures,
) -> TitleRelevanceResult:
    job_groups = _title_groups(job.title)

    if not job_groups:
        return TitleRelevanceResult(
            score=0.0,
            supporting_experience_ids=(),
        )

    supporting_experience_ids = tuple(
        experience_id
        for experience_id, title, _ in candidate.experiences
        if _title_groups(title) & job_groups
    )

    if not supporting_experience_ids:
        return TitleRelevanceResult(
            score=0.0,
            supporting_experience_ids=(),
        )

    return TitleRelevanceResult(
        score=1.0,
        supporting_experience_ids=supporting_experience_ids,
    )


def score_compatibility(
    candidate: CandidateFeatures,
    job: JobFeatures,
) -> CompatibilityResult:
    statuses: list[str] = []
    known_results: list[bool] = []

    if candidate.current_country and job.country:
        location_compatible = (
            candidate.current_country == job.country
        )

        statuses.append(
            "location:compatible"
            if location_compatible
            else "location:mismatch"
        )
        known_results.append(location_compatible)
    else:
        statuses.append("location:unknown")

    workplace_preferences = _preference_values(
        candidate,
        "workplace",
        "workplace_types",
    )

    if job.workplace_type and workplace_preferences:
        workplace_compatible = (
            job.workplace_type
            in workplace_preferences
        )

        statuses.append(
            "workplace:compatible"
            if workplace_compatible
            else "workplace:mismatch"
        )
        known_results.append(workplace_compatible)
    else:
        statuses.append("workplace:unknown")

    employment_preferences = _preference_values(
        candidate,
        "employment",
        "employment_types",
    )

    if job.employment_type and employment_preferences:
        employment_compatible = (
            job.employment_type
            in employment_preferences
        )

        statuses.append(
            "employment_type:compatible"
            if employment_compatible
            else "employment_type:mismatch"
        )
        known_results.append(employment_compatible)
    else:
        statuses.append(
            "employment_type:unknown"
        )

    score = (
        sum(known_results) / len(known_results)
        if known_results
        else 0.0
    )

    return CompatibilityResult(
        score=score,
        statuses=tuple(statuses),
    )