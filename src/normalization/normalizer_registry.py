from src.normalization.greenhouse_normalizer import normalize_greenhouse_job
from src.normalization.lever_normalizer import normalize_lever_job


NORMALIZERS = {
    "lever": normalize_lever_job,
    "greenhouse": normalize_greenhouse_job,
}