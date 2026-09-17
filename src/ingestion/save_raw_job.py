from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.database.models import RawJobPosting
from src.database.session import engine
from src.ingestion.lever_probe import fetch_jobs


def save_raw_job(session: Session, job: dict, company: str) -> bool:
    source_created_at = None

    if job.get("createdAt"):
        source_created_at = datetime.fromtimestamp(
            job["createdAt"] / 1000,
            tz=timezone.utc,
        )

    stmt = (
        insert(RawJobPosting)
        .values(
            source="lever",
            source_company=company,
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


def main():
    company = "h1"
    jobs = fetch_jobs(company=company, limit=5)

    inserted = 0
    skipped = 0

    with Session(engine) as session:
        for job in jobs:
            if save_raw_job(session, job, company):
                inserted += 1
                print(f"Inserted raw job: {job['id']}")
            else:
                skipped += 1
                print(f"Skipped duplicate: {job['id']}")

        session.commit()

    print(
        f"Finished ingestion. "
        f"Inserted={inserted}, Skipped={skipped}"
    )


if __name__ == "__main__":
    main()