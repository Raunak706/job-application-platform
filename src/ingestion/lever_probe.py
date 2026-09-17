from src.ingestion.relevance_filter import is_relevant
from src.ingestion.source_registry import SOURCES

from src.ingestion.lever_adapter import fetch_source_jobs

def main():
    for source in SOURCES:

        if not source["enabled"]:
            continue

        if source["source_type"] != "lever":
            continue

        company = source["company"]

        print(f"\nChecking: {company}")

        jobs = fetch_source_jobs(source)

        print(f"Jobs discovered: {len(jobs)}")

        relevant_jobs = [
            job
            for job in jobs
            if is_relevant(job)
        ]

        print(
            f"Relevant jobs: {len(relevant_jobs)}"
        )

        for job in relevant_jobs:
            print(
                f"- {job.get('text')} "
                f"| {job.get('categories', {}).get('location')}"
            )


if __name__ == "__main__":
    main()