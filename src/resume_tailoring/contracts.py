from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.candidate_profile.contracts import (
    CandidateAchievementRecord,
    CandidateExperienceRecord,
    CandidateExperienceSkillRecord,
    CandidateProjectRecord,
    CandidateProjectSkillRecord,
    CandidateSkillRecord,
)

if TYPE_CHECKING:
    from src.resume_tailoring.composition import ResumeCompositionPlan


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
    experience_skills: tuple[CandidateExperienceSkillRecord, ...] = ()
    project_skills: tuple[CandidateProjectSkillRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class ResumeGenerationInput:
    tailoring_input: TailoringInput
    composition_plan: "ResumeCompositionPlan"


@dataclass(frozen=True, slots=True)
class GeneratedExperienceContent:
    experience_id: int
    bullets: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GeneratedProjectContent:
    project_id: int
    bullets: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StructuredResumeContent:
    professional_summary: str | None
    experiences: tuple[GeneratedExperienceContent, ...]
    projects: tuple[GeneratedProjectContent, ...]
    skills: tuple[str, ...]