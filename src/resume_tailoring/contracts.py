from dataclasses import dataclass

from src.candidate_profile.contracts import (
    CandidateAchievementRecord,
    CandidateExperienceRecord,
    CandidateProjectRecord,
    CandidateSkillRecord,
)


@dataclass(frozen=True, slots=True)
class TailoringJobContext:
    job_id: int
    title: str
    company: str
    description: str | None
    location: str | None
    country: str | None
    workplace_type: str | None
    employment_type: str | None
    department: str | None


@dataclass(frozen=True, slots=True)
class TailoringInput:
    candidate_id: int
    job: TailoringJobContext
    professional_headline: str | None
    professional_summary: str | None
    experiences: tuple[CandidateExperienceRecord, ...]
    projects: tuple[CandidateProjectRecord, ...]
    skills: tuple[CandidateSkillRecord, ...]
    achievements: tuple[CandidateAchievementRecord, ...] = ()