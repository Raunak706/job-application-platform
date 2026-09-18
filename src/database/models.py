from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class RawJobPosting(Base):
    __tablename__ = "raw_job_postings"

    __table_args__ = (
        UniqueConstraint(
            "source",
            "source_job_id",
            name="uq_raw_job_source_job_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_job_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    apply_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    raw_payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    source_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class Job(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        UniqueConstraint(
            "source",
            "source_job_id",
            name="uq_jobs_source_job_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    raw_job_posting_id: Mapped[int | None] = mapped_column(
        ForeignKey("raw_job_postings.id"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    workplace_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    employment_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_job_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    apply_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        unique=True,
        nullable=False,
    )

    professional_headline: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    professional_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    current_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    current_country: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CandidateContact(Base):
    __tablename__ = "candidate_contacts"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "contact_type",
            "contact_value",
            name="uq_candidate_contact",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
    )

    contact_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    contact_value: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CandidateLink(Base):
    __tablename__ = "candidate_links"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "link_type",
            "url",
            name="uq_candidate_link",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
    )

    link_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CandidateExperience(Base):
    __tablename__ = "candidate_experiences"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    employment_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CandidateProject(Base):
    __tablename__ = "candidate_projects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    organization: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    problem: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    solution: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    architecture: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    outcome: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CandidateProjectLink(Base):
    __tablename__ = "candidate_project_links"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "link_type",
            "url",
            name="uq_candidate_project_link",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_projects.id"),
        nullable=False,
    )

    link_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    canonical_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    normalized_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id"),
        nullable=False,
    )

    alias: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    normalized_alias: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "skill_id",
            name="uq_candidate_skill",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id"),
        nullable=False,
    )

    proficiency_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    experience_months: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    last_used_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )


class CandidateExperienceSkill(Base):
    __tablename__ = "candidate_experience_skills"

    __table_args__ = (
        UniqueConstraint(
            "experience_id",
            "skill_id",
            name="uq_candidate_experience_skill",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    experience_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_experiences.id"),
        nullable=False,
    )

    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id"),
        nullable=False,
    )

    usage_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class CandidateProjectSkill(Base):
    __tablename__ = "candidate_project_skills"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "skill_id",
            name="uq_candidate_project_skill",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_projects.id"),
        nullable=False,
    )

    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id"),
        nullable=False,
    )

    usage_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    institution: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    degree: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    field_of_study: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    education_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    graduation_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    gpa: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )


class CandidateCourse(Base):
    __tablename__ = "candidate_courses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    education_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_education.id"),
        nullable=False,
    )

    course_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    course_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    grade: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class CandidateCertification(Base):
    __tablename__ = "candidate_certifications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    issuer: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    credential_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    issue_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    expiration_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    credential_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )


class CandidateAward(Base):
    __tablename__ = "candidate_awards"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    issuer: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    awarded_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )


class CandidatePublication(Base):
    __tablename__ = "candidate_publications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    publication_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    publisher: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    publication_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )


class CandidateActivity(Base):
    __tablename__ = "candidate_activities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    organization: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    activity_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )


class CandidateAchievement(Base):
    __tablename__ = "candidate_achievements"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    experience_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_experiences.id"),
        nullable=True,
    )

    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_projects.id"),
        nullable=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    metric_text: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )


class CandidatePreference(Base):
    __tablename__ = "candidate_preferences"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "category",
            "preference_key",
            name="uq_candidate_preference",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    preference_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    value_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    priority: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class CandidateApplicationFact(Base):
    __tablename__ = "candidate_application_facts"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "fact_key",
            name="uq_candidate_application_fact",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    fact_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    question_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="application_only",
        nullable=False,
    )


class CandidateStory(Base):
    __tablename__ = "candidate_stories"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    story_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    situation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    task: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )


class CandidateFact(Base):
    __tablename__ = "candidate_facts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    fact_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    value_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    value_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    visibility: Mapped[str] = mapped_column(
        String(50),
        default="internal",
        nullable=False,
    )

    is_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    valid_from: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    valid_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CandidateSourceDocument(Base):
    __tablename__ = "candidate_source_documents"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "content_hash",
            name="uq_candidate_source_document_hash",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    document_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    label: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    storage_uri: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    size_bytes: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    content_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class CandidateDocumentParse(Base):
    __tablename__ = "candidate_document_parses"

    __table_args__ = (
        UniqueConstraint(
            "source_document_id",
            "parser_name",
            "parser_version",
            name="uq_candidate_document_parse",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    source_document_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_source_documents.id"),
        nullable=False,
    )

    parser_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    parser_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    structured_payload: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    parsed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class CandidateExtractedFact(Base):
    __tablename__ = "candidate_extracted_facts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    source_document_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_source_documents.id"),
        nullable=False,
    )

    document_parse_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_document_parses.id"),
        nullable=True,
    )

    proposed_entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    proposed_field: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    value_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    value_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    review_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    resolved_entity_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    resolved_entity_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class CandidateProfileConflict(Base):
    __tablename__ = "candidate_profile_conflicts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    conflict_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    existing_entity_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    existing_entity_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    field_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    incoming_extracted_fact_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_extracted_facts.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="open",
        nullable=False,
    )

    resolution_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    resolution_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class CandidateEvidence(Base):
    __tablename__ = "candidate_evidence"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    source_kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_source_documents.id"),
        nullable=True,
    )

    extracted_fact_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_extracted_facts.id"),
        nullable=True,
    )

    target_entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target_entity_id: Mapped[int] = mapped_column(
        nullable=False,
    )

    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    locator_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class CandidateTag(Base):
    __tablename__ = "candidate_tags"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "name",
            name="uq_candidate_tag",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


class CandidateEntityTag(Base):
    __tablename__ = "candidate_entity_tags"

    __table_args__ = (
        UniqueConstraint(
            "tag_id",
            "entity_type",
            "entity_id",
            name="uq_candidate_entity_tag",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    tag_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_tags.id"),
        nullable=False,
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entity_id: Mapped[int] = mapped_column(
        nullable=False,
    )


class CandidateEntityRelation(Base):
    __tablename__ = "candidate_entity_relations"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "from_entity_type",
            "from_entity_id",
            "relation_type",
            "to_entity_type",
            "to_entity_id",
            name="uq_candidate_entity_relation",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    from_entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    from_entity_id: Mapped[int] = mapped_column(
        nullable=False,
    )

    relation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    to_entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    to_entity_id: Mapped[int] = mapped_column(
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )


class CandidateProfileVersion(Base):
    __tablename__ = "candidate_profile_versions"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "version_number",
            name="uq_candidate_profile_version",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    snapshot: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class CandidateAuditLog(Base):
    __tablename__ = "candidate_audit_log"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entity_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    actor_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    changes_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    source_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidate_source_documents.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )