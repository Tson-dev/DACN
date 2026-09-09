# IMPLEMENTATION PLAN - Target GPA Achievement Prediction System

**Version**: 1.0
**Date**: 2026-09-09
**Purpose**: Fill all documentation gaps and provide concrete implementation guidance

---

## PART 1: GAP RESOLUTION DECISIONS

### 1.1 Timezone Decision

**Decision**: `Asia/Ho_Chi_Minh` (UTC+7) for all date/time operations.

**Rationale**: Vietnamese project, Vietnamese users. All day boundaries, prediction dates, and lock schedules use this timezone.

**Implementation**: All `datetime.now()` calls use `datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))`. SQLite stores UTC dates; conversion happens at application layer.

---

### 1.2 Authentication Decision

**Decision**: Cookie-based session with server-side in-memory session store (Python dict).

**Rationale**: Simple for 2-user academic project. No external dependencies.

**Implementation**:
- Session ID: `secrets.token_hex(32)` (64-char hex string)
- Cookie name: `session_id`
- Cookie flags: `HttpOnly=True, SameSite="lax"` (not Secure for local dev)
- Session store: `dict` mapping `session_id -> {"user_id": int, "username": str, "role": str, "created_at": datetime}`
- Session expiry: 24 hours (end of day in `Asia/Ho_Chi_Minh`)
- Logout: Delete from dict, expire cookie
- Transport: Cookie automatically attached by browser

**Per-request auth check**: Load session from cookie, verify exists and not expired, verify user is ACTIVE (NOT locked).

---

### 1.3 Lock/Unlock Mechanism (BR-06) Decision

**Decision**: Simplified approach - no delayed lock for V1.

**Rationale**: The "lock effective next day" adds significant complexity (new column, scheduled task, timezone edge cases) with minimal value for an academic demo. For V1:
- Lock is immediate: status changes to `LOCKED` immediately
- Unlock is immediate: status changes to `ACTIVE` immediately
- Currently logged-in session is terminated on lock (per-request check)
- This satisfies BR-01 (one prediction per day) and BR-02 regardless

**Note**: If the requirement strictly demands delayed lock, we add `pending_status` and `effective_date` columns later.

---

### 1.4 Database Schema Decisions

**Primary keys**: `INTEGER PRIMARY KEY AUTOINCREMENT` (SQLite native)

**Role table**: Use SPEC schema (`role_id, name, desc`) over SDD schema for richer data.

**Indexes**:
```sql
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_role_id ON user(role_id);
CREATE INDEX idx_user_status ON user(status);
CREATE INDEX idx_student_profile_user_id ON student_profile(user_id);
CREATE INDEX idx_student_profile_student_code ON student_profile(student_code);
CREATE INDEX idx_prediction_history_user_id ON prediction_history(user_id);
CREATE INDEX idx_prediction_history_date ON prediction_history(prediction_date);
CREATE INDEX idx_prediction_history_user_date ON prediction_history(user_id, prediction_date);
```

**SQLite WAL mode**: Enable at startup for concurrent reads during writes.

---

### 1.5 ML Pipeline Decisions

**Feature Encoding**:
- `Gender`: Label encoding (`"Male"` = 0, `"Female"` = 1)
- `Major`: One-hot encoding (all majors from training dataset)
- Numeric features used as-is (no scaling needed for LightGBM)

**Feature Vector Order**:
```
[age, attendance_percentage, study_hours_per_day, sleep_hours_per_day,
 social_hours_per_week, previous_cgpa, gender_encoded, major_encoded_1, ..., major_encoded_N]
```

**LightGBM Hyperparameters**:
```python
LGBMRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=6,
    num_leaves=31,
    min_child_samples=20,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    device='cpu',
    verbose=-1
)
```

**Train/Test Split**: 80/20, `random_state=42`

**Pipeline Artifacts Saved as Single File**:
```
model_artifacts.pkl  # Contains:
    - model: trained LGBMRegressor
    - label_encoder_gender: LabelEncoder for Gender
    - onehot_encoder_major: OneHotEncoder for Major (sparse=False)
    - knn_features_scaler: StandardScaler for KNN features
    - knn_model: fitted NearestNeighbors
    - historical_data: numpy array of historical student features + outcomes
    - feature_columns: list of column names in order
```

