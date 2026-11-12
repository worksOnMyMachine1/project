from typing import Any, List, Optional

from sqlalchemy import inspect, text, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from domain import Asset
from exceptions import AssetNotFoundError, DuplicateAssetError
from models import AssetModel, AssetTagModel, db


class AssetRepository:
    def create_tables(self) -> None:
        db.create_all()

    def create(self, asset: Asset) -> Asset:
        asset_row = AssetModel()

        asset_row.name = asset.name
        asset_row.asset_type = asset.asset_type
        asset_row.description = asset.description
        asset_row.created_by = asset.created_by
        asset_row.updated_by = asset.updated_by
        asset_row.status = "Active"

        for tag in self._unique_tags(asset.tags):
            tag_row = AssetTagModel()
            tag_row.tag = tag
            tag_row.created_by = asset.created_by
            tag_row.updated_by = asset.updated_by
            tag_row.status = "Active"

            asset_row.tags.append(tag_row)

        db.session.add(asset_row)
        self._commit()

        return self._to_domain(asset_row)

    def get_by_id(self, asset_id: int) -> Asset:
        return self._to_domain(self._get_active_model(asset_id))

    def list(
        self,
        asset_type: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Asset]:
        statement = db.select(AssetModel).where(AssetModel.status == "Active")
        if asset_type is not None:
            statement = statement.where(AssetModel.asset_type.ilike(asset_type))
        if tag is not None:
            tag_exists = db.select(AssetTagModel.id).where(
                AssetTagModel.asset_id == AssetModel.id,
                AssetTagModel.status == "Active",
                func.lower(AssetTagModel.tag) == tag.lower(),
            ).exists()
            statement = statement.where(tag_exists)
        statement = statement.order_by(AssetModel.id)
        rows = db.session.execute(statement).scalars().all()
        return [self._to_domain(row) for row in rows]

    def update(self, asset_id: int, changes: dict[str, Any]) -> Asset:
        asset_row = self._get_active_model(asset_id)
        if "name" in changes:
            asset_row.name = changes["name"]
        if "asset_type" in changes:
            asset_row.asset_type = changes["asset_type"]
        if "description" in changes:
            asset_row.description = changes["description"]
        asset_row.updated_by = changes.get("updated_by") or "system"
        self._commit()
        return self._to_domain(asset_row)

    def add_tags(
        self,
        asset_id: int,
        tags: List[str],
        updated_by: str,
    ) -> tuple[Asset, bool]:
        asset_row = self._get_active_model(asset_id)
        existing_rows = db.session.execute(
            db.select(AssetTagModel).where(AssetTagModel.asset_id == asset_id)
        ).scalars().all()
        existing_by_name = {row.tag.casefold(): row for row in existing_rows}
        added = False

        for tag in self._unique_tags(tags):
            existing_row = existing_by_name.get(tag.casefold())
            if existing_row is not None:
                if existing_row.status != "Active":
                    existing_row.status = "Active"
                    existing_row.updated_by = updated_by
                    added = True
                continue

            tag_row = AssetTagModel()

            tag_row.asset_id = asset_id
            tag_row.tag = tag
            tag_row.created_by = updated_by
            tag_row.updated_by = updated_by
            tag_row.status = "Active"
            db.session.add(tag_row)
            existing_by_name[tag.casefold()] = tag_row
            added = True

        asset_row.updated_by = updated_by
        self._commit()
        return self._to_domain(asset_row), added

    def deactivate(self, asset_id: int) -> None:
        asset_row = self._get_active_model(asset_id)
        asset_row.status = "Inactive"
        asset_row.updated_by = "system"
        self._commit()


    def _get_active_model(self, asset_id: int) -> AssetModel:
        asset_row = db.session.get(AssetModel, asset_id)
        if asset_row is None or asset_row.status != "Active":
            raise AssetNotFoundError("Asset not found")
        return asset_row

    def _to_domain(self, asset_row: AssetModel) -> Asset:
        return Asset.from_dict(
            {
                "id": asset_row.id,
                "name": asset_row.name,
                "type": asset_row.asset_type,
                "description": asset_row.description,
                "tags": [
                    tag.tag for tag in asset_row.tags if tag.status == "Active"
                ],
                "createdAt": asset_row.created_at,
                "updatedAt": asset_row.updated_at,
                "createdBy": asset_row.created_by,
                "updatedBy": asset_row.updated_by,
                "status": asset_row.status,
            }
        )

    def _commit(self) -> None:
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise DuplicateAssetError("A duplicate record already exists") from error
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def _unique_tags(tags: List[str]) -> List[str]:
        unique: List[str] = []
        seen: set[str] = set()
        for tag in tags:
            clean_tag = tag.strip()
            key = clean_tag.casefold()
            if clean_tag and key not in seen:
                unique.append(clean_tag)
                seen.add(key)
        return unique
