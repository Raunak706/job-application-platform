from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date

from src.candidate_profile.contracts import (
    CandidateAchievementRecord,
    CandidateActivityRecord,
    CandidateApplicationFactRecord,
    CandidateAwardRecord,
    CandidateCertificationRecord,
    CandidateContactRecord,
    CandidateCourseRecord,
    CandidateEducationRecord,
    CandidateEntityRelationRecord,
    CandidateEntityTagRecord,
    CandidateEvidenceRecord,
    CandidateExperienceRecord,
    CandidateExperienceSkillRecord,
    CandidateFactRecord,
    CandidateIdentity,
    CandidateLinkRecord,
    CandidatePreferenceRecord,
    CandidateProfileDetails,
    CandidateProjectLinkRecord,
    CandidateProjectRecord,
    CandidateProjectSkillRecord,
    CandidatePublicationRecord,
    CandidateSkillRecord,
    CandidateStoryRecord,
    CandidateTagRecord,
    CanonicalCandidateProfile,
    SkillRecord,
)

from src.database.models import (
    Candidate,
    CandidateAchievement,
    CandidateActivity,
    CandidateApplicationFact,
    CandidateAward,
    CandidateCertification,
    CandidateContact,
    CandidateCourse,
    CandidateEducation,
    CandidateEntityRelation,
    CandidateEntityTag,
    CandidateEvidence,
    CandidateExperience,
    CandidateExperienceSkill,
    CandidateFact,
    CandidateLink,
    CandidatePreference,
    CandidateProfile,
    CandidateProject,
    CandidateProjectLink,
    CandidateProjectSkill,
    CandidatePublication,
    CandidateSkill,
    CandidateStory,
    CandidateTag,
    Skill,
)


class CandidateNotFoundError(LookupError):
    """Raised when a requested candidate does not exist."""


class CandidateProfileIntegrityError(RuntimeError):
    """Raised when canonical candidate data is structurally incomplete."""


class CandidateProfileRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_profile(self, candidate_id: int) -> CanonicalCandidateProfile:

        candidate = self.session.scalar(
            select(Candidate).where(Candidate.id == candidate_id)
        )

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate {candidate_id} does not exist."
            )

        profile = self.session.scalar(
            select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
        )

        if profile is None:
            raise CandidateProfileIntegrityError(
                f"Candidate {candidate_id} has no canonical profile row."
            )

        contacts = self.session.scalars(
            select(CandidateContact)
            .where(CandidateContact.candidate_id == candidate_id)
            .order_by(CandidateContact.id)
        ).all()

        links = self.session.scalars(
            select(CandidateLink)
            .where(CandidateLink.candidate_id == candidate_id)
            .order_by(CandidateLink.id)
        ).all()

        experiences = self.session.scalars(
            select(CandidateExperience)
            .where(CandidateExperience.candidate_id == candidate_id)
            .order_by(CandidateExperience.id)
        ).all()

        projects = self.session.scalars(
            select(CandidateProject)
            .where(CandidateProject.candidate_id == candidate_id)
            .order_by(CandidateProject.id)
        ).all()

        education = self.session.scalars(
            select(CandidateEducation)
            .where(CandidateEducation.candidate_id == candidate_id)
            .order_by(CandidateEducation.id)
        ).all()

        certifications = self.session.scalars(
            select(CandidateCertification)
            .where(CandidateCertification.candidate_id == candidate_id)
            .order_by(CandidateCertification.id)
        ).all()

        awards = self.session.scalars(
            select(CandidateAward)
            .where(CandidateAward.candidate_id == candidate_id)
            .order_by(CandidateAward.id)
        ).all()

        publications = self.session.scalars(
            select(CandidatePublication)
            .where(CandidatePublication.candidate_id == candidate_id)
            .order_by(CandidatePublication.id)
        ).all()

        activities = self.session.scalars(
            select(CandidateActivity)
            .where(CandidateActivity.candidate_id == candidate_id)
            .order_by(CandidateActivity.id)
        ).all()

        achievements = self.session.scalars(
            select(CandidateAchievement)
            .where(CandidateAchievement.candidate_id == candidate_id)
            .order_by(CandidateAchievement.id)
        ).all()

        preferences = self.session.scalars(
            select(CandidatePreference)
            .where(CandidatePreference.candidate_id == candidate_id)
            .order_by(CandidatePreference.id)
        ).all()

        application_facts = self.session.scalars(
            select(CandidateApplicationFact)
            .where(CandidateApplicationFact.candidate_id == candidate_id)
            .order_by(CandidateApplicationFact.id)
        ).all()

        stories = self.session.scalars(
            select(CandidateStory)
            .where(CandidateStory.candidate_id == candidate_id)
            .order_by(CandidateStory.id)
        ).all()

        facts = self.session.scalars(
            select(CandidateFact)
            .where(CandidateFact.candidate_id == candidate_id)
            .order_by(CandidateFact.id)
        ).all()

        evidence = self.session.scalars(
            select(CandidateEvidence)
            .where(CandidateEvidence.candidate_id == candidate_id)
            .order_by(CandidateEvidence.id)
        ).all()

        tags = self.session.scalars(
            select(CandidateTag)
            .where(CandidateTag.candidate_id == candidate_id)
            .order_by(CandidateTag.id)
        ).all()

        entity_relations = self.session.scalars(
            select(CandidateEntityRelation)
            .where(CandidateEntityRelation.candidate_id == candidate_id)
            .order_by(CandidateEntityRelation.id)
        ).all()

        experience_ids = [record.id for record in experiences]
        project_ids = [record.id for record in projects]
        education_ids = [record.id for record in education]
        tag_ids = [record.id for record in tags]

        project_links = []

        if project_ids:
            project_links = self.session.scalars(
                select(CandidateProjectLink)
                .where(CandidateProjectLink.project_id.in_(project_ids))
                .order_by(CandidateProjectLink.id)
            ).all()

        courses = []

        if education_ids:
            courses = self.session.scalars(
                select(CandidateCourse)
                .where(CandidateCourse.education_id.in_(education_ids))
                .order_by(CandidateCourse.id)
            ).all()

        entity_tags = []

        if tag_ids:
            entity_tags = self.session.scalars(
                select(CandidateEntityTag)
                .where(CandidateEntityTag.tag_id.in_(tag_ids))
                .order_by(CandidateEntityTag.id)
            ).all()

        candidate_skill_rows = self.session.execute(
            select(CandidateSkill, Skill)
            .join(Skill, CandidateSkill.skill_id == Skill.id)
            .where(CandidateSkill.candidate_id == candidate_id)
            .order_by(CandidateSkill.id)
        ).all()

        experience_skill_rows = []

        if experience_ids:
            experience_skill_rows = self.session.execute(
                select(CandidateExperienceSkill, Skill)
                .join(
                    Skill,
                    CandidateExperienceSkill.skill_id == Skill.id,
                )
                .where(
                    CandidateExperienceSkill.experience_id.in_(
                        experience_ids
                    )
                )
                .order_by(CandidateExperienceSkill.id)
            ).all()

        project_skill_rows = []

        if project_ids:
            project_skill_rows = self.session.execute(
                select(CandidateProjectSkill, Skill)
                .join(
                    Skill,
                    CandidateProjectSkill.skill_id == Skill.id,
                )
                .where(
                    CandidateProjectSkill.project_id.in_(project_ids)
                )
                .order_by(CandidateProjectSkill.id)
            ).all()

        return CanonicalCandidateProfile(
            identity=CandidateIdentity(
                candidate_id=candidate.id,
                display_name=candidate.display_name,
                status=candidate.status,
            ),
            profile=CandidateProfileDetails(
                profile_id=profile.id,
                professional_headline=profile.professional_headline,
                professional_summary=profile.professional_summary,
                current_location=profile.current_location,
                current_country=profile.current_country,
            ),
            contacts=tuple(
                CandidateContactRecord(
                    id=record.id,
                    contact_type=record.contact_type,
                    contact_value=record.contact_value,
                    label=record.label,
                    is_primary=record.is_primary,
                )
                for record in contacts
            ),
            links=tuple(
                CandidateLinkRecord(
                    id=record.id,
                    link_type=record.link_type,
                    url=record.url,
                    label=record.label,
                    is_primary=record.is_primary,
                )
                for record in links
            ),
            experiences=tuple(
                CandidateExperienceRecord(
                    id=record.id,
                    company=record.company,
                    title=record.title,
                    employment_type=record.employment_type,
                    department=record.department,
                    location=record.location,
                    country=record.country,
                    start_date=record.start_date,
                    end_date=record.end_date,
                    is_current=record.is_current,
                    description=record.description,
                    verification_status=record.verification_status,
                    visibility=record.visibility,
                )
                for record in experiences
            ),
            projects=tuple(
                CandidateProjectRecord(
                    id=record.id,
                    name=record.name,
                    role=record.role,
                    organization=record.organization,
                    description=record.description,
                    problem=record.problem,
                    solution=record.solution,
                    architecture=record.architecture,
                    outcome=record.outcome,
                    start_date=record.start_date,
                    end_date=record.end_date,
                    status=record.status,
                    verification_status=record.verification_status,
                    visibility=record.visibility,
                )
                for record in projects
            ),
            project_links=tuple(
                CandidateProjectLinkRecord(
                    id=record.id,
                    project_id=record.project_id,
                    link_type=record.link_type,
                    url=record.url,
                    label=record.label,
                )
                for record in project_links
            ),
            skills=tuple(
                CandidateSkillRecord(
                    id=candidate_skill.id,
                    skill=self._skill_record(skill),
                    proficiency_level=candidate_skill.proficiency_level,
                    experience_months=candidate_skill.experience_months,
                    last_used_date=candidate_skill.last_used_date,
                    notes=candidate_skill.notes,
                    verification_status=(
                        candidate_skill.verification_status
                    ),
                    visibility=candidate_skill.visibility,
                )
                for candidate_skill, skill in candidate_skill_rows
            ),
            experience_skills=tuple(
                CandidateExperienceSkillRecord(
                    id=experience_skill.id,
                    experience_id=experience_skill.experience_id,
                    skill=self._skill_record(skill),
                    usage_description=experience_skill.usage_description,
                )
                for experience_skill, skill in experience_skill_rows
            ),
            project_skills=tuple(
                CandidateProjectSkillRecord(
                    id=project_skill.id,
                    project_id=project_skill.project_id,
                    skill=self._skill_record(skill),
                    usage_description=project_skill.usage_description,
                )
                for project_skill, skill in project_skill_rows
            ),
            education=tuple(
                CandidateEducationRecord(
                    id=record.id,
                    institution=record.institution,
                    degree=record.degree,
                    field_of_study=record.field_of_study,
                    education_level=record.education_level,
                    location=record.location,
                    country=record.country,
                    start_date=record.start_date,
                    end_date=record.end_date,
                    graduation_date=record.graduation_date,
                    gpa=record.gpa,
                    description=record.description,
                    verification_status=record.verification_status,
                    visibility=record.visibility,
                )
                for record in education
            ),
            courses=tuple(
                CandidateCourseRecord(
                    id=record.id,
                    education_id=record.education_id,
                    course_name=record.course_name,
                    course_code=record.course_code,
                    grade=record.grade,
                    description=record.description,
                )
                for record in courses
            ),
            certifications=tuple(
                CandidateCertificationRecord(
                    id=record.id,
                    name=record.name,
                    issuer=record.issuer,
                    credential_id=record.credential_id,
                    issue_date=record.issue_date,
                    expiration_date=record.expiration_date,
                    credential_url=record.credential_url,
                    description=record.description,
                    verification_status=record.verification_status,
                    visibility=record.visibility,
                )
                for record in certifications
            ),
            awards=tuple(
                CandidateAwardRecord(
                    id=record.id,
                    name=record.name,
                    issuer=record.issuer,
                    awarded_date=record.awarded_date,
                    description=record.description,
                    visibility=record.visibility,
                )
                for record in awards
            ),
            publications=tuple(
                CandidatePublicationRecord(
                    id=record.id,
                    title=record.title,
                    publication_type=record.publication_type,
                    publisher=record.publisher,
                    publication_date=record.publication_date,
                    url=record.url,
                    description=record.description,
                    visibility=record.visibility,
                )
                for record in publications
            ),
            activities=tuple(
                CandidateActivityRecord(
                    id=record.id,
                    organization=record.organization,
                    role=record.role,
                    activity_type=record.activity_type,
                    start_date=record.start_date,
                    end_date=record.end_date,
                    description=record.description,
                    visibility=record.visibility,
                )
                for record in activities
            ),
            achievements=tuple(
                CandidateAchievementRecord(
                    id=record.id,
                    experience_id=record.experience_id,
                    project_id=record.project_id,
                    title=record.title,
                    description=record.description,
                    metric_text=record.metric_text,
                    verification_status=record.verification_status,
                    visibility=record.visibility,
                )
                for record in achievements
            ),
            preferences=tuple(
                CandidatePreferenceRecord(
                    id=record.id,
                    category=record.category,
                    preference_key=record.preference_key,
                    value_json=record.value_json,
                    priority=record.priority,
                    is_active=record.is_active,
                )
                for record in preferences
            ),
            application_facts=tuple(
                CandidateApplicationFactRecord(
                    id=record.id,
                    fact_key=record.fact_key,
                    category=record.category,
                    question_text=record.question_text,
                    answer_text=record.answer_text,
                    is_sensitive=record.is_sensitive,
                    verification_status=record.verification_status,
                    visibility=record.visibility,
                )
                for record in application_facts
            ),
            stories=tuple(
                CandidateStoryRecord(
                    id=record.id,
                    title=record.title,
                    story_type=record.story_type,
                    situation=record.situation,
                    task=record.task,
                    action=record.action,
                    result=record.result,
                    summary=record.summary,
                    verification_status=record.verification_status,
                    visibility=record.visibility,
                )
                for record in stories
            ),
            facts=tuple(
                CandidateFactRecord(
                    id=record.id,
                    category=record.category,
                    fact_key=record.fact_key,
                    value_text=record.value_text,
                    value_json=record.value_json,
                    verification_status=record.verification_status,
                    confidence=record.confidence,
                    visibility=record.visibility,
                    is_sensitive=record.is_sensitive,
                    valid_from=record.valid_from,
                    valid_to=record.valid_to,
                    status=record.status,
                )
                for record in facts
            ),
            evidence=tuple(
                CandidateEvidenceRecord(
                    id=record.id,
                    source_kind=record.source_kind,
                    source_document_id=record.source_document_id,
                    extracted_fact_id=record.extracted_fact_id,
                    target_entity_type=record.target_entity_type,
                    target_entity_id=record.target_entity_id,
                    excerpt=record.excerpt,
                    locator_json=record.locator_json,
                    confidence=record.confidence,
                    verification_status=record.verification_status,
                )
                for record in evidence
            ),
            tags=tuple(
                CandidateTagRecord(
                    id=record.id,
                    name=record.name,
                )
                for record in tags
            ),
            entity_tags=tuple(
                CandidateEntityTagRecord(
                    id=record.id,
                    tag_id=record.tag_id,
                    entity_type=record.entity_type,
                    entity_id=record.entity_id,
                )
                for record in entity_tags
            ),
            entity_relations=tuple(
                CandidateEntityRelationRecord(
                    id=record.id,
                    from_entity_type=record.from_entity_type,
                    from_entity_id=record.from_entity_id,
                    relation_type=record.relation_type,
                    to_entity_type=record.to_entity_type,
                    to_entity_id=record.to_entity_id,
                    metadata_json=record.metadata_json,
                )
                for record in entity_relations
            ),
        )

    def update_profile_details(
        self,
        candidate_id: int,
        *,
        professional_headline: str | None = None,
        professional_summary: str | None = None,
        current_location: str | None = None,
        current_country: str | None = None,
    ) -> CandidateProfile:
        self._require_candidate(candidate_id)

        profile = self.session.scalar(
            select(CandidateProfile).where(
                CandidateProfile.candidate_id == candidate_id
            )
        )

        if profile is None:
            raise CandidateProfileIntegrityError(
                f"Candidate {candidate_id} has no canonical profile row."
            )

        profile.professional_headline = professional_headline
        profile.professional_summary = professional_summary
        profile.current_location = current_location
        profile.current_country = current_country

        self.session.flush()

        return profile

    def add_contact(
        self,
        candidate_id: int,
        *,
        contact_type: str,
        contact_value: str,
        label: str | None = None,
        is_primary: bool = False,
    ) -> CandidateContact:
        self._require_candidate(candidate_id)

        contact = CandidateContact(
            candidate_id=candidate_id,
            contact_type=contact_type,
            contact_value=contact_value,
            label=label,
            is_primary=is_primary,
        )

        self.session.add(contact)
        self.session.flush()

        return contact

    def add_link(
        self,
        candidate_id: int,
        *,
        link_type: str,
        url: str,
        label: str | None = None,
        is_primary: bool = False,
    ) -> CandidateLink:
        self._require_candidate(candidate_id)

        link = CandidateLink(
            candidate_id=candidate_id,
            link_type=link_type,
            url=url,
            label=label,
            is_primary=is_primary,
        )

        self.session.add(link)
        self.session.flush()

        return link

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
    ) -> CandidateExperience:
        self._require_candidate(candidate_id)

        experience = CandidateExperience(
            candidate_id=candidate_id,
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

        self.session.add(experience)
        self.session.flush()

        return experience

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
    ) -> CandidateProject:
        self._require_candidate(candidate_id)

        project = CandidateProject(
            candidate_id=candidate_id,
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

        self.session.add(project)
        self.session.flush()

        return project

    def _require_candidate(self, candidate_id: int) -> Candidate:
        candidate = self.session.scalar(
            select(Candidate).where(Candidate.id == candidate_id)
        )

        if candidate is None:
            raise CandidateNotFoundError(
                f"Candidate {candidate_id} does not exist."
            )

        return candidate

    @staticmethod
    def _skill_record(skill: Skill) -> SkillRecord:
        return SkillRecord(
            skill_id=skill.id,
            canonical_name=skill.canonical_name,
            normalized_name=skill.normalized_name,
            category=skill.category,
        )