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

    def add_project_link(
        self,
        candidate_id: int,
        *,
        project_id: int,
        link_type: str,
        url: str,
        label: str | None = None,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_project_link(
                candidate_id,
                project_id=project_id,
                link_type=link_type,
                url=url,
                label=label,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_education(
        self,
        candidate_id: int,
        *,
        institution: str,
        degree: str | None = None,
        field_of_study: str | None = None,
        education_level: str | None = None,
        location: str | None = None,
        country: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        graduation_date: date | None = None,
        gpa: str | None = None,
        description: str | None = None,
        verification_status: str = "unverified",
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_education(
                candidate_id,
                institution=institution,
                degree=degree,
                field_of_study=field_of_study,
                education_level=education_level,
                location=location,
                country=country,
                start_date=start_date,
                end_date=end_date,
                graduation_date=graduation_date,
                gpa=gpa,
                description=description,
                verification_status=verification_status,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_course(
        self,
        candidate_id: int,
        *,
        education_id: int,
        course_name: str,
        course_code: str | None = None,
        grade: str | None = None,
        description: str | None = None,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_course(
                candidate_id,
                education_id=education_id,
                course_name=course_name,
                course_code=course_code,
                grade=grade,
                description=description,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_certification(
        self,
        candidate_id: int,
        *,
        name: str,
        issuer: str | None = None,
        credential_id: str | None = None,
        issue_date: date | None = None,
        expiration_date: date | None = None,
        credential_url: str | None = None,
        description: str | None = None,
        verification_status: str = "unverified",
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_certification(
                candidate_id,
                name=name,
                issuer=issuer,
                credential_id=credential_id,
                issue_date=issue_date,
                expiration_date=expiration_date,
                credential_url=credential_url,
                description=description,
                verification_status=verification_status,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_award(
        self,
        candidate_id: int,
        *,
        name: str,
        issuer: str | None = None,
        awarded_date: date | None = None,
        description: str | None = None,
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_award(
                candidate_id,
                name=name,
                issuer=issuer,
                awarded_date=awarded_date,
                description=description,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_publication(
        self,
        candidate_id: int,
        *,
        title: str,
        publication_type: str | None = None,
        publisher: str | None = None,
        publication_date: date | None = None,
        url: str | None = None,
        description: str | None = None,
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_publication(
                candidate_id,
                title=title,
                publication_type=publication_type,
                publisher=publisher,
                publication_date=publication_date,
                url=url,
                description=description,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_activity(
        self,
        candidate_id: int,
        *,
        organization: str | None = None,
        role: str | None = None,
        activity_type: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        description: str | None = None,
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_activity(
                candidate_id,
                organization=organization,
                role=role,
                activity_type=activity_type,
                start_date=start_date,
                end_date=end_date,
                description=description,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_achievement(
        self,
        candidate_id: int,
        *,
        description: str,
        experience_id: int | None = None,
        project_id: int | None = None,
        title: str | None = None,
        metric_text: str | None = None,
        verification_status: str = "unverified",
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_achievement(
                candidate_id,
                description=description,
                experience_id=experience_id,
                project_id=project_id,
                title=title,
                metric_text=metric_text,
                verification_status=verification_status,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_preference(
        self,
        candidate_id: int,
        *,
        category: str,
        preference_key: str,
        value_json: dict,
        priority: str | None = None,
        is_active: bool = True,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_preference(
                candidate_id,
                category=category,
                preference_key=preference_key,
                value_json=value_json,
                priority=priority,
                is_active=is_active,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_application_fact(
        self,
        candidate_id: int,
        *,
        fact_key: str,
        answer_text: str,
        category: str | None = None,
        question_text: str | None = None,
        is_sensitive: bool = False,
        verification_status: str = "unverified",
        visibility: str = "application_only",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_application_fact(
                candidate_id,
                fact_key=fact_key,
                answer_text=answer_text,
                category=category,
                question_text=question_text,
                is_sensitive=is_sensitive,
                verification_status=verification_status,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_story(
        self,
        candidate_id: int,
        *,
        title: str,
        story_type: str | None = None,
        situation: str | None = None,
        task: str | None = None,
        action: str | None = None,
        result: str | None = None,
        summary: str | None = None,
        verification_status: str = "unverified",
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_story(
                candidate_id,
                title=title,
                story_type=story_type,
                situation=situation,
                task=task,
                action=action,
                result=result,
                summary=summary,
                verification_status=verification_status,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_fact(
        self,
        candidate_id: int,
        *,
        category: str,
        fact_key: str,
        value_text: str | None = None,
        value_json: dict | None = None,
        verification_status: str = "unverified",
        confidence: float | None = None,
        visibility: str = "internal",
        is_sensitive: bool = False,
        valid_from: date | None = None,
        valid_to: date | None = None,
        status: str = "active",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_fact(
                candidate_id,
                category=category,
                fact_key=fact_key,
                value_text=value_text,
                value_json=value_json,
                verification_status=verification_status,
                confidence=confidence,
                visibility=visibility,
                is_sensitive=is_sensitive,
                valid_from=valid_from,
                valid_to=valid_to,
                status=status,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_skill(
        self,
        candidate_id: int,
        *,
        skill_name: str,
        category: str | None = None,
        proficiency_level: str | None = None,
        experience_months: int | None = None,
        last_used_date: date | None = None,
        notes: str | None = None,
        verification_status: str = "unverified",
        visibility: str = "internal",
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_skill(
                candidate_id,
                skill_name=skill_name,
                category=category,
                proficiency_level=proficiency_level,
                experience_months=experience_months,
                last_used_date=last_used_date,
                notes=notes,
                verification_status=verification_status,
                visibility=visibility,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_experience_skill(
        self,
        candidate_id: int,
        *,
        experience_id: int,
        skill_id: int,
        usage_description: str | None = None,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_experience_skill(
                candidate_id,
                experience_id=experience_id,
                skill_id=skill_id,
                usage_description=usage_description,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_project_skill(
        self,
        candidate_id: int,
        *,
        project_id: int,
        skill_id: int,
        usage_description: str | None = None,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_project_skill(
                candidate_id,
                project_id=project_id,
                skill_id=skill_id,
                usage_description=usage_description,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_tag(
        self,
        candidate_id: int,
        *,
        name: str,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_tag(
                candidate_id,
                name=name,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_entity_tag(
        self,
        candidate_id: int,
        *,
        tag_id: int,
        entity_type: str,
        entity_id: int,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_entity_tag(
                candidate_id,
                tag_id=tag_id,
                entity_type=entity_type,
                entity_id=entity_id,
            )

            session.commit()
            return repository.get_profile(candidate_id)

    def add_entity_relation(
        self,
        candidate_id: int,
        *,
        from_entity_type: str,
        from_entity_id: int,
        relation_type: str,
        to_entity_type: str,
        to_entity_id: int,
        metadata_json: dict | None = None,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            repository.add_entity_relation(
                candidate_id,
                from_entity_type=from_entity_type,
                from_entity_id=from_entity_id,
                relation_type=relation_type,
                to_entity_type=to_entity_type,
                to_entity_id=to_entity_id,
                metadata_json=metadata_json,
            )

            session.commit()
            return repository.get_profile(candidate_id)