from datetime import datetime, timezone
from src.ingestion.http_client import create_retry_session


def fetch_jobs(
    company: str,
    page_size: int = 100,
) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{company}"

    jobs = []
    skip = 0

    with create_retry_session() as session:
        while True:
            response = session.get(
                url,
                params={
                    "mode": "json",
                    "skip": skip,
                    "limit": page_size,
                },
                timeout=30,
            )

            response.raise_for_status()

            batch = response.json()
            jobs.extend(batch)

            if len(batch) < page_size:
                break

            skip += page_size

    return jobs


def fetch_source_jobs(
    source: dict,
) -> list[dict]:
    if source["source_type"] != "lever":
        raise ValueError(
            "Lever adapter received a non-Lever source."
        )

    return fetch_jobs(
        company=source["company"],
    )


def to_raw_record(
    job: dict,
    source: dict,
) -> dict:
    source_created_at = None

    if job.get("createdAt"):
        source_created_at = datetime.fromtimestamp(
            job["createdAt"] / 1000,
            tz=timezone.utc,
        )

    return {
        "source": source["source_type"],
        "source_company": source.get(
            "company_name",
            source["company"],
        ),
        "source_job_id": job["id"],
        "source_url": job.get("hostedUrl"),
        "apply_url": job.get("applyUrl"),
        "source_created_at": source_created_at,
        "title": job.get("text", ""),
        "raw_payload": job,
    }