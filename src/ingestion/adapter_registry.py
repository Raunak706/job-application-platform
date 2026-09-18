from src.ingestion.greenhouse_adapter import (
    fetch_source_jobs as fetch_greenhouse_jobs,
    to_raw_record as greenhouse_to_raw_record,
)
from src.ingestion.lever_adapter import (
    fetch_source_jobs as fetch_lever_jobs,
    to_raw_record as lever_to_raw_record,
)


ADAPTERS = {
    "lever": {
        "fetch": fetch_lever_jobs,
        "to_raw_record": lever_to_raw_record,
    },
    "greenhouse": {
        "fetch": fetch_greenhouse_jobs,
        "to_raw_record": greenhouse_to_raw_record,
    },
}