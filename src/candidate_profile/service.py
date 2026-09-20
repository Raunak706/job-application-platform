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

    def update_profile_details(
        self,
        candidate_id: int,
        *,
        professional_headline: str | None,
        professional_summary: str | None,
        current_location: str | None,
        current_country: str | None,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.update_profile_details(
                candidate_id,
                professional_headline=professional_headline,
                professional_summary=professional_summary,
                current_location=current_location,
                current_country=current_country,
            )

            session.commit()

            return repository.get_profile(candidate_id)

    def add_contact(
        self,
        candidate_id: int,
        *,
        contact_type: str,
        contact_value: str,
        label: str | None = None,
        is_primary: bool = False,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_contact(
                candidate_id,
                contact_type=contact_type,
                contact_value=contact_value,
                label=label,
                is_primary=is_primary,
            )

            session.commit()

            return repository.get_profile(candidate_id)

    def add_link(
        self,
        candidate_id: int,
        *,
        link_type: str,
        url: str,
        label: str | None = None,
        is_primary: bool = False,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_link(
                candidate_id,
                link_type=link_type,
                url=url,
                label=label,
                is_primary=is_primary,
            )

            session.commit()

            return repository.get_profile(candidate_id)