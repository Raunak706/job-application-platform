from dataclasses import dataclass
from datetime import date
from typing import TypeAlias


JsonObject: TypeAlias = dict[str, object]


@dataclass(frozen=True, slots=True)
class CandidateIdentity:
    candidate_id: int
    display_name: str
    status: str


@dataclass(frozen=True, slots=True)
class CandidateProfileDetails:
    profile_id: int
    professional_headline: str | None
    professional_summary: str | None
    current_location: str | None
    current_country: str | None


@dataclass(frozen=True, slots=True)
class CandidateContactRecord:
    id: int
    contact_type: str
    contact_value: str
    label: str | None
    is_primary: bool


@dataclass(frozen=True, slots=True)
class CandidateLinkRecord:
    id: int
    link_type: str
    url: str
    label: str | None
    is_primary: bool


@dataclass(frozen=True, slots=True)
class CandidateExperienceRecord:
    id: int
    company: str
    title: str
    employment_type: str | None
    department: str | None
    location: str | None
    country: str | None
    start_date: date | None
    end_date: date | None
    is_current: bool
    description: str | None
    verification_status: str
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidateProjectLinkRecord:
    id: int
    project_id: int
    link_type: str
    url: str
    label: str | None


@dataclass(frozen=True, slots=True)
class CandidateProjectRecord:
    id: int
    name: str
    role: str | None
    organization: str | None
    description: str | None
    problem: str | None
    solution: str | None
    architecture: str | None
    outcome: str | None
    start_date: date | None
    end_date: date | None
    status: str | None
    verification_status: str
    visibility: str


@dataclass(frozen=True, slots=True)
class SkillRecord:
    skill_id: int
    canonical_name: str
    normalized_name: str
    category: str | None


@dataclass(frozen=True, slots=True)
class CandidateSkillRecord:
    id: int
    skill: SkillRecord
    proficiency_level: str | None
    experience_months: int | None
    last_used_date: date | None
    notes: str | None
    verification_status: str
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidateExperienceSkillRecord:
    id: int
    experience_id: int
    skill: SkillRecord
    usage_description: str | None


@dataclass(frozen=True, slots=True)
class CandidateProjectSkillRecord:
    id: int
    project_id: int
    skill: SkillRecord
    usage_description: str | None


@dataclass(frozen=True, slots=True)
class CandidateCourseRecord:
    id: int
    education_id: int
    course_name: str
    course_code: str | None
    grade: str | None
    description: str | None


@dataclass(frozen=True, slots=True)
class CandidateEducationRecord:
    id: int
    institution: str
    degree: str | None
    field_of_study: str | None
    education_level: str | None
    location: str | None
    country: str | None
    start_date: date | None
    end_date: date | None
    graduation_date: date | None
    gpa: str | None
    description: str | None
    verification_status: str
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidateCertificationRecord:
    id: int
    name: str
    issuer: str | None
    credential_id: str | None
    issue_date: date | None
    expiration_date: date | None
    credential_url: str | None
    description: str | None
    verification_status: str
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidateAwardRecord:
    id: int
    name: str
    issuer: str | None
    awarded_date: date | None
    description: str | None
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidatePublicationRecord:
    id: int
    title: str
    publication_type: str | None
    publisher: str | None
    publication_date: date | None
    url: str | None
    description: str | None
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidateActivityRecord:
    id: int
    organization: str | None
    role: str | None
    activity_type: str | None
    start_date: date | None
    end_date: date | None
    description: str | None
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidateAchievementRecord:
    id: int
    experience_id: int | None
    project_id: int | None
    title: str | None
    description: str
    metric_text: str | None
    verification_status: str
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidatePreferenceRecord:
    id: int
    category: str
    preference_key: str
    value_json: JsonObject
    priority: str | None
    is_active: bool


@dataclass(frozen=True, slots=True)
class CandidateApplicationFactRecord:
    id: int
    fact_key: str
    category: str | None
    question_text: str | None
    answer_text: str
    is_sensitive: bool
    verification_status: str
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidateStoryRecord:
    id: int
    title: str
    story_type: str | None
    situation: str | None
    task: str | None
    action: str | None
    result: str | None
    summary: str | None
    verification_status: str
    visibility: str


@dataclass(frozen=True, slots=True)
class CandidateFactRecord:
    id: int
    category: str
    fact_key: str
    value_text: str | None
    value_json: JsonObject | None
    verification_status: str
    confidence: float | None
    visibility: str
    is_sensitive: bool
    valid_from: date | None
    valid_to: date | None
    status: str


@dataclass(frozen=True, slots=True)
class CandidateEvidenceRecord:
    id: int
    source_kind: str
    source_document_id: int | None
    extracted_fact_id: int | None
    target_entity_type: str
    target_entity_id: int
    excerpt: str | None
    locator_json: JsonObject | None
    confidence: float | None
    verification_status: str


@dataclass(frozen=True, slots=True)
class CandidateTagRecord:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class CandidateEntityTagRecord:
    id: int
    tag_id: int
    entity_type: str
    entity_id: int


@dataclass(frozen=True, slots=True)
class CandidateEntityRelationRecord:
    id: int
    from_entity_type: str
    from_entity_id: int
    relation_type: str
    to_entity_type: str
    to_entity_id: int
    metadata_json: JsonObject | None


@dataclass(frozen=True, slots=True)
class CanonicalCandidateProfile:
    identity: CandidateIdentity
    profile: CandidateProfileDetails

    contacts: tuple[CandidateContactRecord, ...]
    links: tuple[CandidateLinkRecord, ...]

    experiences: tuple[CandidateExperienceRecord, ...]
    projects: tuple[CandidateProjectRecord, ...]
    project_links: tuple[CandidateProjectLinkRecord, ...]

    skills: tuple[CandidateSkillRecord, ...]
    experience_skills: tuple[CandidateExperienceSkillRecord, ...]
    project_skills: tuple[CandidateProjectSkillRecord, ...]

    education: tuple[CandidateEducationRecord, ...]
    courses: tuple[CandidateCourseRecord, ...]

    certifications: tuple[CandidateCertificationRecord, ...]
    awards: tuple[CandidateAwardRecord, ...]
    publications: tuple[CandidatePublicationRecord, ...]
    activities: tuple[CandidateActivityRecord, ...]
    achievements: tuple[CandidateAchievementRecord, ...]

    preferences: tuple[CandidatePreferenceRecord, ...]
    application_facts: tuple[CandidateApplicationFactRecord, ...]
    stories: tuple[CandidateStoryRecord, ...]
    facts: tuple[CandidateFactRecord, ...]

    evidence: tuple[CandidateEvidenceRecord, ...]

    tags: tuple[CandidateTagRecord, ...]
    entity_tags: tuple[CandidateEntityTagRecord, ...]
    entity_relations: tuple[CandidateEntityRelationRecord, ...]