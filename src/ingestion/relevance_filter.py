TARGET_KEYWORDS = [
    "data engineer",
    "data analyst",
    "data scientist",
    "analytics engineer",
    "machine learning",
    "ml engineer",
    "ai engineer",
    "software engineer",
    "backend engineer",
    "cloud engineer",
]

EXCLUDED_SENIORITY = [
    "senior",
    "sr.",
    "sr ",
    "director",
    "principal",
    "staff",
    "lead",
    "manager",
    "head",
    "vp",
    "vice president",
]


def is_relevant(title: str) -> bool:
    title = title.lower()

    if any(
        seniority in title
        for seniority in EXCLUDED_SENIORITY
    ):
        return False

    return any(
        keyword in title
        for keyword in TARGET_KEYWORDS
    )