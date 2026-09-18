from html import unescape
from re import sub

from src.database.models import RawJobPosting

def _html_to_text(value: str | None) -> str | None:
    if not value:
        return None

    text = unescape(value)
    text = sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = sub(r"\s+", " ", text)

    return text.strip()



def normalize_greenhouse_job(raw_job: RawJobPosting) -> dict:
    payload = raw_job.raw_payload

    metadata = payload.get("metadata") or []
    departments = payload.get("departments") or []
    location = payload.get("location") or {}

    workplace_type = None

    for item in metadata:
        if item.get("name") == "Location Type":
            workplace_type = item.get("value")
            break

    department = None

    if departments:
        department = departments[0].get("name")

    return {
        "raw_job_posting_id": raw_job.id,
        "title": payload.get("title"),
        "company": raw_job.source_company,
        "location": location.get("name"),
        "country": None,
        "workplace_type": workplace_type,
        "employment_type": None,
        "department": department,
        "description": _html_to_text(payload.get("content")),
        "source": raw_job.source,
        "source_job_id": raw_job.source_job_id,
        "source_url": raw_job.source_url,
        "apply_url": raw_job.apply_url,
    }