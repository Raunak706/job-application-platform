from sqlalchemy.orm import Session

from src.database.session import engine
from src.ingestion.lever_adapter import fetch_source_jobs, to_raw_record
from src.ingestion.relevance_filter import is_relevant
from src.ingestion.save_raw_job import save_raw_job
from src.ingestion.source_registry import SOURCES
from src.ingestion.greenhouse_adapter import (
    fetch_source_jobs as fetch_greenhouse_jobs,
    to_raw_record as greenhouse_to_raw_record,
)
ADAPTERS = {
    "lever": {
        "fetch": fetch_source_jobs,
        "to_raw_record": to_raw_record,
    },
    "greenhouse": {
        "fetch": fetch_greenhouse_jobs,
        "to_raw_record": greenhouse_to_raw_record,
    },
}

def main():
    inserted = 0
    skipped = 0
    filtered = 0
    source_errors = 0
    job_errors = 0

    with Session(engine) as session:
        for source in SOURCES:
            if not source["enabled"]:
                continue

            try:
                adapter = ADAPTERS.get(source["source_type"])

                if adapter is None:
                    print(
                        f"Skipping unsupported source type: "
                        f"{source['source_type']}"
                    )
                    continue

                company = source["company"]
                print(f"\nIngesting: {company}")

                jobs = adapter["fetch"](source)
                print(f"Jobs discovered: {len(jobs)}")

                for job in jobs:
                    try:
                        record = adapter["to_raw_record"](job, source)

                        if not is_relevant(record["title"]):
                            filtered += 1
                            continue

                        if save_raw_job(
                            session=session,
                            record=record,
                        ):
                            inserted += 1
                        else:
                            skipped += 1

                    except Exception as exc:
                        job_errors += 1
                        print(
                            f"Error processing job from {company}: "
                            f"{type(exc).__name__}: {exc}"
                        )
                        continue

            except Exception as exc:
                source_errors += 1
                company = source.get("company", "unknown")
                print(
                    f"Error ingesting {company}: "
                    f"{type(exc).__name__}: {exc}"
                )
                continue

        session.commit()

    print(
        f"\nFinished ingestion. "
        f"Inserted={inserted}, "
        f"Skipped={skipped}, "
        f"Filtered={filtered}, "
        f"Source errors={source_errors}, "
        f"Job errors={job_errors}"
    )


if __name__ == "__main__":
    main()