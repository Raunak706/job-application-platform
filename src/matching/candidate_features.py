from dataclasses import dataclass

from src.candidate_profile.contracts import CanonicalCandidateProfile


@dataclass(frozen=True, slots=True)
class CandidateFeatures:
    candidate_id: int
    skills: tuple[str, ...]
    experiences: tuple[tuple[int, str, str | None], ...]
    projects: tuple[tuple[int, str, str | None], ...]
    current_location: str | None = None
    current_country: str | None = None
    preferences: tuple[
        tuple[str, str, dict[str, object], str | None],
        ...,
    ] = ()


def _normalize_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    normalized = " ".join(
        value.strip().casefold().split()
    )

    if not normalized:
        return None

    return normalized


def extract_candidate_features(
    profile: CanonicalCandidateProfile,
) -> CandidateFeatures:
    skills = tuple(
        sorted(
            {
                skill.skill.normalized_name
                for skill in profile.skills
            }
        )
    )

    experiences = tuple(
        (
            experience.id,
            experience.title,
            experience.description,
        )
        for experience in profile.experiences
    )

    projects = tuple(
        (
            project.id,
            project.name,
            project.description,
        )
        for project in profile.projects
    )

    preferences = tuple(
        (
            preference.category,
            preference.preference_key,
            preference.value_json,
            preference.priority,
        )
        for preference in profile.preferences
        if preference.is_active
    )

    return CandidateFeatures(
        candidate_id=profile.identity.candidate_id,
        skills=skills,
        experiences=experiences,
        projects=projects,
        current_location=_normalize_text(
            profile.profile.current_location
        ),
        current_country=_normalize_text(
            profile.profile.current_country
        ),
        preferences=preferences,
    )