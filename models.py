from __future__ import annotations

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


db = SQLAlchemy()


class AssetModel(db.Model):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_type: Mapped[str] = mapped_column("type", String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        "createdAt", DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
    created_by: Mapped[str] = mapped_column(
        "createdBy", String(100), default="system", nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        "updatedBy", String(100), default="system", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="Active", nullable=False
    )

    tags: Mapped[list[AssetTagModel]] = relationship(
        "AssetTagModel",
        backref="asset",
        cascade="all, delete-orphan"
    )


class AssetTagModel(db.Model):
    __tablename__ = "asset_tags"
    __table_args__ = (
        UniqueConstraint("asset_id", "tag", name="uq_asset_tag"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"), nullable=False
    )
    tag: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        "createdAt", DateTime, default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
    created_by: Mapped[str] = mapped_column(
        "createdBy", String(100), default="system", nullable=False
    )
    updated_by: Mapped[str] = mapped_column(
        "updatedBy", String(100), default="system", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="Active", nullable=False
    )
