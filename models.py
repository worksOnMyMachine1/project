from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column("type", db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.JSON, nullable=False, default=list)

    created_at = db.Column("createdAt", db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        "updatedAt",
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    created_by = db.Column("createdBy", db.String(100), default="system")
    updated_by = db.Column("updatedBy", db.String(100), default="system")
    status = db.Column(db.String(20), default="Active", nullable=False)