from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import Job


def is_duplicate_job(
    session: Session,
    record: dict,
) -> bool:
    stmt = select(Job.id).where(
        Job.source == record["source"],
        Job.source_job_id == record["source_job_id"],
    )

    existing_job_id = session.execute(stmt).scalar_one_or_none()

    return existing_job_id is not None