**Model Loading**: Load at server startup into a global `MLService` instance. Raise exception if file missing.

---

### 1.6 KNN Similarity Decisions

**K Value**: `K=50` (will be tunable in config)

**Features for KNN**: Same features as LightGBM (excluding Final_CGPA):
```
[age, attendance_percentage, study_hours_per_day, sleep_hours_per_day,
 social_hours_per_week, previous_cgpa, gender, major...]
```

**Normalization**: `StandardScaler` (Z-score normalization)

**Historical Dataset**: Loaded from CSV into memory at startup. Stored as numpy array. KNN index built using `sklearn.neighbors.NearestNeighbors`.

---

### 1.7 Probability Calculation Decisions

**Formula** (as per SPEC):
```python
success_probability = (similar_students_with_gpa >= target_gpa) / total_similar_students * 100
```

**Edge Cases**:
- 0 similar students found: Return `50.0` (neutral probability) with `similar_student_count = 0`
- All similar students meet target: Return `100.0`
- None meet target: Return `0.0`

**Target GPA matching**: `final_cgpa >= target_gpa` (non-strict, inclusive)

---

### 1.8 Frontend Decision

**Technology**: HTML + CSS + Vanilla JavaScript (no framework)

**Rationale**: Academic project, 2 members, simplicity. No build tooling needed.

**Pages**:
| Page | URL | Auth Required | Role |
|------|-----|---------------|------|
| Login | `/login` | No | All |
| Dashboard (Profile + Predict) | `/dashboard` | Yes | STUDENT |
| History | `/history` | Yes | STUDENT |
| Admin Dashboard | `/admin` | Yes | ADMIN |
| Admin User Management | `/admin/users` | Yes | ADMIN |
| Admin Profile Management | `/admin/profiles` | Yes | ADMIN |
| Admin Create User | `/admin/users/create` | Yes | ADMIN |
| Admin Edit Profile | `/admin/profiles/{id}/edit` | Yes | ADMIN |

**Serving**: FastAPI serves static files from `/static/` and HTML pages via Jinja2 templates.

---

### 1.9 Docker Decision

**Architecture**: Single container (FastAPI + ML + SQLite + Static Frontend).

**Rationale**: Simplest for deployment. SDD diagram shows single container.

**Port**: 8000

**SQLite persistence**: Volume mount for `/app/data/` directory.

---

### 1.10 API Contract Decisions

**Standard Response Envelope**:
```json
{
  "success": true|false,
  "message": "...",
  "data": { ... }
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "Error description",
  "errors": [
    {"field": "target_gpa", "message": "Must be between 0 and 4.0"}
  ]
}
```

**HTTP Status Codes**:
| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created (user, profile) |
| 400 | Bad Request (business logic error) |
| 401 | Unauthorized (not logged in) |
| 403 | Forbidden (wrong role) |
| 404 | Not Found |
| 409 | Conflict (duplicate prediction today) |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

### 1.11 Student Profile Creation Decision

**Flow**:
1. Admin creates User with `POST /api/admin/users` (username, password, role)
2. For STUDENT role, system auto-creates empty `StudentProfile` with:
   - `student_code`: `"PENDING"` (placeholder, not NULL)
   - `full_name`: `"Not Set"` (placeholder, not NULL)
   - All numeric fields: `0.0`
3. Admin then updates profile via `PUT /api/admin/profiles/{id}` with full data

**Prediction guard**: If profile has `student_code == "PENDING"` or `previous_cgpa == 0`, reject prediction with message "Student Profile incomplete. Please ask Admin to update your profile."

---

### 1.12 Seed Data

**Initial Admin Account** (created at first startup):
```
username: admin
password: admin123
role: ADMIN
status: ACTIVE
```

**Roles**:
```
(1, "ADMIN", "System administrator")
(2, "STUDENT", "Student user")
```

---

### 1.13 Password Policy

**Decision**: Minimum 6 characters. No complexity requirements (academic project).

**Hashing**: `bcrypt` via `passlib[bcrypt]`

---

### 1.14 Gender/Major Enumeration

