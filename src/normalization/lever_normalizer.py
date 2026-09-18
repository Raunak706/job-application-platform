from src.database.models import RawJobPosting


def normalize_lever_job(raw_job: RawJobPosting) -> dict:
    payload = raw_job.raw_payload
    categories = payload.get("categories") or {}

    return {
        "raw_job_posting_id": raw_job.id,
        "title": payload.get("text"),
        "company": raw_job.source_company,
        "location": categories.get("location"),
        "country": payload.get("country"),
        "workplace_type": payload.get("workplaceType"),
        "employment_type": categories.get("commitment"),
        "department": categories.get("team"),
        "description": payload.get("descriptionPlain"),
        "source": raw_job.source,
        "source_job_id": raw_job.source_job_id,
        "source_url": raw_job.source_url,
        "apply_url": raw_job.apply_url,
    }