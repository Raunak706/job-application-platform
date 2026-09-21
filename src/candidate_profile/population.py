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

                existing_profile = repository.get_profile(
                    candidate_id
                )

                entity_refs: dict[tuple[str, str], int] = {
                    ("candidate", "candidate"): candidate_id,
                    (
                        "profile",
                        "profile",
                    ): existing_profile.profile.profile_id,
                }

                existing_experience_ids = {
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
                    ): record.id
                    for record in existing_profile.experiences
                }

                existing_project_ids = {
                    (
                        record.name,
                        record.role,
                        record.organization,
                        record.description,
                        record.problem,
                        record.solution,
                        record.architecture,
                        record.outcome,
                        record.start_date,
                        record.end_date,
                        record.status,
                    ): record.id
                    for record in existing_profile.projects
                }

                existing_education_ids = {
                    (
                        record.institution,
                        record.degree,
                        record.field_of_study,
                        record.education_level,
                        record.location,
                        record.country,
                        record.start_date,
                        record.end_date,
                        record.graduation_date,
                        record.gpa,
                        record.description,
                    ): record.id
                    for record in existing_profile.education
                }

                existing_certification_ids = {
                    (
                        record.name,
                        record.issuer,
                        record.credential_id,
                        record.issue_date,
                        record.expiration_date,
                        record.credential_url,
                        record.description,
                    ): record.id
                    for record in existing_profile.certifications
                }

                existing_award_ids = {
                    (
                        record.name,
                        record.issuer,
                        record.awarded_date,
                        record.description,
                    ): record.id
                    for record in existing_profile.awards
                }

                existing_publication_ids = {
                    (
                        record.title,
                        record.publication_type,
                        record.publisher,
                        record.publication_date,
                        record.url,
                        record.description,
                    ): record.id
                    for record in existing_profile.publications
                }

                existing_activity_ids = {
                    (
                        record.organization,
                        record.role,
                        record.activity_type,
                        record.start_date,
                        record.end_date,
                        record.description,
                    ): record.id
                    for record in existing_profile.activities
                }

                existing_story_ids = {
                    (
                        record.title,
                        record.story_type,
                        record.situation,
                        record.task,
                        record.action,
                        record.result,
                        record.summary,
                    ): record.id
                    for record in existing_profile.stories
                }

                existing_fact_ids = {
                    (
                        record.category,
                        record.fact_key,
                        record.value_text,
                        self._freeze_json(
                            record.value_json
                        ),
                        record.confidence,
                        record.visibility,
                        record.is_sensitive,
                        record.valid_from,
                        record.valid_to,
                        record.status,
                    ): record.id
                    for record in existing_profile.facts
                }

                existing_course_ids = {
                    (
                        record.education_id,
                        record.course_name,
                        record.course_code,
                        record.grade,
                        record.description,
                    ): record.id
                    for record in existing_profile.courses
                }

                existing_achievement_ids = {
                    (
                        record.experience_id,
                        record.project_id,
                        record.title,
                        record.description,
                        record.metric_text,
                        record.verification_status,
                        record.visibility,
                    ): record.id
                    for record in existing_profile.achievements
                }

                for contact in data.get("contacts", []):
                    created_contact = repository.add_contact(
                        candidate_id,
                        contact_type=contact["contact_type"],
                        contact_value=contact["contact_value"],
                        label=contact.get("label"),
                        is_primary=contact.get(
                            "is_primary",
                            False,
                        ),
                    )

                    self._register_ref(
                        entity_refs,
                        "contact",
                        contact.get("ref"),
                        created_contact.id,
                    )

                for link in data.get("links", []):
                    created_link = repository.add_link(
                        candidate_id,
                        link_type=link["link_type"],
                        url=link["url"],
                        label=link.get("label"),
                        is_primary=link.get(
                            "is_primary",
                            False,
                        ),
                    )

                    self._register_ref(
                        entity_refs,
                        "link",
                        link.get("ref"),
                        created_link.id,
                    )

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

                    key = (
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

                    experience_id = existing_experience_ids.get(
                        key
                    )

                    if experience_id is None:
                        created_experience = (
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
                        )

                        experience_id = (
                            created_experience.id
                        )
                        existing_experience_ids[
                            key
                        ] = experience_id

                    self._register_ref(
                        entity_refs,
                        "experience",
                        experience.get("ref"),
                        experience_id,
                    )

                for project in data.get("projects", []):
                    start_date = self._parse_date(
                        project.get("start_date")
                    )

                    end_date = self._parse_date(
                        project.get("end_date")
                    )

                    key = (
                        project["name"],
                        project.get("role"),
                        project.get("organization"),
                        project.get("description"),
                        project.get("problem"),
                        project.get("solution"),
                        project.get("architecture"),
                        project.get("outcome"),
                        start_date,
                        end_date,
                        project.get("status"),
                    )

                    project_id = existing_project_ids.get(
                        key
                    )

                    if project_id is None:
                        created_project = repository.add_project(
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
                            start_date=start_date,
                            end_date=end_date,
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

                        project_id = created_project.id
                        existing_project_ids[
                            key
                        ] = project_id

                    self._register_ref(
                        entity_refs,
                        "project",
                        project.get("ref"),
                        project_id,
                    )

                for project_link in data.get(
                    "project_links",
                    [],
                ):
                    project_id = self._resolve_ref(
                        entity_refs,
                        "project",
                        project_link["project_ref"],
                    )

                    created_project_link = (
                        repository.add_project_link(
                            candidate_id,
                            project_id=project_id,
                            link_type=project_link[
                                "link_type"
                            ],
                            url=project_link["url"],
                            label=project_link.get(
                                "label"
                            ),
                        )
                    )

                    self._register_ref(
                        entity_refs,
                        "project_link",
                        project_link.get("ref"),
                        created_project_link.id,
                    )

                for education in data.get(
                    "education",
                    [],
                ):
                    start_date = self._parse_date(
                        education.get("start_date")
                    )

                    end_date = self._parse_date(
                        education.get("end_date")
                    )

                    graduation_date = self._parse_date(
                        education.get(
                            "graduation_date"
                        )
                    )

                    key = (
                        education["institution"],
                        education.get("degree"),
                        education.get("field_of_study"),
                        education.get("education_level"),
                        education.get("location"),
                        education.get("country"),
                        start_date,
                        end_date,
                        graduation_date,
                        education.get("gpa"),
                        education.get("description"),
                    )

                    education_id = existing_education_ids.get(
                        key
                    )

                    if education_id is None:
                        created_education = (
                            repository.add_education(
                                candidate_id,
                                institution=education[
                                    "institution"
                                ],
                                degree=education.get(
                                    "degree"
                                ),
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
                                start_date=start_date,
                                end_date=end_date,
                                graduation_date=(
                                    graduation_date
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
                        )

                        education_id = created_education.id
                        existing_education_ids[
                            key
                        ] = education_id

                    self._register_ref(
                        entity_refs,
                        "education",
                        education.get("ref"),
                        education_id,
                    )

                for course in data.get("courses", []):
                    education_id = self._resolve_ref(
                        entity_refs,
                        "education",
                        course["education_ref"],
                    )

                    key = (
                        education_id,
                        course["course_name"],
                        course.get("course_code"),
                        course.get("grade"),
                        course.get("description"),
                    )

                    course_id = existing_course_ids.get(
                        key
                    )

                    if course_id is None:
                        created_course = repository.add_course(
                            candidate_id,
                            education_id=education_id,
                            course_name=course[
                                "course_name"
                            ],
                            course_code=course.get(
                                "course_code"
                            ),
                            grade=course.get("grade"),
                            description=course.get(
                                "description"
                            ),
                        )

                        course_id = created_course.id
                        existing_course_ids[
                            key
                        ] = course_id

                    self._register_ref(
                        entity_refs,
                        "course",
                        course.get("ref"),
                        course_id,
                    )

                for certification in data.get(
                    "certifications",
                    [],
                ):
                    issue_date = self._parse_date(
                        certification.get(
                            "issue_date"
                        )
                    )

                    expiration_date = self._parse_date(
                        certification.get(
                            "expiration_date"
                        )
                    )

                    key = (
                        certification["name"],
                        certification.get("issuer"),
                        certification.get(
                            "credential_id"
                        ),
                        issue_date,
                        expiration_date,
                        certification.get(
                            "credential_url"
                        ),
                        certification.get(
                            "description"
                        ),
                    )

                    certification_id = (
                        existing_certification_ids.get(
                            key
                        )
                    )

                    if certification_id is None:
                        created_certification = (
                            repository.add_certification(
                                candidate_id,
                                name=certification[
                                    "name"
                                ],
                                issuer=certification.get(
                                    "issuer"
                                ),
                                credential_id=(
                                    certification.get(
                                        "credential_id"
                                    )
                                ),
                                issue_date=issue_date,
                                expiration_date=(
                                    expiration_date
                                ),
                                credential_url=(
                                    certification.get(
                                        "credential_url"
                                    )
                                ),
                                description=(
                                    certification.get(
                                        "description"
                                    )
                                ),
                                verification_status=(
                                    certification.get(
                                        "verification_status",
                                        "unverified",
                                    )
                                ),
                                visibility=(
                                    certification.get(
                                        "visibility",
                                        "internal",
                                    )
                                ),
                            )
                        )

                        certification_id = (
                            created_certification.id
                        )
                        existing_certification_ids[
                            key
                        ] = certification_id

                    self._register_ref(
                        entity_refs,
                        "certification",
                        certification.get("ref"),
                        certification_id,
                    )

                for award in data.get("awards", []):
                    awarded_date = self._parse_date(
                        award.get("awarded_date")
                    )

                    key = (
                        award["name"],
                        award.get("issuer"),
                        awarded_date,
                        award.get("description"),
                    )

                    award_id = existing_award_ids.get(
                        key
                    )

                    if award_id is None:
                        created_award = repository.add_award(
                            candidate_id,
                            name=award["name"],
                            issuer=award.get("issuer"),
                            awarded_date=awarded_date,
                            description=award.get(
                                "description"
                            ),
                            visibility=award.get(
                                "visibility",
                                "internal",
                            ),
                        )

                        award_id = created_award.id
                        existing_award_ids[key] = award_id

                    self._register_ref(
                        entity_refs,
                        "award",
                        award.get("ref"),
                        award_id,
                    )

                for publication in data.get(
                    "publications",
                    [],
                ):
                    publication_date = self._parse_date(
                        publication.get(
                            "publication_date"
                        )
                    )

                    key = (
                        publication["title"],
                        publication.get(
                            "publication_type"
                        ),
                        publication.get("publisher"),
                        publication_date,
                        publication.get("url"),
                        publication.get("description"),
                    )

                    publication_id = (
                        existing_publication_ids.get(
                            key
                        )
                    )

                    if publication_id is None:
                        created_publication = (
                            repository.add_publication(
                                candidate_id,
                                title=publication[
                                    "title"
                                ],
                                publication_type=(
                                    publication.get(
                                        "publication_type"
                                    )
                                ),
                                publisher=publication.get(
                                    "publisher"
                                ),
                                publication_date=(
                                    publication_date
                                ),
                                url=publication.get(
                                    "url"
                                ),
                                description=(
                                    publication.get(
                                        "description"
                                    )
                                ),
                                visibility=publication.get(
                                    "visibility",
                                    "internal",
                                ),
                            )
                        )

                        publication_id = (
                            created_publication.id
                        )
                        existing_publication_ids[
                            key
                        ] = publication_id

                    self._register_ref(
                        entity_refs,
                        "publication",
                        publication.get("ref"),
                        publication_id,
                    )

                for activity in data.get(
                    "activities",
                    [],
                ):
                    start_date = self._parse_date(
                        activity.get("start_date")
                    )

                    end_date = self._parse_date(
                        activity.get("end_date")
                    )

                    key = (
                        activity.get("organization"),
                        activity.get("role"),
                        activity.get("activity_type"),
                        start_date,
                        end_date,
                        activity.get("description"),
                    )

                    activity_id = existing_activity_ids.get(
                        key
                    )

                    if activity_id is None:
                        created_activity = (
                            repository.add_activity(
                                candidate_id,
                                organization=activity.get(
                                    "organization"
                                ),
                                role=activity.get("role"),
                                activity_type=activity.get(
                                    "activity_type"
                                ),
                                start_date=start_date,
                                end_date=end_date,
                                description=activity.get(
                                    "description"
                                ),
                                visibility=activity.get(
                                    "visibility",
                                    "internal",
                                ),
                            )
                        )

                        activity_id = created_activity.id
                        existing_activity_ids[
                            key
                        ] = activity_id

                    self._register_ref(
                        entity_refs,
                        "activity",
                        activity.get("ref"),
                        activity_id,
                    )

                for achievement in data.get(
                    "achievements",
                    [],
                ):
                    experience_id = None
                    project_id = None

                    if achievement.get(
                        "experience_ref"
                    ) is not None:
                        experience_id = self._resolve_ref(
                            entity_refs,
                            "experience",
                            achievement[
                                "experience_ref"
                            ],
                        )

                    if achievement.get(
                        "project_ref"
                    ) is not None:
                        project_id = self._resolve_ref(
                            entity_refs,
                            "project",
                            achievement[
                                "project_ref"
                            ],
                        )

                    verification_status = (
                        achievement.get(
                            "verification_status",
                            "unverified",
                        )
                    )

                    visibility = achievement.get(
                        "visibility",
                        "internal",
                    )

                    key = (
                        experience_id,
                        project_id,
                        achievement.get("title"),
                        achievement["description"],
                        achievement.get("metric_text"),
                        verification_status,
                        visibility,
                    )

                    achievement_id = (
                        existing_achievement_ids.get(
                            key
                        )
                    )

                    if achievement_id is None:
                        created_achievement = (
                            repository.add_achievement(
                                candidate_id,
                                description=achievement[
                                    "description"
                                ],
                                experience_id=(
                                    experience_id
                                ),
                                project_id=project_id,
                                title=achievement.get(
                                    "title"
                                ),
                                metric_text=(
                                    achievement.get(
                                        "metric_text"
                                    )
                                ),
                                verification_status=(
                                    verification_status
                                ),
                                visibility=visibility,
                            )
                        )

                        achievement_id = (
                            created_achievement.id
                        )
                        existing_achievement_ids[
                            key
                        ] = achievement_id

                    self._register_ref(
                        entity_refs,
                        "achievement",
                        achievement.get("ref"),
                        achievement_id,
                    )

                for skill in data.get("skills", []):
                    created_skill = repository.add_skill(
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
                            skill.get(
                                "last_used_date"
                            )
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

                    self._register_ref(
                        entity_refs,
                        "skill",
                        skill.get("ref"),
                        created_skill.skill_id,
                    )

                for experience_skill in data.get(
                    "experience_skills",
                    [],
                ):
                    experience_id = self._resolve_ref(
                        entity_refs,
                        "experience",
                        experience_skill[
                            "experience_ref"
                        ],
                    )

                    skill_id = self._resolve_ref(
                        entity_refs,
                        "skill",
                        experience_skill["skill_ref"],
                    )

                    created_experience_skill = (
                        repository.add_experience_skill(
                            candidate_id,
                            experience_id=experience_id,
                            skill_id=skill_id,
                            usage_description=(
                                experience_skill.get(
                                    "usage_description"
                                )
                            ),
                        )
                    )

                    self._register_ref(
                        entity_refs,
                        "experience_skill",
                        experience_skill.get("ref"),
                        created_experience_skill.id,
                    )

                for project_skill in data.get(
                    "project_skills",
                    [],
                ):
                    project_id = self._resolve_ref(
                        entity_refs,
                        "project",
                        project_skill["project_ref"],
                    )

                    skill_id = self._resolve_ref(
                        entity_refs,
                        "skill",
                        project_skill["skill_ref"],
                    )

                    created_project_skill = (
                        repository.add_project_skill(
                            candidate_id,
                            project_id=project_id,
                            skill_id=skill_id,
                            usage_description=(
                                project_skill.get(
                                    "usage_description"
                                )
                            ),
                        )
                    )

                    self._register_ref(
                        entity_refs,
                        "project_skill",
                        project_skill.get("ref"),
                        created_project_skill.id,
                    )

                for preference in data.get(
                    "preferences",
                    [],
                ):
                    created_preference = (
                        repository.add_preference(
                            candidate_id,
                            category=preference[
                                "category"
                            ],
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
                    )

                    self._register_ref(
                        entity_refs,
                        "preference",
                        preference.get("ref"),
                        created_preference.id,
                    )

                for application_fact in data.get(
                    "application_facts",
                    [],
                ):
                    created_application_fact = (
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
                            question_text=(
                                application_fact.get(
                                    "question_text"
                                )
                            ),
                            is_sensitive=(
                                application_fact.get(
                                    "is_sensitive",
                                    False,
                                )
                            ),
                            verification_status=(
                                application_fact.get(
                                    "verification_status",
                                    "unverified",
                                )
                            ),
                            visibility=(
                                application_fact.get(
                                    "visibility",
                                    "application_only",
                                )
                            ),
                        )
                    )

                    self._register_ref(
                        entity_refs,
                        "application_fact",
                        application_fact.get("ref"),
                        created_application_fact.id,
                    )

                for story in data.get("stories", []):
                    key = (
                        story["title"],
                        story.get("story_type"),
                        story.get("situation"),
                        story.get("task"),
                        story.get("action"),
                        story.get("result"),
                        story.get("summary"),
                    )

                    story_id = existing_story_ids.get(key)

                    if story_id is None:
                        created_story = repository.add_story(
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

                        story_id = created_story.id
                        existing_story_ids[key] = story_id

                    self._register_ref(
                        entity_refs,
                        "story",
                        story.get("ref"),
                        story_id,
                    )

                for fact in data.get("facts", []):
                    valid_from = self._parse_date(
                        fact.get("valid_from")
                    )

                    valid_to = self._parse_date(
                        fact.get("valid_to")
                    )

                    value_json = fact.get("value_json")

                    key = (
                        fact["category"],
                        fact["fact_key"],
                        fact.get("value_text"),
                        self._freeze_json(value_json),
                        fact.get("confidence"),
                        fact.get(
                            "visibility",
                            "internal",
                        ),
                        fact.get(
                            "is_sensitive",
                            False,
                        ),
                        valid_from,
                        valid_to,
                        fact.get(
                            "status",
                            "active",
                        ),
                    )

                    fact_id = existing_fact_ids.get(key)

                    if fact_id is None:
                        created_fact = repository.add_fact(
                            candidate_id,
                            category=fact["category"],
                            fact_key=fact["fact_key"],
                            value_text=fact.get(
                                "value_text"
                            ),
                            value_json=value_json,
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
                            valid_from=valid_from,
                            valid_to=valid_to,
                            status=fact.get(
                                "status",
                                "active",
                            ),
                        )

                        fact_id = created_fact.id
                        existing_fact_ids[key] = fact_id

                    self._register_ref(
                        entity_refs,
                        "fact",
                        fact.get("ref"),
                        fact_id,
                    )

                tag_ref_to_id: dict[str, int] = {}

                for tag in data.get("tags", []):
                    created_tag = repository.add_tag(
                        candidate_id,
                        name=tag["name"],
                    )

                    tag_ref = tag.get("ref")

                    if tag_ref is not None:
                        normalized_ref = self._normalize_ref(
                            tag_ref,
                            "Tag ref",
                        )

                        existing_tag_id = (
                            tag_ref_to_id.get(
                                normalized_ref
                            )
                        )

                        if (
                            existing_tag_id is not None
                            and existing_tag_id
                            != created_tag.id
                        ):
                            raise ValueError(
                                f"Duplicate tag ref: "
                                f"{normalized_ref!r}."
                            )

                        tag_ref_to_id[
                            normalized_ref
                        ] = created_tag.id

                for entity_tag in data.get(
                    "entity_tags",
                    [],
                ):
                    tag_ref = self._normalize_ref(
                        entity_tag["tag_ref"],
                        "tag_ref",
                    )

                    tag_id = tag_ref_to_id.get(
                        tag_ref
                    )

                    if tag_id is None:
                        raise ValueError(
                            f"Unknown tag_ref: "
                            f"{tag_ref!r}."
                        )

                    entity_type = entity_tag[
                        "entity_type"
                    ]

                    entity_id = self._resolve_ref(
                        entity_refs,
                        entity_type,
                        entity_tag["entity_ref"],
                    )

                    repository.add_entity_tag(
                        candidate_id,
                        tag_id=tag_id,
                        entity_type=entity_type,
                        entity_id=entity_id,
                    )

                for relation in data.get(
                    "entity_relations",
                    [],
                ):
                    from_entity_type = relation[
                        "from_entity_type"
                    ]
                    to_entity_type = relation[
                        "to_entity_type"
                    ]

                    from_entity_id = self._resolve_ref(
                        entity_refs,
                        from_entity_type,
                        relation["from_entity_ref"],
                    )

                    to_entity_id = self._resolve_ref(
                        entity_refs,
                        to_entity_type,
                        relation["to_entity_ref"],
                    )

                    repository.add_entity_relation(
                        candidate_id,
                        from_entity_type=(
                            from_entity_type
                        ),
                        from_entity_id=from_entity_id,
                        relation_type=relation[
                            "relation_type"
                        ],
                        to_entity_type=to_entity_type,
                        to_entity_id=to_entity_id,
                        metadata_json=relation.get(
                            "metadata_json"
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
    def _register_ref(
        entity_refs: dict[tuple[str, str], int],
        entity_type: str,
        ref_value: object,
        entity_id: int,
    ) -> None:
        if ref_value is None:
            return

        normalized_ref = (
            CandidatePopulationService._normalize_ref(
                ref_value,
                f"{entity_type} ref",
            )
        )

        key = (
            entity_type,
            normalized_ref,
        )

        existing_id = entity_refs.get(key)

        if (
            existing_id is not None
            and existing_id != entity_id
        ):
            raise ValueError(
                f"Duplicate {entity_type} ref: "
                f"{normalized_ref!r}."
            )

        entity_refs[key] = entity_id

    @staticmethod
    def _resolve_ref(
        entity_refs: dict[tuple[str, str], int],
        entity_type: str,
        ref_value: object,
    ) -> int:
        normalized_ref = (
            CandidatePopulationService._normalize_ref(
                ref_value,
                f"{entity_type}_ref",
            )
        )

        entity_id = entity_refs.get(
            (
                entity_type,
                normalized_ref,
            )
        )

        if entity_id is None:
            raise ValueError(
                f"Unknown {entity_type}_ref: "
                f"{normalized_ref!r}."
            )

        return entity_id

    @staticmethod
    def _normalize_ref(
        value: object,
        label: str,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError(
                f"{label} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{label} cannot be empty."
            )

        return normalized

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

    @staticmethod
    def _freeze_json(
        value: object,
    ) -> object:
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        CandidatePopulationService._freeze_json(
                            nested_value
                        ),
                    )
                    for key, nested_value in value.items()
                )
            )

        if isinstance(value, list):
            return tuple(
                CandidatePopulationService._freeze_json(
                    item
                )
                for item in value
            )

        return value