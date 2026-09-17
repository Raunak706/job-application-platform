import requests


def fetch_jobs(company: str, limit: int = 10) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{company}"

    params = {
        "mode": "json",
        "limit": limit,
    }

    response = requests.get(
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