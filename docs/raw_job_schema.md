# Raw Job Schema

The raw job layer stores the original data collected from a job source before normalization.

## Fields

- `id`
  - Internal UUID.

- `source`
  - Source connector that collected the job.
  - Examples: `greenhouse`, `lever`, `indeed`, `company_site`

- `source_job_id`
  - Identifier supplied by the source when available.

- `source_url`
  - URL from which the job was collected.

- `application_url_raw`
  - Application URL exactly as received.

- `payload`
  - Original source response stored as PostgreSQL JSONB.
  - Must remain unchanged after ingestion.

- `content_hash`
  - Hash generated from stable job content.
  - Used for detecting changes and duplicate ingestion.

- `fetched_at`
  - Timestamp when the platform collected the record.

- `ingestion_version`
  - Version of the source connector that produced the record.

- `normalization_status`
  - `PENDING`
  - `SUCCESS`
  - `FAILED`

- `normalization_error`
  - Error information when normalization fails.

## Processing Rule

Raw records are immutable.

If a source posting changes, the platform stores the updated raw representation rather than silently rewriting historical source data.