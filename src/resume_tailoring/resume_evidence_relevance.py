import re


SEMANTIC_CONCEPTS = (
    {
        "job_terms": (
            "speech recognition",
            "automatic speech recognition",
            "asr",
        ),
        "evidence_any": (
            "whisper asr",
            "whisper",
            "automatic speech recognition",
            "speech recognition",
        ),
    },
    {
        "job_terms": (
            "machine translation",
            "neural machine translation",
            "multilingual translation",
        ),
        "evidence_any": (
            "marianmt",
            "machine translation",
            "neural machine translation",
        ),
    },
    {
        "job_terms": (
            "speech translation",
            "spoken language translation",
        ),
        "evidence_all_groups": (
            (
                "whisper asr",
                "whisper",
                "speech recognition",
                "automatic speech recognition",
            ),
            (
                "marianmt",
                "machine translation",
                "neural machine translation",
            ),
        ),
    },
    {
        "job_terms": (
            "signal processing",
            "digital signal processing",
            "frequency domain analysis",
            "spectral analysis",
        ),
        "evidence_any": (
            "signal processing",
            "fft",
            "fast fourier transform",
            "eeg",
        ),
    },
    {
        "job_terms": (
            "heterogeneous data integration",
            "heterogeneous database",
            "heterogeneous databases",
            "federated database",
            "federated databases",
            "federated querying",
            "relational and document databases",
            "relational and nosql databases",
        ),
        "evidence_all_groups": (
            (
                "postgresql",
                "postgres",
                "relational database",
            ),
            (
                "mongodb",
                "document database",
                "nosql",
            ),
        ),
    },
)


def score_resume_evidence(
    *,
    job_text: str | None,
    evidence_terms,
) -> int:
    normalized_job_text = _normalize_text(job_text or "")

    normalized_evidence_terms = {
        _normalize_text(term)
        for term in evidence_terms
        if term
    }

    if not normalized_job_text or not normalized_evidence_terms:
        return 0

    score = _count_direct_matches(
        job_text=normalized_job_text,
        evidence_terms=normalized_evidence_terms,
    )

    for concept in SEMANTIC_CONCEPTS:
        if not _job_mentions_concept(
            normalized_job_text,
            concept["job_terms"],
        ):
            continue

        if _evidence_supports_concept(
            normalized_evidence_terms,
            concept,
        ):
            score += 1

    return score


def _count_direct_matches(
    *,
    job_text: str,
    evidence_terms: set[str],
) -> int:
    return sum(
        1
        for term in evidence_terms
        if term and _contains_phrase(job_text, term)
    )


def _job_mentions_concept(
    job_text: str,
    job_terms,
) -> bool:
    return any(
        _contains_phrase(
            job_text,
            _normalize_text(term),
        )
        for term in job_terms
    )


def _evidence_supports_concept(
    evidence_terms: set[str],
    concept,
) -> bool:
    evidence_any = concept.get("evidence_any")

    if evidence_any is not None:
        return any(
            _normalize_text(term) in evidence_terms
            for term in evidence_any
        )

    evidence_all_groups = concept.get(
        "evidence_all_groups",
        (),
    )

    return all(
        any(
            _normalize_text(term) in evidence_terms
            for term in group
        )
        for group in evidence_all_groups
    )


def _contains_phrase(
    text: str,
    phrase: str,
) -> bool:
    if not phrase:
        return False

    return (
        f" {phrase} "
        in f" {text} "
    )


def _normalize_text(value: str) -> str:
    normalized = value.casefold()
    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        normalized,
    )
    return " ".join(
        normalized.split()
    )