# FastAPI to Flask Migration Guide

This document outlines the key differences and migration notes from FastAPI to Flask MVC architecture.

## Architecture Changes

### FastAPI → Flask MVC

**FastAPI Structure:**
```
- routers/          → Controllers (route handlers)
- models/           → Models (SQLAlchemy models)
- schemas/          → Views (response formatters)
- services/         → Services (business logic)
- dependencies.py   → Utils/auth.py (authentication)
```

**Flask MVC Structure:**
```
- controllers/      → Route handlers (MVC Controllers)
- models/           → Database models (MVC Models)
- views/            → Response formatters (MVC Views)
- services/         → Business logic services
- utils/            → Utilities and helpers
```

## Key Differences

### 1. Route Definitions

**FastAPI:**
```python
@router.post("/register")
async def register(user: UserCreate):
    ...
```

**Flask:**
```python
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    ...
```

### 2. Dependency Injection

**FastAPI:**
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    ...
```

**Flask:**
```python
@jwt_required()
def get_current_user_info():
    user = get_current_user()  # From utils/auth.py
    ...
```

### 3. Request Validation

**FastAPI:**
- Automatic validation via Pydantic models

**Flask:**
- Manual validation in controllers using validators.py

### 4. Response Formatting

**FastAPI:**
```python
return user.to_dict()
```

**Flask:**
```python
return success_response(user.to_dict(), status_code=200)
```

### 5. Error Handling

**FastAPI:**
```python
raise HTTPException(status_code=404, detail="Not found")
```

**Flask:**
```python
return error_response("Not Found", "Resource not found", "module", True, status_code=404)
```

### 6. File Uploads

**FastAPI:**
```python
file: UploadFile = File(...)
```

**Flask:**
```python
file = request.files['file']
```

### 7. Background Tasks

**FastAPI:**
```python
background_tasks.add_task(process_extraction, doc_id)
```

**Flask:**
```python
from threading import Thread
thread = Thread(target=process_extraction, args=(doc_id,))
thread.start()
```

## Database Models

Models remain largely the same, but:
- Use Flask-SQLAlchemy's `db.Model` instead of SQLAlchemy Base
- Use `db.Column` instead of direct Column import
- Serialization via `.to_dict()` methods

## Authentication

- JWT tokens work similarly
- Flask-JWT-Extended replaces python-jose
- Token creation and verification in `utils/auth.py`

## API Compatibility

All endpoints maintain the same:
- URL paths
- Request/response formats
- Status codes
- Error formats

## Environment Variables

Same environment variables are used:
- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `SUPABASE_*`
- `GEMINI_API_KEY`

## Running the Application

**FastAPI:**
```bash
uvicorn main:app --reload
```

**Flask:**
```bash
python run.py
# or
flask run
```

## Testing

Endpoints can be tested with the same tools:
- cURL
- Postman
- Thunder Client
- Any HTTP client

The API contract remains identical, so frontend code should work without changes.

