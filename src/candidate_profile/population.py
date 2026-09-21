from collections.abc import Callable
from datetime import date

from sqlalchemy.orm import Session

from src.candidate_profile.contracts import CanonicalCandidateProfile
from src.candidate_profile.repository import CandidateProfileRepository
from src.database.session import SessionLocal


class CandidatePopulationService:
    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
    ) -> None:
        self._session_factory = session_factory

    def populate_candidate(
        self,
        *,
        candidate_id: int,
        data: dict,
    ) -> CanonicalCandidateProfile:
        with self._session_factory() as session:
            repository = CandidateProfileRepository(session)

            try:
                profile_data = data.get("profile")

                if profile_data is not None:
                    repository.update_profile_details(
                        candidate_id,
                        professional_headline=profile_data.get(
                            "professional_headline"
                        ),
                        professional_summary=profile_data.get(
                            "professional_summary"
                        ),
                        current_location=profile_data.get(
                            "current_location"
                        ),
                        current_country=profile_data.get(
                            "current_country"
                        ),
                    )

                for contact in data.get("contacts", []):
                    repository.add_contact(
                        candidate_id,
                        contact_type=contact["contact_type"],
                        contact_value=contact["contact_value"],
                        label=contact.get("label"),
                        is_primary=contact.get(
                            "is_primary",
                            False,
                        ),
                    )

                for link in data.get("links", []):
                    repository.add_link(
                        candidate_id,
                        link_type=link["link_type"],
                        url=link["url"],
                        label=link.get("label"),
                        is_primary=link.get(
                            "is_primary",
                            False,
                        ),
                    )

                existing_profile = repository.get_profile(
                    candidate_id
                )

                existing_experiences = {
                    (
                        record.company,
                        record.title,
                        record.employment_type,
                        record.department,
                        record.location,
                        record.country,
                        record.start_date,
                        record.end_date,
                        record.is_current,
                        record.description,
                    )
                    for record in existing_profile.experiences
                }

                for experience in data.get(
                    "experiences",
                    [],
                ):
                    start_date = self._parse_date(
                        experience.get("start_date")
                    )

                    end_date = self._parse_date(
                        experience.get("end_date")
                    )

                    experience_key = (
                        experience["company"],
                        experience["title"],
                        experience.get("employment_type"),
                        experience.get("department"),
                        experience.get("location"),
                        experience.get("country"),
                        start_date,
                        end_date,
                        experience.get(
                            "is_current",
                            False,
                        ),
                        experience.get("description"),
                    )

                    if (
                        experience_key
                        in existing_experiences
                    ):
                        continue

                    repository.add_experience(
                        candidate_id,
                        company=experience["company"],
                        title=experience["title"],
                        employment_type=experience.get(
                            "employment_type"
                        ),
                        department=experience.get(
                            "department"
                        ),
                        location=experience.get(
                            "location"
                        ),
                        country=experience.get(
                            "country"
                        ),
                        start_date=start_date,
                        end_date=end_date,
                        is_current=experience.get(
                            "is_current",
                            False,
                        ),
                        description=experience.get(
                            "description"
                        ),
                        verification_status=experience.get(
                            "verification_status",
                            "unverified",
                        ),
                        visibility=experience.get(
                            "visibility",
                            "internal",
                        ),
                    )

                    existing_experiences.add(
                        experience_key
                    )

                for project in data.get("projects", []):
                    repository.add_project(
                        candidate_id,
                        name=project["name"],
                        role=project.get("role"),
                        organization=project.get(
                            "organization"
                        ),
                        description=project.get(
                            "description"
                        ),
                        problem=project.get("problem"),
                        solution=project.get("solution"),
                        architecture=project.get(
                            "architecture"
                        ),
                        outcome=project.get("outcome"),
                        start_date=self._parse_date(
                            project.get("start_date")
                        ),
                        end_date=self._parse_date(
                            project.get("end_date")
                        ),
                        status=project.get("status"),
                        verification_status=project.get(
                            "verification_status",
                            "unverified",
                        ),
                        visibility=project.get(
                            "visibility",
                            "internal",
                        ),
                    )

                for education in data.get(
                    "education",
                    [],
                ):
                    repository.add_education(
                        candidate_id,
                        institution=education[
                            "institution"
                        ],
                        degree=education.get("degree"),
                        field_of_study=education.get(
                            "field_of_study"
                        ),
                        education_level=education.get(
                            "education_level"
                        ),
                        location=education.get(
                            "location"
                        ),
                        country=education.get(
                            "country"
                        ),
                        start_date=self._parse_date(
                            education.get("start_date")
                        ),
                        end_date=self._parse_date(
                            education.get("end_date")
                        ),
                        graduation_date=self._parse_date(
                            education.get(
                                "graduation_date"
                            )
                        ),
                        gpa=education.get("gpa"),
                        description=education.get(
                            "description"
                        ),
                        verification_status=education.get(
                            "verification_status",
                            "unverified",
                        ),
                        visibility=education.get(
                            "visibility",
                            "internal",
                        ),
                    )

                for certification in data.get(
                    "certifications",
                    [],
                ):
                    repository.add_certification(
                        candidate_id,
                        name=certification["name"],
                        issuer=certification.get(
                            "issuer"
                        ),
                        credential_id=certification.get(
                            "credential_id"
                        ),
                        issue_date=self._parse_date(
                            certification.get(
                                "issue_date"
                            )
                        ),
                        expiration_date=self._parse_date(
                            certification.get(
                                "expiration_date"
                            )
                        ),
                        credential_url=certification.get(
                            "credential_url"
                        ),
                        description=certification.get(
                            "description"
                        ),
                        verification_status=certification.get(
                            "verification_status",
                            "unverified",
                        ),
                        visibility=certification.get(
                            "visibility",
                            "internal",
                        ),
                    )

                for award in data.get("awards", []):
                    repository.add_award(
                        candidate_id,
                        name=award["name"],
                        issuer=award.get("issuer"),
                        awarded_date=self._parse_date(
                            award.get("awarded_date")
                        ),
                        description=award.get(
                            "description"
                        ),
                        visibility=award.get(
                            "visibility",
                            "internal",
                        ),
                    )

                for publication in data.get(
                    "publications",
                    [],
                ):
                    repository.add_publication(
                        candidate_id,
                        title=publication["title"],
                        publication_type=publication.get(
                            "publication_type"
                        ),
                        publisher=publication.get(
                            "publisher"
                        ),
                        publication_date=self._parse_date(
                            publication.get(
                                "publication_date"
                            )
                        ),
                        url=publication.get("url"),
                        description=publication.get(
                            "description"
                        ),
                        visibility=publication.get(
                            "visibility",
                            "internal",
                        ),
                    )

                for activity in data.get(
                    "activities",
                    [],
                ):
                    repository.add_activity(
                        candidate_id,
                        organization=activity.get(
                            "organization"
                        ),
                        role=activity.get("role"),
                        activity_type=activity.get(
                            "activity_type"
                        ),
                        start_date=self._parse_date(
                            activity.get("start_date")
                        ),
                        end_date=self._parse_date(
                            activity.get("end_date")
                        ),
                        description=activity.get(
                            "description"
                        ),
                        visibility=activity.get(
                            "visibility",
                            "internal",
                        ),
                    )

                for skill in data.get("skills", []):
                    repository.add_skill(
                        candidate_id,
                        skill_name=skill["skill_name"],
                        category=skill.get("category"),
                        proficiency_level=skill.get(
                            "proficiency_level"
                        ),
                        experience_months=skill.get(
                            "experience_months"
                        ),
                        last_used_date=self._parse_date(
                            skill.get("last_used_date")
                        ),
                        notes=skill.get("notes"),
                        verification_status=skill.get(
                            "verification_status",
                            "unverified",
                        ),
                        visibility=skill.get(
                            "visibility",
                            "internal",
                        ),
                    )

                for preference in data.get(
                    "preferences",
                    [],
                ):
                    repository.add_preference(
                        candidate_id,
                        category=preference["category"],
                        preference_key=preference[
                            "preference_key"
                        ],
                        value_json=preference[
                            "value_json"
                        ],
                        priority=preference.get(
                            "priority"
                        ),
                        is_active=preference.get(
                            "is_active",
                            True,
                        ),
                    )

                for application_fact in data.get(
                    "application_facts",
                    [],
                ):
                    repository.add_application_fact(
                        candidate_id,
                        fact_key=application_fact[
                            "fact_key"
                        ],
                        answer_text=application_fact[
                            "answer_text"
                        ],
                        category=application_fact.get(
                            "category"
                        ),
                        question_text=application_fact.get(
                            "question_text"
                        ),
                        is_sensitive=application_fact.get(
                            "is_sensitive",
                            False,
                        ),
                        verification_status=(
                            application_fact.get(
                                "verification_status",
                                "unverified",
                            )
                        ),
                        visibility=application_fact.get(
                            "visibility",
                            "application_only",
                        ),
                    )

                for story in data.get("stories", []):
                    repository.add_story(
                        candidate_id,
                        title=story["title"],
                        story_type=story.get(
                            "story_type"
                        ),
                        situation=story.get(
                            "situation"
                        ),
                        task=story.get("task"),
                        action=story.get("action"),
                        result=story.get("result"),
                        summary=story.get("summary"),
                        verification_status=story.get(
                            "verification_status",
                            "unverified",
                        ),
                        visibility=story.get(
                            "visibility",
                            "internal",
                        ),
                    )

                for fact in data.get("facts", []):
                    repository.add_fact(
                        candidate_id,
                        category=fact["category"],
                        fact_key=fact["fact_key"],
                        value_text=fact.get(
                            "value_text"
                        ),
                        value_json=fact.get(
                            "value_json"
                        ),
                        verification_status=fact.get(
                            "verification_status",
                            "unverified",
                        ),
                        confidence=fact.get(
                            "confidence"
                        ),
                        visibility=fact.get(
                            "visibility",
                            "internal",
                        ),
                        is_sensitive=fact.get(
                            "is_sensitive",
                            False,
                        ),
                        valid_from=self._parse_date(
                            fact.get("valid_from")
                        ),
                        valid_to=self._parse_date(
                            fact.get("valid_to")
                        ),
                        status=fact.get(
                            "status",
                            "active",
                        ),
                    )

                result = repository.get_profile(
                    candidate_id
                )

                session.commit()

                return result

            except Exception:
                session.rollback()
                raise

    @staticmethod
    def _parse_date(
        value: object,
    ) -> date | None:
        if value is None:
            return None

        if isinstance(value, date):
            return value

        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid date value: {value!r}. "
                    "Expected YYYY-MM-DD."
                ) from exc

        raise ValueError(
            f"Invalid date value: {value!r}. "
            "Expected YYYY-MM-DD or date."
        )