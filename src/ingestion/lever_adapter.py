from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)

    session = requests.Session()
    session.mount("https://", adapter)

    return session

def fetch_jobs(company: str, limit: int = 10) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{company}"

    params = {
        "mode": "json",
        "limit": limit,
    }

    with create_session() as session:
        response = session.get(
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
    "source_company": source.get("company_name", source["company"]),
    "source_job_id": job["id"],
    "source_url": job.get("hostedUrl"),
    "apply_url": job.get("applyUrl"),
    "source_created_at": source_created_at,
    "title": job.get("text", ""),
    "raw_payload": job,
}