from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import RawJobPosting
from src.database.session import engine
from src.normalization.normalizer_registry import NORMALIZERS
from src.normalization.validator import validate_normalized_job
from src.normalization.deduplicator import is_duplicate_job
from src.normalization.enricher import enrich_job
from src.normalization.canonicalizer import canonicalize_job
from src.normalization.save_job import save_job


def main():
    normalized = 0
    unsupported = 0
    errors = 0

    with Session(engine) as session:
        raw_jobs = session.scalars(
            select(RawJobPosting).order_by(RawJobPosting.id)
        ).all()

        for raw_job in raw_jobs:
            normalizer = NORMALIZERS.get(raw_job.source)

            if normalizer is None:
                unsupported += 1
                continue

            try:
                record = normalizer(raw_job)

                is_valid, validation_errors = validate_normalized_job(record)

                if not is_valid:
                    errors += 1
                    print(
                        f"Validation failed for raw job {raw_job.id}: "
                        f"{validation_errors}"
                    )
                    continue

                if is_duplicate_job(session, record):
                    print(
                        f"Duplicate job skipped: "
                        f"{record['source']} / {record['source_job_id']}"
                    )
                    continue

                record = enrich_job(record)
                record = canonicalize_job(record)

                if save_job(session, record):
                    normalized += 1
                else:
                    print(
                        f"Job already exists: "
                        f"{record['source']} / {record['source_job_id']}"
                    )

            except Exception as exc:
                errors += 1
                print(
                    f"Error normalizing raw job {raw_job.id}: "
                    f"{type(exc).__name__}: {exc}"
                )

        session.commit()

    print(
        f"\nFinished normalization. "
        f"Inserted={normalized}, "
        f"Unsupported={unsupported}, "
        f"Errors={errors}"
    )


if __name__ == "__main__":
    main()