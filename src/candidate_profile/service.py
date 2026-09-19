from collections.abc import Callable

from sqlalchemy.orm import Session

from src.candidate_profile.contracts import CanonicalCandidateProfile
from src.candidate_profile.repository import CandidateProfileRepository
from src.database.session import SessionLocal


class CandidateProfileService:
    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def get_profile(
        self,
        candidate_id: int,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)
            return repository.get_profile(candidate_id)