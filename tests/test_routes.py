from typing import Any

import pytest
from flask.testing import FlaskClient


import routes
from domain import Asset
from exceptions import DuplicateAssetError


BASE_ASSET: dict[str, Any] = {
    "name": "Dell Laptop",
    "type": "Electronics",
    "description": "Office laptop",
    "tags": ["office", "computer"],
    "createdBy": "admin",
}


def create_asset(client: FlaskClient, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    response = client.post("/assets", json=payload or BASE_ASSET)
    assert response.status_code == 201
    return response.get_json()


def test_create_asset_success(client: FlaskClient) -> None:
    response = client.post("/assets", json=BASE_ASSET)

    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] is not None
    assert data["name"] == "Dell Laptop"
    assert data["type"] == "Electronics"
    assert data["tags"] == ["computer", "office"]
    assert data["createdBy"] == "admin"
    assert data["updatedBy"] == "admin"
    assert data["status"] == "Active"



def test_list_assets_and_filter_by_type_and_tag(client: FlaskClient) -> None:
    create_asset(client)
    create_asset(
        client,
        {
            "name": "Office Chair",
            "type": "Furniture",
            "tags": ["office"],
        },
    )

    all_assets = client.get("/assets")
    by_type = client.get("/assets?type=electronics")
    by_tag = client.get("/assets?tag=OFFICE")
    by_both = client.get("/assets?type=Electronics&tag=office")

    assert all_assets.status_code == 200
    assert len(all_assets.get_json()) == 2
    assert [item["name"] for item in by_type.get_json()] == ["Dell Laptop"]
    assert len(by_tag.get_json()) == 2
    assert [item["name"] for item in by_both.get_json()] == ["Dell Laptop"]


def test_get_one_asset_success(client: FlaskClient) -> None:
    created = create_asset(client)

    response = client.get(f"/assets/{created['id']}")

    assert response.status_code == 200
    assert response.get_json()["id"] == created["id"]
    assert response.get_json()["tags"] == ["computer", "office"]


def test_update_asset_success(client: FlaskClient) -> None:
    created = create_asset(client)

    response = client.put(
        f"/assets/{created['id']}",
        json={
            "name": "Dell Latitude",
            "type": "Business Equipment",
            "description": "Assigned to finance",
            "updatedBy": "manager",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Dell Latitude"
    assert data["description"] == "Assigned to finance"
    assert data["updatedBy"] == "manager"
    assert data["type"] == "Business Equipment"


def test_add_tags_success_and_duplicate_tags_are_ignored(client: FlaskClient) -> None:
    created = create_asset(client)

    added = client.post(
        f"/assets/{created['id']}/tags",
        json={"tags": ["finance", "assigned"], "updatedBy": "admin"},
    )
    repeated = client.post(
        f"/assets/{created['id']}/tags",
        json={"tags": ["FINANCE", "assigned"], "updatedBy": "admin"},
    )

    assert added.status_code == 201
    assert set(added.get_json()["tags"]) == {
        "office", "computer", "finance", "assigned"
    }
    assert repeated.status_code == 200
    assert len(repeated.get_json()["tags"]) == 4


def test_deactivate_asset_and_never_return_it_again(client: FlaskClient) -> None:
    created = create_asset(client)

    deleted = client.delete(f"/assets/{created['id']}")
    listed = client.get("/assets")
    filtered = client.get("/assets?tag=office")
    fetched = client.get(f"/assets/{created['id']}")

    assert deleted.status_code == 200
    assert deleted.get_json() == {"message": "Asset deactivated successfully"}
    assert listed.get_json() == []
    assert filtered.get_json() == []
    assert fetched.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"name": "Dell Laptop"},
        {"type": "Electronics"},
        {"name": " ", "type": "Electronics"},
        {"name": "Dell Laptop", "type": " "},
        {"name": "Dell Laptop", "type": "Electronics", "tags": "office"},
        {"name": "Dell Laptop", "type": "Electronics", "tags": [" "]},
        {"name": "Dell Laptop", "type": "Electronics", "description": 123},
    ],
)
def test_create_asset_bad_input_returns_400(
    client: FlaskClient, payload: dict[str, Any] | None
) -> None:
    response = client.post("/assets", json=payload)
    assert response.status_code == 400


def test_create_asset_malformed_json_returns_400(client: FlaskClient) -> None:
    response = client.post(
        "/assets", data="{not valid json", content_type="application/json"
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"name": ""},
        {"type": None},
        {"description": 123},
        {"unknown": "value"},
    ],
)
def test_update_asset_bad_input_returns_400(
    client: FlaskClient, payload: dict[str, Any] | None
) -> None:
    response = client.put("/assets/1", json=payload)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"tags": []},
        {"tags": "office"},
        {"tags": [" "]},
        {"tags": [123]},
    ],
)
def test_add_tags_bad_input_returns_400(
    client: FlaskClient, payload: dict[str, Any] | None
) -> None:
    response = client.post("/assets/1/tags", json=payload)
    assert response.status_code == 400


@pytest.mark.parametrize("query", ["?type=", "?tag=", "?type=%20%20"])
def test_list_assets_bad_filters_return_400(
    client: FlaskClient, query: str
) -> None:
    response = client.get(f"/assets{query}")
    assert response.status_code == 400


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("GET", "/assets/999", {}),
        ("PUT", "/assets/999", {"json": {"name": "Updated"}}),
        ("POST", "/assets/999/tags", {"json": {"tags": ["office"]}}),
        ("DELETE", "/assets/999", {}),
    ],
)
def test_missing_asset_returns_404(
    client: FlaskClient,
    method: str,
    path: str,
    kwargs: dict[str, Any],
) -> None:
    response = client.open(path, method=method, **kwargs)
    assert response.status_code == 404


def test_duplicate_exception_is_returned_as_409(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_duplicate(asset: Asset) -> Asset:
        raise DuplicateAssetError("A duplicate record already exists")

    monkeypatch.setattr(routes.repository, "create", raise_duplicate)

    response = client.post("/assets", json=BASE_ASSET)

    assert response.status_code == 409
    assert response.get_json()["error"] == "A duplicate record already exists"


def test_unexpected_error_returns_500(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_error(asset_id: int) -> Asset:
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(routes.repository, "get_by_id", raise_error)

    response = client.get("/assets/1")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error"}
