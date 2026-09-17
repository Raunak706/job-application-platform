import requests
from datetime import datetime, timezone


def fetch_jobs(company: str, limit: int = 10) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{company}"

    params = {
        "mode": "json",
        "limit": limit,
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def fetch_source_jobs(
    source: dict,
    limit: int = 10,
) -> list[dict]:
    if source["source_type"] != "lever":
        raise ValueError(
            "Lever adapter received a non-Lever source."
        )

    return fetch_jobs(
        company=source["company"],
        limit=limit,
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
        "source_company": source["company"],
        "source_job_id": job["id"],
        "source_url": job.get("hostedUrl"),
        "apply_url": job.get("applyUrl"),
        "source_created_at": source_created_at,
        "title": job.get("text", ""),
        "raw_payload": job,
    }