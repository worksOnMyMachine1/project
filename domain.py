from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Asset:
    name: str
    asset_type: str
    description: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str = "system"
    updated_by: str = "system"
    status: str = "Active"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Asset":
        asset_type = data.get("type", data.get("asset_type"))
        name = data.get("name")
        raw_tags = data.get("tags", [])

        if not isinstance(asset_type, str):
            raise ValueError("Asset type must be a string")

        if not isinstance(name, str):
            raise ValueError("Asset name must be a string")

        if not isinstance(raw_tags, list):
            raise ValueError("Tags must be a list")

        tags: list[str] = []

        for tag in raw_tags:
            if not isinstance(tag, str):
                raise ValueError("Every tag must be a string")
            tags.append(tag)

        return cls(
            id=data.get("id"),
            name=name,
            asset_type=asset_type,
            description=data.get("description"),
            tags=tags,
            created_at=data.get("createdAt", data.get("created_at")),
            updated_at=data.get("updatedAt", data.get("updated_at")),
            created_by=data.get("createdBy", data.get("created_by", "system")),
            updated_by=data.get("updatedBy", data.get("updated_by", "system")),
            status=data.get("status", "Active"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.asset_type,
            "description": self.description,
            "tags": self.tags,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "createdBy": self.created_by,
            "updatedBy": self.updated_by,
            "status": self.status,
        }
