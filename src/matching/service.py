from src.candidate_profile.contracts import CanonicalCandidateProfile
from src.database.models import Job
from src.matching.candidate_features import extract_candidate_features
from src.matching.contracts import CandidateJobMatchResult
from src.matching.job_features import extract_job_features
from src.matching.scorer import (
    score_compatibility,
    score_evidence_match,
    score_skill_match,
    score_title_relevance,
)


MATCHER_VERSION = "v1"

SKILL_WEIGHT = 0.45
TITLE_WEIGHT = 0.25
EVIDENCE_WEIGHT = 0.20
COMPATIBILITY_WEIGHT = 0.10


class MatchingService:
    def match(
        self,
        profile: CanonicalCandidateProfile,
        job: Job,
    ) -> CandidateJobMatchResult:
        candidate = extract_candidate_features(profile)
        job_features = extract_job_features(job)

        skill_result = score_skill_match(
            candidate,
            job_features,
        )

        title_result = score_title_relevance(
            candidate,
            job_features,
        )

        evidence_result = score_evidence_match(
            candidate,
            job_features,
        )

        compatibility_result = score_compatibility(
            candidate,
            job_features,
        )

        overall_score = (
            skill_result.score * SKILL_WEIGHT
            + title_result.score * TITLE_WEIGHT
            + evidence_result.score * EVIDENCE_WEIGHT
            + compatibility_result.score * COMPATIBILITY_WEIGHT
        )

        supporting_experience_ids = tuple(
            dict.fromkeys(
                (
                    *title_result.supporting_experience_ids,
                    *evidence_result.supporting_experience_ids,
                )
            )
        )

        reasons = self._build_reasons(
            matched_skills=skill_result.matched_skills,
            missing_skills=skill_result.missing_skills,
            title_score=title_result.score,
            evidence_score=evidence_result.score,
            compatibility=compatibility_result.statuses,
        )

        return CandidateJobMatchResult(
            candidate_id=candidate.candidate_id,
            job_id=job_features.job_id,
            matcher_version=MATCHER_VERSION,
            overall_score=overall_score,
            skill_score=skill_result.score,
            title_relevance_score=title_result.score,
            evidence_score=evidence_result.score,
            compatibility_score=compatibility_result.score,
            matched_skills=skill_result.matched_skills,
            missing_skills=skill_result.missing_skills,
            supporting_experience_ids=supporting_experience_ids,
            supporting_project_ids=(
                evidence_result.supporting_project_ids
            ),
            compatibility=compatibility_result.statuses,
            reasons=reasons,
        )

    @staticmethod
    def _build_reasons(
        *,
        matched_skills: tuple[str, ...],
        missing_skills: tuple[str, ...],
        title_score: float,
        evidence_score: float,
        compatibility: tuple[str, ...],
    ) -> tuple[str, ...]:
        reasons: list[str] = []

        if matched_skills:
            reasons.append(
                "Matched skills: "
                + ", ".join(matched_skills)
                + "."
            )
        else:
            reasons.append(
                "No directly matched canonical skills were found."
            )

        if missing_skills:
            reasons.append(
                "Job skills without direct candidate evidence: "
                + ", ".join(missing_skills)
                + "."
            )

        if title_score > 0.0:
            reasons.append(
                "Candidate experience includes a related role family."
            )
        else:
            reasons.append(
                "No directly related experience title was identified."
            )

        if evidence_score > 0.0:
            reasons.append(
                "Canonical experience or project evidence supports "
                "matched job skills."
            )
        else:
            reasons.append(
                "No direct experience or project evidence was identified "
                "for the matched job skills."
            )

        reasons.append(
            "Compatibility: "
            + ", ".join(compatibility)
            + "."
        )

        return tuple(reasons)