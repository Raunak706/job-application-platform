from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.database.models import Job


def save_job(
    session: Session,
    record: dict,
) -> bool:
    stmt = (
        insert(Job)
        .values(
            raw_job_posting_id=record["raw_job_posting_id"],
            title=record["title"],
            company=record["company"],
            location=record.get("location"),
            country=record.get("country"),
            workplace_type=record.get("workplace_type"),
            employment_type=record.get("employment_type"),
            department=record.get("department"),
            description=record.get("description"),
            source=record["source"],
            source_job_id=record["source_job_id"],
            source_url=record.get("source_url"),
            apply_url=record.get("apply_url"),
        )
        .on_conflict_do_nothing(
            constraint="uq_jobs_source_job_id"
        )
        .returning(Job.id)
    )

    inserted_id = session.execute(stmt).scalar_one_or_none()

    return inserted_id is not None