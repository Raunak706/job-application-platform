from src.normalization.enricher import enrich_job


def test_us_state_location_sets_us_country():
    record = {
        "location": "San Francisco, CA",
        "country": None,
    }

    result = enrich_job(record)

    assert result["country"] == "US"


def test_uk_location_sets_gb_country():
    record = {
        "location": "London, UK",
        "country": None,
    }

    result = enrich_job(record)

    assert result["country"] == "GB"


def test_short_country_name_does_not_match_inside_city():
    record = {
        "location": "Mukilteo, WA",
        "country": None,
    }

    result = enrich_job(record)

    assert result["country"] == "US"


def test_existing_country_is_preserved():
    record = {
        "location": "London, UK",
        "country": "US",
    }

    result = enrich_job(record)

    assert result["country"] == "US"
    