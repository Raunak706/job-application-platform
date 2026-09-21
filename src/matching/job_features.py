from dataclasses import dataclass

from src.database.models import Job


@dataclass(frozen=True, slots=True)
class JobFeatures:
    job_id: int
    title: str
    company: str
    location: str | None
    country: str | None
    workplace_type: str | None
    employment_type: str | None
    department: str | None
    description: str | None


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()

    if not normalized:
        return None

    return normalized


def extract_job_features(
    job: Job,
) -> JobFeatures:
    return JobFeatures(
        job_id=job.id,
        title=_normalize_text(job.title) or "",
        company=_normalize_text(job.company) or "",
        location=_normalize_text(job.location),
        country=_normalize_text(job.country),
        workplace_type=_normalize_text(job.workplace_type),
        employment_type=_normalize_text(job.employment_type),
        department=_normalize_text(job.department),
        description=_normalize_text(job.description),
    )