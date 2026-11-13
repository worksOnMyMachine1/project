
## Project structure

```text

  ├── app.py                  # Creates the Flask app and registers the Blueprint
  ├── models.py               # SQLAlchemy AssetModel and AssetTagModel tables
  ├── schemas.py              # Pydantic request and query-string validation
  ├── domain.py               # Asset dataclass and its from_dict()/to_dict() methods
  ├── repository.py           # All database queries, writes, commits and rollbacks
  ├── exceptions.py           # Expected asset-related exceptions
  ├── routes.py               # Blueprint endpoints
  └── asset_register_postman_collection.json
  ├── requirements.txt
  └── README.md
```

`AssetModel` and `AssetTagModel` are the SQLAlchemy database models. `Asset` in `domain.py` is a separate dataclass used by the application and repository. This avoids a name clash while keeping the requested `Asset` dataclass.

## Setup

Use Python 3.10 or newer.

### 1. Create and activate a virtual environment

**Windows (Command Prompt):**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the database

In `.env`:

```env
DATABASE_URL=sqlite:///assets.db
```


### 4. Run the API

From the project root:

```bash
python -m app.py
```

The API runs at `http://127.0.0.1:5000` by default.


## API endpoints

The request and response formats remain compatible with the Week 1 Postman collection.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/assets` | Create an asset, optionally with tags |
| GET | `/assets` | List active assets |
| GET | `/assets?type=Electronics` | Filter active assets by type |
| GET | `/assets?tag=office` | Filter active assets by tag |
| GET | `/assets/<id>` | Get one active asset |
| PUT | `/assets/<id>` | Update name, type, or description |
| POST | `/assets/<id>/tags` | Add tags without duplicating existing tags |
| DELETE | `/assets/<id>` | Deactivate an asset (soft delete) |


### Create asset example

```http
POST /assets
Content-Type: application/json
```

```json
{
  "name": "Dell Laptop",
  "type": "Electronics",
  "description": "Office laptop",
  "tags": ["office", "computer"],
  "createdBy": "admin"
}
```

### Update asset example

```http
PUT /assets/1
Content-Type: application/json
```

```json
{
  "name": "Dell Latitude Laptop",
  "updatedBy": "admin"
}
```

### Add tags example

```http
POST /assets/1/tags
Content-Type: application/json
```

```json
{
  "tags": ["finance", "assigned"],
  "updatedBy": "admin"
}
```

