US_STATE_ABBREVIATIONS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
}

COUNTRY_NAME_MAPPING = {
    "united states": "US",
    "usa": "US",
    "uk": "GB",
    "united kingdom": "GB",
    "germany": "DE",
    "france": "FR",
    "japan": "JP",
}


def enrich_job(record: dict) -> dict:
    enriched = record.copy()

    location = enriched.get("location")
    country = enriched.get("country")

    if country or not isinstance(location, str):
        return enriched

    location_lower = location.lower()

    for country_name, country_code in COUNTRY_NAME_MAPPING.items():
        if country_name in location_lower:
            enriched["country"] = country_code
            return enriched

    location_parts = (
        location.replace("|", ";")
        .replace(",", ";")
        .split(";")
    )

    for part in location_parts:
        token = part.strip().upper()

        if token in US_STATE_ABBREVIATIONS:
            enriched["country"] = "US"
            return enriched

    return enriched