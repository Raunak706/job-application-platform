# Job Data Flow

Job Source
    |
    v
Source Connector
    |
    v
Raw Job Record
    |
    +--> PostgreSQL raw_job_postings
    |
    v
Normalization Service
    |
    +--> validation failure --> mark raw record FAILED
    |
    v
Canonical Job
    |
    v
PostgreSQL jobs
    |
    +--> Application API
    |
    +--> Matching Engine
    |
    +--> Databricks batch processing