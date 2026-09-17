from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.database.models import RawJobPosting
from src.database.session import engine


def save_raw_job(session: Session, record: dict,) -> bool:
    source_created_at = None

    stmt = (
        insert(RawJobPosting)
        .values(
            source=record["source"],
            source_company=record["source_company"],
            source_job_id=record["source_job_id"],
            source_url=record.get("source_url"),
            apply_url=record.get("apply_url"),
            raw_payload=record["raw_payload"],
            source_created_at=record.get("source_created_at"),
            fetched_at=datetime.now(timezone.utc),
        )
                .on_conflict_do_nothing(
            constraint="uq_raw_job_source_job_id"
        )
        .returning(RawJobPosting.id)
    )

    inserted_id = session.execute(stmt).scalar_one_or_none()

    return inserted_id is not None

