from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column("type", db.String(100), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column("createdAt", db.DateTime, default=datetime.utcnow)
    updated_at = db.Column("updatedAt", db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = db.Column("createdBy", db.String(100), default="system")
    updated_by = db.Column("updatedBy", db.String(100), default="system")
    status = db.Column(db.String(20), default="Active", nullable=False)

    tags = db.relationship("AssetTag", backref="asset", cascade="all, delete-orphan")


class AssetTag(db.Model):
    __tablename__ = "asset_tags"

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False)
    tag = db.Column(db.String(100), nullable=False)

    created_at = db.Column("createdAt", db.DateTime, default=datetime.utcnow)
    updated_at = db.Column("updatedAt", db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = db.Column("createdBy", db.String(100), default="system")
    updated_by = db.Column("updatedBy", db.String(100), default="system")
    status = db.Column(db.String(20), default="Active", nullable=False)