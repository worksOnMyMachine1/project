import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from models import db, Asset

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def asset_to_dict(asset):
    return {
        "id": asset.id,
        "name": asset.name,
        "type": asset.asset_type,
        "description": asset.description,
        "tags": asset.tags,
        "createdAt": asset.created_at.isoformat(),
        "updatedAt": asset.updated_at.isoformat(),
        "createdBy": asset.created_by,
        "updatedBy": asset.updated_by,
        "status": asset.status
    }


def clean_tags(tags):
    if not isinstance(tags, list):
        return None

    if not all(isinstance(tag, str) and tag.strip() for tag in tags):
        return None

    return list(dict.fromkeys(tag.strip() for tag in tags))


@app.route("/assets", methods=["POST"])
def create_asset():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON is required"}), 400

    if not data.get("name") or not isinstance(data["name"], str) or not data["name"].strip():
        return jsonify({"error": "Name is required"}), 400

    if not data.get("type") or not isinstance(data["type"], str) or not data["type"].strip():
        return jsonify({"error": "Type is required"}), 400

    description = data.get("description")
    if description is not None and not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    tags = clean_tags(data.get("tags", []))
    if tags is None:
        return jsonify({"error": "Tags must be a list of strings"}), 400

    created_by = data.get("createdBy", "system")
    updated_by = data.get("updatedBy", created_by)

    if not isinstance(created_by, str) or not created_by.strip():
        return jsonify({"error": "Invalid createdBy"}), 400

    if not isinstance(updated_by, str) or not updated_by.strip():
        return jsonify({"error": "Invalid updatedBy"}), 400

    asset = Asset(
        name=data["name"].strip(),
        asset_type=data["type"].strip(),
        description=description,
        tags=tags,
        created_by=created_by.strip(),
        updated_by=updated_by.strip()
    )

    db.session.add(asset)
    db.session.commit()

    return jsonify(asset_to_dict(asset)), 201


@app.route("/assets", methods=["GET"])
def get_assets():
    type_filter = request.args.get("type")
    tag_filter = request.args.get("tag")

    if type_filter is not None and not type_filter.strip():
        return jsonify({"error": "Type cannot be empty"}), 400

    if tag_filter is not None and not tag_filter.strip():
        return jsonify({"error": "Tag cannot be empty"}), 400

    assets = Asset.query.filter_by(status="Active").all()

    if type_filter:
        assets = [
            asset for asset in assets
            if asset.asset_type.lower() == type_filter.strip().lower()
        ]

    if tag_filter:
        assets = [
            asset for asset in assets
            if any(tag.lower() == tag_filter.strip().lower() for tag in asset.tags)
        ]

    return jsonify([asset_to_dict(asset) for asset in assets]), 200


@app.route("/assets/<int:asset_id>", methods=["GET"])
def get_asset(asset_id):
    asset = Asset.query.filter_by(
        id=asset_id,
        status="Active"
    ).first()

    if asset is None:
        return jsonify({"error": "Asset not found"}), 404

    return jsonify(asset_to_dict(asset)), 200


@app.route("/assets/<int:asset_id>", methods=["PUT"])
def update_asset(asset_id):
    asset = Asset.query.filter_by(
        id=asset_id,
        status="Active"
    ).first()

    if asset is None:
        return jsonify({"error": "Asset not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Valid JSON is required"}), 400

    if not any(key in data for key in ["name", "type", "description"]):
        return jsonify({"error": "Provide at least one field to update"}), 400

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return jsonify({"error": "Invalid name"}), 400
        asset.name = data["name"].strip()

    if "type" in data:
        if not isinstance(data["type"], str) or not data["type"].strip():
            return jsonify({"error": "Invalid type"}), 400
        asset.asset_type = data["type"].strip()

    if "description" in data:
        if data["description"] is not None and not isinstance(data["description"], str):
            return jsonify({"error": "Invalid description"}), 400
        asset.description = data["description"]

    updated_by = data.get("updatedBy", "system")

    if not isinstance(updated_by, str) or not updated_by.strip():
        return jsonify({"error": "Invalid updatedBy"}), 400

    asset.updated_by = updated_by.strip()

    db.session.commit()

    return jsonify(asset_to_dict(asset)), 200


@app.route("/assets/<int:asset_id>/tags", methods=["POST"])
def add_tags(asset_id):
    asset = Asset.query.filter_by(
        id=asset_id,
        status="Active"
    ).first()

    if asset is None:
        return jsonify({"error": "Asset not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON is required"}), 400

    tags = clean_tags(data.get("tags"))

    if not tags:
        return jsonify({"error": "Provide a non-empty list of tags"}), 400

    updated_by = data.get("updatedBy", "system")

    if not isinstance(updated_by, str) or not updated_by.strip():
        return jsonify({"error": "Invalid updatedBy"}), 400

    current_tags = list(asset.tags or [])
    added_tags = []

    for tag in tags:
        if tag.lower() not in [item.lower() for item in current_tags]:
            current_tags.append(tag)
            added_tags.append(tag)

    asset.tags = current_tags
    asset.updated_by = updated_by.strip()

    db.session.commit()

    status_code = 201 if added_tags else 200

    return jsonify(asset_to_dict(asset)), status_code


@app.route("/assets/<int:asset_id>", methods=["DELETE"])
def delete_asset(asset_id):
    asset = Asset.query.filter_by(
        id=asset_id,
        status="Active"
    ).first()

    if asset is None:
        return jsonify({"error": "Asset not found"}), 404

    asset.status = "Inactive"
    asset.updated_by = "system"

    db.session.commit()

    return jsonify({"message": "Asset deactivated successfully"}), 200


@app.errorhandler(500)
def server_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run()