**Gender values**: `"Male"`, `"Female"` (matching dataset)

**Major values**: Read from training dataset CSV. Stored in model artifacts for consistent one-hot encoding.

---

### 1.15 Error Handling

**Global Exception Handler**: FastAPI `@app.exception_handler(Exception)` returns 500 with standardized error response.

**ML Inference Failure**: Catch exception, log, return 500 with "Prediction service temporarily unavailable."

---

### 1.16 Logging

**Framework**: Python `logging` module

**Level**: INFO for requests, WARNING for business errors, ERROR for exceptions

**Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

---

### 1.17 CORS

**Configuration**: Since frontend is served from same origin (FastAPI static files), CORS is NOT needed. All API and frontend requests come from the same host/port.

---

## PART 2: PROJECT STRUCTURE

```
D:\DACN\DACN\
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, startup, shutdown, middleware
│   ├── config.py                  # Settings, constants, timezone
│   ├── database.py                # SQLite connection, WAL mode, session factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User SQLAlchemy model
│   │   ├── role.py                # Role SQLAlchemy model
│   │   ├── student_profile.py     # StudentProfile SQLAlchemy model
│   │   └── prediction_history.py  # PredictionHistory SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                # LoginRequest, LoginResponse, etc.
│   │   ├── user.py                # UserCreate, UserResponse, UserListResponse
│   │   ├── profile.py             # ProfileResponse, ProfileUpdate
│   │   ├── prediction.py          # PredictionRequest, PredictionResponse
│   │   └── common.py              # StandardResponse, ErrorResponse
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                # POST /api/auth/login, /logout
│   │   ├── profile.py             # GET /api/profile/me
│   │   ├── prediction.py          # POST /api/predictions, GET /api/predictions/today
│   │   └── admin.py               # All /api/admin/* endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Session management, login, logout
│   │   ├── user_service.py        # CRUD users
│   │   ├── profile_service.py     # CRUD profiles
│   │   └── prediction_service.py  # Orchestrate prediction flow
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── ml_service.py          # Load model, predict, find similar, calc probability
│   │   └── train.py               # Training script (run once)
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth_middleware.py     # Session validation middleware
│   ├── seed.py                    # Seed roles + admin account
│   └── requirements.txt
├── data/
│   ├── students_dataset.csv       # Training dataset (~5000 records)
│   ├── model_artifacts.pkl        # Trained model + encoders + KNN
│   └── app.db                     # SQLite database (created at runtime)
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── api.js             # API client (fetch wrapper)
│   │       ├── auth.js            # Login/logout handling
│   │       ├── dashboard.js       # Profile display + prediction form
│   │       ├── history.js         # Prediction history display
│   │       └── admin.js           # Admin panel logic
│   └── templates/
│       ├── base.html              # Base layout (navbar, sidebar)
│       ├── login.html
│       ├── dashboard.html
│       ├── history.html
│       ├── admin/
│       │   ├── dashboard.html
│       │   ├── users.html
│       │   ├── create_user.html
│       │   ├── profiles.html
│       │   └── edit_profile.html
│       └── components/
│           ├── navbar.html
│           └── sidebar.html
├── Dockerfile
├── docker-compose.yml
├── train_model.py                 # Entry point for training
└── README.md
```

---

## PART 3: DETAILED API CONTRACT

### 3.1 Authentication APIs

#### POST /api/auth/login

**Request**:
```json
{
  "username": "string (required, min 1)",
  "password": "string (required, min 1)"
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user_id": 1,
    "username": "student01",
    "role": "STUDENT"
  }
}
```

**Set-Cookie**: `session_id=<token>; HttpOnly; SameSite=lax; Path=/`

**Error Responses**:
- 400: `{"success": false, "message": "Invalid username or password"}`
- 400: `{"success": false, "message": "Account is locked"}`

---

#### POST /api/auth/logout

**Request**: No body (uses session cookie)

**Success Response** (200):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Set-Cookie**: `session_id=; Max-Age=0; Path=/` (expires cookie)

**Error Responses**:
- 401: `{"success": false, "message": "Not authenticated"}`

---

### 3.2 Profile APIs

#### GET /api/profile/me

**Request**: No body (uses session cookie)

