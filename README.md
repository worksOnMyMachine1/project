
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
  |__ weather_client/    # for working with custom decorators around weather api 
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

### Testing

Tests are written using pythons `pytest` library, having coverage over 90%.
Install the `pytest` and other testing libraries using `pip install -r requirements.txt`.

Run the test suite and coverage thru `pytest --cov`.

i.e.

```
 pytest --cov
======================= test session starts =======================
platform linux -- Python 3.13.5, pytest-9.2.0, pluggy-1.7.0
rootdir: /home/srvk/prj/project
configfile: pytest.ini
testpaths: tests
plugins: cov-7.1.0
collected 37 items                                                

tests/test_routes.py .....................................  [100%]

========================= tests coverage ==========================
_________ coverage: platform linux, python 3.13.5-final-0 _________

Name                   Stmts   Miss  Cover
------------------------------------------
app.py                    35      2    94%
domain.py                 34      4    88%
exceptions.py              3      0   100%
models.py                 33      0   100%
repository.py            107      9    92%
routes.py                 39      0   100%
schemas.py                43      3    93%
tests/conftest.py         25      1    96%
tests/test_routes.py     105      0   100%
------------------------------------------
TOTAL                    424     19    96%
======================= 37 passed in 0.56s ========================

```