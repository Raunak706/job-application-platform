import argparse
import json
from pathlib import Path

from src.candidate_profile.population import CandidatePopulationService


def load_candidate_data(file_path: str) -> dict:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Candidate data file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Candidate data must be a JSON object."
        )

    return data


def populate_candidate_from_json(
    *,
    candidate_id: int,
    file_path: str,
) -> None:
    if candidate_id <= 0:
        raise ValueError(
            "candidate_id must be greater than zero."
        )

    data = load_candidate_data(file_path)

    population = CandidatePopulationService()

    profile = population.populate_candidate(
        candidate_id=candidate_id,
        data=data,
    )

    print(
        f"Candidate {profile.identity.candidate_id} populated successfully."
    )
    print(
        f"Name: {profile.identity.display_name}"
    )
    print(
        f"Experiences: {len(profile.experiences)}"
    )
    print(
        f"Projects: {len(profile.projects)}"
    )
    print(
        f"Education: {len(profile.education)}"
    )
    print(
        f"Skills: {len(profile.skills)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Populate an existing candidate profile "
            "from a structured JSON file."
        )
    )

    parser.add_argument(
        "--candidate-id",
        type=int,
        required=True,
        help="Existing candidate database ID.",
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Path to the candidate JSON file.",
    )

    args = parser.parse_args()

    populate_candidate_from_json(
        candidate_id=args.candidate_id,
        file_path=args.file,
    )


if __name__ == "__main__":
    main()