**Success Response** (200):
```json
{
  "success": true,
  "data": {
    "profile_id": 1,
    "student_code": "SE001",
    "full_name": "Nguyen Van A",
    "gender": "Male",
    "age": 21,
    "major": "Software Engineering",
    "attendance_percentage": 90.0,
    "study_hours_per_day": 4.0,
    "sleep_hours_per_day": 7.0,
    "social_hours_per_week": 5.0,
    "previous_cgpa": 3.2
  }
}
```

**Error Responses**:
- 401: `{"success": false, "message": "Not authenticated"}`
- 404: `{"success": false, "message": "Student profile not found"}`

---

### 3.3 Prediction APIs

#### POST /api/predictions

**Request**:
```json
{
  "target_gpa": 3.5
}
```

**Validation**: `0 < target_gpa <= 4.0`

**Success Response** (200):
```json
{
  "success": true,
  "data": {
    "predicted_gpa": 3.28,
    "target_gpa": 3.50,
    "success_probability": 74.2,
    "similar_student_count": 120
  }
}
```

**Error Responses**:
- 400: `{"success": false, "message": "Student profile is incomplete. Please ask admin to update your profile."}`
- 400: `{"success": false, "message": "Target GPA must be between 0 (exclusive) and 4.0 (inclusive)"}`
- 409: `{"success": false, "message": "You have already made a prediction today."}`
- 500: `{"success": false, "message": "Prediction service temporarily unavailable"}`

---

#### GET /api/predictions/today

**Request**: No body (uses session cookie)

**Success Response** (200):
```json
{
  "success": true,
  "data": {
    "predicted_gpa": 3.28,
    "target_gpa": 3.50,
    "success_probability": 74.2,
    "similar_student_count": 120,
    "prediction_date": "2026-09-09"
  }
}
```

**No Prediction Today** (200):
```json
{
  "success": true,
  "data": null
}
```

**Error Responses**:
- 401: `{"success": false, "message": "Not authenticated"}`

---

### 3.4 Admin APIs

#### POST /api/admin/users

**Request**:
```json
{
  "username": "student02",
  "password": "123456",
  "role": "STUDENT"
}
```

**Validation**:
- `username`: min 3 chars, unique
- `password`: min 6 chars
- `role`: must be "ADMIN" or "STUDENT"

**Success Response** (201):
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user_id": 3,
    "username": "student02",
    "role": "STUDENT"
  }
}
```

**Error Responses**:
- 400: `{"success": false, "message": "Username already exists"}`
- 400: `{"success": false, "message": "Validation failed", "errors": [...]}`

---

#### GET /api/admin/users

**Request**: No body

**Success Response** (200):
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "user_id": 1,
        "username": "admin",
        "role": "ADMIN",
        "status": "ACTIVE",
        "created_at": "2026-09-09T08:00:00"
      },
      {
        "user_id": 2,
        "username": "student01",
        "role": "STUDENT",
        "status": "ACTIVE",
        "created_at": "2026-09-09T08:00:00"
      }
    ]
  }
}
```

---

#### PUT /api/admin/users/{user_id}/lock

**Request**: No body

**Success Response** (200):
```json
{
  "success": true,
  "message": "User locked successfully"
}
```

**Error Responses**:
- 404: `{"success": false, "message": "User not found"}`
- 400: `{"success": false, "message": "User is already locked"}`

---

#### PUT /api/admin/users/{user_id}/unlock

**Request**: No body

**Success Response** (200):
```json
{
  "success": true,
  "message": "User unlocked successfully"
}
```

**Error Responses**:
- 404: `{"success": false, "message": "User not found"}`
- 400: `{"success": false, "message": "User is already active"}`

---

#### GET /api/admin/profiles

**Request**: No body

**Success Response** (200):
```json
{
  "success": true,
  "data": {
    "profiles": [
      {
        "profile_id": 1,
        "user_id": 2,
        "student_code": "SE001",
        "full_name": "Nguyen Van A",
        "major": "Software Engineering",
        "previous_cgpa": 3.2
      }
    ]
  }
}
```

---

#### PUT /api/admin/profiles/{profile_id}

