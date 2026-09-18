from datetime import datetime
from src.ingestion.http_client import create_retry_session


def fetch_jobs(company: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    with create_retry_session() as session:
        response = session.get(
            url,
            params={"content": "true"},
            timeout=30,
        )

    response.raise_for_status()

    data = response.json()

    return data.get("jobs", [])


def fetch_source_jobs(
    source: dict,
) -> list[dict]:
    if source["source_type"] != "greenhouse":
        raise ValueError(
            "Greenhouse adapter received a non-Greenhouse source."
        )

    jobs = fetch_jobs(
        company=source["company"],
    )

    return jobs


def to_raw_record(
    job: dict,
    source: dict,
) -> dict:
    source_created_at = None

    if job.get("first_published"):
        source_created_at = datetime.fromisoformat(
            job["first_published"]
        )

    return {
        "source": source["source_type"],
        "source_company": source.get("company_name", source["company"]),
        "source_job_id": str(job["id"]),
        "source_url": job.get("absolute_url"),
        "apply_url": job.get("absolute_url"),
        "source_created_at": source_created_at,
        "title": job.get("title", ""),
        "raw_payload": job,
    }
