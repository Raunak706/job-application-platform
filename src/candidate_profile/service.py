from collections.abc import Callable
from datetime import date

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

    def add_experience(
        self,
        candidate_id: int,
        *,
        company: str,
        title: str,
        employment_type: str | None = None,
        department: str | None = None,
        location: str | None = None,
        country: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        is_current: bool = False,
        description: str | None = None,
        verification_status: str = "unverified",
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_experience(
                candidate_id,
                company=company,
                title=title,
                employment_type=employment_type,
                department=department,
                location=location,
                country=country,
                start_date=start_date,
                end_date=end_date,
                is_current=is_current,
                description=description,
                verification_status=verification_status,
                visibility=visibility,
            )

            session.commit()

            return repository.get_profile(candidate_id)

    def add_project(
        self,
        candidate_id: int,
        *,
        name: str,
        role: str | None = None,
        organization: str | None = None,
        description: str | None = None,
        problem: str | None = None,
        solution: str | None = None,
        architecture: str | None = None,
        outcome: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None,
        verification_status: str = "unverified",
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_project(
                candidate_id,
                name=name,
                role=role,
                organization=organization,
                description=description,
                problem=problem,
                solution=solution,
                architecture=architecture,
                outcome=outcome,
                start_date=start_date,
                end_date=end_date,
                status=status,
                verification_status=verification_status,
                visibility=visibility,
            )

            session.commit()

            return repository.get_profile(candidate_id)