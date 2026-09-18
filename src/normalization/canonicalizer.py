from src.normalization.mappings import (
    EMPLOYMENT_TYPE_MAPPING,
    WORKPLACE_TYPE_MAPPING,
)


def canonicalize_job(record: dict) -> dict:
    canonical = record.copy()

    workplace_type = canonical.get("workplace_type")
    employment_type = canonical.get("employment_type")

    if isinstance(workplace_type, str):
        key = workplace_type.strip().lower()
        canonical["workplace_type"] = WORKPLACE_TYPE_MAPPING.get(
            key,
            key,
        )

    if isinstance(employment_type, str):
        key = employment_type.strip().lower()
        canonical["employment_type"] = EMPLOYMENT_TYPE_MAPPING.get(
            key,
            key,
        )

    return canonical