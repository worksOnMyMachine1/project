from typing import Any

from flask import Blueprint, jsonify, request
from werkzeug.wrappers import Response

# below functions are yet to be implemented 
from domain import Asset
from repository import AssetRepository
from schemas import (
    AssetCreate,
    AssetListFilters,
    AssetTagsCreate,
    AssetUpdate,
)


assets_blueprint = Blueprint("assets", __name__)
repository = AssetRepository()


@assets_blueprint.route("/assets", methods=["POST"])
def create_asset() -> tuple[Response, int]:
    payload = AssetCreate.model_validate(request.get_json(silent=True))
    updated_by = payload.updated_by or payload.created_by
    asset = Asset(
        name=payload.name,
        asset_type=payload.asset_type,
        description=payload.description,
        tags=payload.tags,
        created_by=payload.created_by,
        updated_by=updated_by,
    )
    created_asset = repository.create(asset)
    return jsonify(created_asset.to_dict()), 201


@assets_blueprint.route("/assets", methods=["GET"])
def get_assets() -> tuple[Response, int]:
    filters = AssetListFilters.model_validate(request.args.to_dict())
    assets = repository.list(asset_type=filters.asset_type, tag=filters.tag)
    return jsonify([asset.to_dict() for asset in assets]), 200


@assets_blueprint.route("/assets/<int:asset_id>", methods=["GET"])
def get_asset(asset_id: int) -> tuple[Response, int]:
    asset = repository.get_by_id(asset_id)
    return jsonify(asset.to_dict()), 200


@assets_blueprint.route("/assets/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id: int) -> tuple[Response, int]:
    payload = AssetUpdate.model_validate(request.get_json(silent=True))
    changes: dict[str, Any] = payload.model_dump(exclude_unset=True)
    updated_asset = repository.update(asset_id, changes)
    return jsonify(updated_asset.to_dict()), 200


@assets_blueprint.route("/assets/<int:asset_id>/tags", methods=["POST"])
def add_tags(asset_id: int) -> tuple[Response, int]:
    payload = AssetTagsCreate.model_validate(request.get_json(silent=True))
    asset, added = repository.add_tags(
        asset_id,
        payload.tags,
        payload.updated_by,
    )
    return jsonify(asset.to_dict()), 201 if added else 200


@assets_blueprint.route("/assets/<int:asset_id>", methods=["DELETE"])
def delete_asset(asset_id: int) -> tuple[Response, int]:
    repository.deactivate(asset_id)
    return jsonify({"message": "Asset deactivated successfully"}), 200
