from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
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
        primary_key=True
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
        primary_key=True
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