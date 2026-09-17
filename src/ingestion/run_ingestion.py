from sqlalchemy.orm import Session

from src.database.session import engine
from src.ingestion.lever_adapter import fetch_source_jobs
from src.ingestion.relevance_filter import is_relevant
from src.ingestion.save_raw_job import save_raw_job
from src.ingestion.source_registry import SOURCES

ADAPTERS = {
    "lever": fetch_source_jobs,
}


def main():
    inserted = 0
    skipped = 0
    filtered = 0

    with Session(engine) as session:
        for source in SOURCES:
            if not source["enabled"]:
                continue

            adapter = ADAPTERS.get(source["source_type"])

            if adapter is None:
                print(
                    f"Skipping unsupported source type: "
                    f"{source['source_type']}"
                )
                continue

            company = source["company"]

            print(f"\nIngesting: {company}")

            jobs = adapter(source)

            print(f"Jobs discovered: {len(jobs)}")

            for job in jobs:
                if not is_relevant(job):
                    filtered += 1
                    continue

                if save_raw_job(
                    session=session,
                    job=job,
                    source=source,
                ):
                    inserted += 1
                else:
                    skipped += 1

        session.commit()

    print(
        f"\nFinished ingestion. "
        f"Inserted={inserted}, "
        f"Skipped={skipped}, "
        f"Filtered={filtered}"
    )


if __name__ == "__main__":
    main()