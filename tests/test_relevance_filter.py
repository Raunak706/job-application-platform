from src.ingestion.relevance_filter import is_relevant


def test_relevant_title_is_accepted():
    assert is_relevant("Software Engineer") is True


def test_senior_title_is_rejected():
    assert is_relevant("Senior Software Engineer") is False


def test_missing_title_is_rejected():
    assert is_relevant(None) is False


def test_empty_title_is_rejected():
    assert is_relevant("") is False