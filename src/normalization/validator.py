REQUIRED_FIELDS = (
    "raw_job_posting_id",
    "title",
    "company",
    "source",
    "source_job_id",
)


def validate_normalized_job(record: dict) -> tuple[bool, list[str]]:
    errors = []

    for field in REQUIRED_FIELDS:
        value = record.get(field)

        if value is None:
            errors.append(f"Missing required field: {field}")
            continue

        if isinstance(value, str) and not value.strip():
            errors.append(f"Empty required field: {field}")

    return len(errors) == 0, errors