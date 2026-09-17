from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.database.models import RawJobPosting
from src.database.session import engine


def save_raw_job(session: Session, job: dict, source: str) -> bool:
    source_created_at = None

    if job.get("createdAt"):
        source_created_at = datetime.fromtimestamp(
            job["createdAt"] / 1000,
            tz=timezone.utc,
        )

    stmt = (
        insert(RawJobPosting)
        .values(
            source=source["source_type"],
            source_company=source["company"],
            source_job_id=job["id"],
            source_url=job.get("hostedUrl"),
            apply_url=job.get("applyUrl"),
            raw_payload=job,
            source_created_at=source_created_at,
            fetched_at=datetime.now(timezone.utc),
        )
        .on_conflict_do_nothing(
            constraint="uq_raw_job_source_job_id"
        )
        .returning(RawJobPosting.id)
    )

    inserted_id = session.execute(stmt).scalar_one_or_none()

    return inserted_id is not None

