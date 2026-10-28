## Project structure

```text
asset_register/
├── main.py
├── models.py
├── .env
├── requirements.txt
└── instance/          # Created by Flask if it does not exist
    └── assets.db      # Created when the app starts
```

## Setup

### 1. Create and activate a virtual environment

From the project directory, run:

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

Create a `.env` file in the same directory as `main.py` and add:

```env
DATABASE_URL=sqlite:///assets.db
```

With Flask-SQLAlchemy, this relative SQLite path stores the database at `instance/assets.db`. The application creates the tables when it starts.

### 4. Start the application

```bash
python main.py
```

The API should be available at:

```text
http://127.0.0.1:5000
```

## API endpoints

### 1. Create an asset

**Request**

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

Example response: `201 Created`

```json
{
  "id": 1,
  "name": "Dell Laptop",
  "type": "Electronics",
  "description": "Office laptop",
  "tags": ["office", "computer"],
  "createdAt": "2026-10-28T10:30:00",
  "updatedAt": "2026-10-28T10:30:00",
  "createdBy": "admin",
  "updatedBy": "admin",
  "status": "Active"
}
```

The returned ID depends on the database. `createdBy` and `updatedBy` default to `system` if omitted.

### 2. List active assets

**Request**

```http
GET /assets
```

Returns a JSON array of active assets. Inactive assets are not included.

### 3. Filter assets by type

**Request**

```http
GET /assets?type=Electronics
```

Returns active assets whose type matches `Electronics`. The type filter is case-insensitive.

### 4. Filter assets by tag

**Request**

```http
GET /assets?tag=office
```

Returns active assets containing the `office` tag. The tag filter is case-insensitive.

You can combine both filters:

```http
GET /assets?type=Electronics&tag=office
```

### 5. Get one asset

**Request**

```http
GET /assets/1
```

Returns the active asset with ID `1`.

Example response: `200 OK`

```json
{
  "id": 1,
  "name": "Dell Laptop",
  "type": "Electronics",
  "description": "Office laptop",
  "tags": ["office", "computer"],
  "createdAt": "2026-10-28T10:30:00",
  "updatedAt": "2026-10-28T10:30:00",
  "createdBy": "admin",
  "updatedBy": "admin",
  "status": "Active"
}
```

If the ID does not exist or the asset is inactive, the API returns `404 Not Found`.

### 6. Update an asset

**Request**

```http
PUT /assets/1
Content-Type: application/json
```

Send only the fields you want to change:

```json
{
  "name": "Dell Latitude Laptop",
  "description": "Laptop assigned to the finance team",
  "updatedBy": "admin"
}
```

Example response: `200 OK`, with the updated asset in the response body.

Allowed fields are `name`, `type`, `description`, and `updatedBy`. At least one asset field (`name`, `type`, or `description`) must be provided.

### 7. Add tags to an asset

**Request**

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

The response contains the asset and its updated tag list. Existing tags are not added again (tag comparisons are case-insensitive). The implementation returns `201 Created` when new tags are added and `200 OK` when all supplied tags already exist.

### 8. Deactivate an asset

**Request**

```http
DELETE /assets/1
```

Example response: `200 OK`

```json
{
  "message": "Asset deactivated successfully"
}
```

This changes the asset's `status` to `Inactive`; it does not delete the row from SQLite. Inactive assets are excluded from list, get, update, tag, and delete operations. Trying to access an inactive asset returns `404 Not Found`.