**Request**:
```json
{
  "student_code": "SE002",
  "full_name": "Tran Thi B",
  "gender": "Female",
  "age": 20,
  "major": "Computer Science",
  "attendance_percentage": 85.0,
  "study_hours_per_day": 3.5,
  "sleep_hours_per_day": 6.5,
  "social_hours_per_week": 8.0,
  "previous_cgpa": 3.0
}
```

**Validation**:
- `student_code`: not empty, unique
- `full_name`: not empty
- `age`: > 0
- `attendance_percentage`: 0-100
- `previous_cgpa`: 0-4.0
- Other hours fields: >= 0

**Success Response** (200):
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

**Error Responses**:
- 404: `{"success": false, "message": "Profile not found"}`
- 400: `{"success": false, "message": "Student code already exists"}`

---

## PART 4: DATABASE DDL

```sql
-- Enable WAL mode
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;

-- Role table
CREATE TABLE IF NOT EXISTS role (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    desc VARCHAR(255)
);

-- User table
CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES role(role_id)
);

-- StudentProfile table
CREATE TABLE IF NOT EXISTS student_profile (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    student_code VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20),
    age INTEGER,
    major VARCHAR(100),
    attendance_percentage REAL,
    study_hours_per_day REAL,
    sleep_hours_per_day REAL,
    social_hours_per_week REAL,
    previous_cgpa REAL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- PredictionHistory table
CREATE TABLE IF NOT EXISTS prediction_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    target_gpa REAL NOT NULL,
    predicted_gpa REAL NOT NULL,
    success_probability REAL NOT NULL,
    similar_student_count INTEGER NOT NULL,
    prediction_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_username ON user(username);
CREATE INDEX IF NOT EXISTS idx_user_role_id ON user(role_id);
CREATE INDEX IF NOT EXISTS idx_user_status ON user(status);
CREATE INDEX IF NOT EXISTS idx_student_profile_user_id ON student_profile(user_id);
CREATE INDEX IF NOT EXISTS idx_student_profile_student_code ON student_profile(student_code);
CREATE INDEX IF NOT EXISTS idx_prediction_history_user_id ON prediction_history(user_id);
CREATE INDEX IF NOT EXISTS idx_prediction_history_date ON prediction_history(prediction_date);
CREATE INDEX IF NOT EXISTS idx_prediction_history_user_date ON prediction_history(user_id, prediction_date);
```

---

## PART 5: IMPLEMENTATION SEQUENCE

### Phase 1: Foundation (Day 1-2)

| Task | Files | Dependencies |
|------|-------|--------------|
| 1.1 Project setup | `requirements.txt`, `.gitignore` | None |
| 1.2 Config module | `backend/config.py` | None |
| 1.3 Database setup | `backend/database.py` | config.py |
| 1.4 SQLAlchemy models | `backend/models/*.py` | database.py |
| 1.5 Schema definitions | `backend/schemas/*.py` | models |
| 1.6 Seed data | `backend/seed.py` | models |

### Phase 2: Auth & Core API (Day 3-4)

| Task | Files | Dependencies |
|------|-------|--------------|
| 2.1 Auth middleware | `backend/middleware/auth_middleware.py` | database, config |
| 2.2 Auth service | `backend/services/auth_service.py` | models, config |
| 2.3 Auth router | `backend/routers/auth.py` | auth_service |
| 2.4 User service | `backend/services/user_service.py` | models |
| 2.5 Profile service | `backend/services/profile_service.py` | models |
| 2.6 Profile router | `backend/routers/profile.py` | profile_service |
| 2.7 Admin router | `backend/routers/admin.py` | user_service, profile_service |
| 2.8 Main app | `backend/main.py` | all routers |

### Phase 3: ML Pipeline (Day 5-7)

| Task | Files | Dependencies |
|------|-------|--------------|
| 3.1 Obtain dataset | `data/students_dataset.csv` | None |
| 3.2 Training script | `backend/ml/train.py`, `train_model.py` | dataset |
| 3.3 Train and save artifacts | `data/model_artifacts.pkl` | train.py |
| 3.4 ML Service | `backend/ml/ml_service.py` | model_artifacts.pkl |
| 3.5 Prediction service | `backend/services/prediction_service.py` | ml_service |
| 3.6 Prediction router | `backend/routers/prediction.py` | prediction_service |

