from collections.abc import Callable

from sqlalchemy.orm import Session

from src.database.models import Candidate, CandidateProfile
from src.database.session import SessionLocal


class CandidateManagementService:
    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def create_candidate(
        self,
        *,
        display_name: str,
        status: str = "active",
    ) -> int:
        display_name = display_name.strip()

        if not display_name:
            raise ValueError("display_name cannot be empty.")

        with self._session_factory() as session:
            candidate = Candidate(
                display_name=display_name,
                status=status,
            )

            session.add(candidate)
            session.flush()

            profile = CandidateProfile(
                candidate_id=candidate.id,
            )

            session.add(profile)
            session.commit()

            return candidate.id