### Phase 4: Frontend (Day 8-10)

| Task | Files | Dependencies |
|------|-------|--------------|
| 4.1 Base template | `frontend/templates/base.html` | None |
| 4.2 Login page | `frontend/templates/login.html` | base.html |
| 4.3 CSS styling | `frontend/static/css/style.css` | None |
| 4.4 JS API client | `frontend/static/js/api.js` | None |
| 4.5 Auth JS | `frontend/static/js/auth.js` | api.js |
| 4.6 Dashboard | `frontend/templates/dashboard.html` + JS | api.js |
| 4.7 History | `frontend/templates/history.html` + JS | api.js |
| 4.8 Admin pages | `frontend/templates/admin/*` + JS | api.js |

### Phase 5: Deployment (Day 11-12)

| Task | Files | Dependencies |
|------|-------|--------------|
| 5.1 Dockerfile | `Dockerfile` | All code |
| 5.2 docker-compose | `docker-compose.yml` | Dockerfile |
| 5.3 Testing | Manual test all endpoints | All code |
| 5.4 README update | `README.md` | All code |

---

## PART 6: KEY DEPENDENCIES (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
jinja2==3.1.2
lightgbm==4.2.0
scikit-learn==1.3.2
numpy==1.26.2
pandas==2.1.4
joblib==1.3.2
```

---

## PART 7: ML TRAINING PIPELINE DETAIL

### 7.1 Dataset Columns
```
Gender, Age, Major, Attendance_Pct, Study_Hours_Per_Day,
Previous_CGPA, Sleep_Hours, Social_Hours_Week, Final_CGPA
```

### 7.2 Preprocessing Steps
1. Load CSV
2. Separate features (X) and target (y = Final_CGPA)
3. Label encode Gender: Male=0, Female=1
4. One-hot encode Major (fit on training data, save encoder)
5. Concatenate numeric + encoded features
6. Split 80/20 train/test
7. Train LightGBM
8. Evaluate (MAE, RMSE, R²)

### 7.3 KNN Setup
1. Take same feature matrix (without Final_CGPA)
2. Fit StandardScaler, transform features
3. Fit NearestNeighbors(n_neighbors=50, metric='euclidean')
4. Save: scaler, KNN model, historical features + Final_CGPA values

### 7.4 Inference Flow
```python
def predict(student_profile, target_gpa):
    # 1. Encode student features
    features = encode_features(student_profile)  # Same encoding as training

    # 2. LightGBM prediction
    predicted_gpa = model.predict([features])[0]

    # 3. KNN search
    scaled_features = knn_scaler.transform([features])
    distances, indices = knn_model.kneighbors(scaled_features)

    # 4. Get similar students' actual GPAs
    similar_gpas = historical_final_gpas[indices[0]]

    # 5. Calculate probability
    meeting_target = np.sum(similar_gpas >= target_gpa)
    total = len(similar_gpas)
    probability = (meeting_target / total * 100) if total > 0 else 50.0

    return predicted_gpa, probability, total
```

---

## PART 8: CONFIGURATION (config.py)

```python
import os
from pathlib import Path

class Settings:
    # Database
    DATABASE_DIR = Path(os.getenv("DATA_DIR", "data"))
    DATABASE_PATH = DATABASE_DIR / "app.db"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

    # ML Model
    MODEL_PATH = DATABASE_DIR / "model_artifacts.pkl"
    DATASET_PATH = DATABASE_DIR / "students_dataset.csv"

    # Auth
    SESSION_EXPIRY_HOURS = 24
    COOKIE_NAME = "session_id"
    COOKIE_MAX_AGE = SESSION_EXPIRY_HOURS * 3600

    # Password
    PASSWORD_MIN_LENGTH = 6

    # Prediction
    TARGET_GPA_MIN = 0.01
    TARGET_GPA_MAX = 4.0
    KNN_K = 50

    # Timezone
    TIMEZONE = "Asia/Ho_Chi_Minh"

    # Seed
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"

settings = Settings()
```

---

*END OF IMPLEMENTATION PLAN*
