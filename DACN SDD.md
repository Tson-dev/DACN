# SOFTWARE DESIGN DOCUMENT (SDD)

# Target GPA Achievement Prediction System

---

# Document Information

| Item | Value |
|--------|--------|
| Project Name | Target GPA Achievement Prediction System |
| Version | 1.0 |
| Document Type | Software Design Document |
| Based On | SRS v1 |
| Development Team | 2 Members |
| Status | Draft |

---

# 1. Introduction

## 1.1 Purpose

Tài liệu này mô tả thiết kế kỹ thuật của hệ thống dự đoán khả năng đạt GPA mục tiêu.

Mục tiêu của tài liệu:

- Làm cơ sở cho việc triển khai hệ thống.
- Làm tài liệu tham khảo cho Backend Developer.
- Làm tài liệu giao tiếp giữa Backend và Frontend.
- Làm cơ sở cho việc kiểm thử hệ thống.

---

## 1.2 Scope

SDD mô tả:

- Kiến trúc hệ thống
- Thiết kế database
- Thiết kế module
- Thiết kế API
- Thiết kế ML Service
- Luồng xử lý dữ liệu

Không bao gồm:

- Thiết kế giao diện chi tiết
- Thiết kế UI/UX
- Mobile Application
- Các tính năng thuộc Future Version

---

# 2. System Architecture

## 2.1 Architecture Overview

Hệ thống được xây dựng theo mô hình 3 lớp.

```text
+------------------+
|     Frontend     |
+------------------+
          |
          v
+------------------+
|  FastAPI Backend |
+------------------+
          |
    +-----+-----+
    |           |
    v           v
Database   ML Service
(SQLite)   (LightGBM)
```

---

## 2.2 Runtime Components

### Frontend

Chức năng:

- Login
- View Profile
- Submit Prediction
- View Prediction Result
- View History
- Admin Management

---

### Backend API

Chức năng:

- Authentication
- Authorization
- Business Logic
- Data Validation
- API Exposure

---

### Database

Lưu trữ:

- User
- Role
- Student Profile
- Prediction History

---

### ML Service

Chức năng:

- Load Model
- Predict GPA
- Find Similar Students
- Calculate Success Probability

---

# 3. Database Design

---

## 3.1 Entity Relationship Diagram

```text
Role
 |
 |
 v
User
 | \
 |  \
 |   \
 v    v
StudentProfile
PredictionHistory
```

---

## 3.2 Table: Role

| Column | Type |
|----------|----------|
| role_id | INTEGER |
| role_name | VARCHAR(50) |

---

Sample Data

```text
ADMIN
STUDENT
```

---

## 3.3 Table: User

| Column | Type |
|----------|----------|
| user_id | INTEGER |
| username | VARCHAR(100) |
| password_hash | VARCHAR(255) |
| role_id | INTEGER |
| status | VARCHAR(20) |
| created_at | DATETIME |
| updated_at | DATETIME |

---

Status:

```text
ACTIVE
LOCKED
```

---

## 3.4 Table: StudentProfile

| Column | Type |
|----------|----------|
| profile_id | INTEGER |
| user_id | INTEGER |
| student_code | VARCHAR(20) |
| full_name | VARCHAR(100) |
| gender | VARCHAR(20) |
| age | INTEGER |
| major | VARCHAR(100) |
| attendance_percentage | FLOAT |
| study_hours_per_day | FLOAT |
| sleep_hours_per_day | FLOAT |
| social_hours_per_week | FLOAT |
| previous_cgpa | FLOAT |

---

Relationship

```text
User 1 --- 1 StudentProfile
```

---

## 3.5 Table: PredictionHistory

| Column | Type |
|----------|----------|
| history_id | INTEGER |
| user_id | INTEGER |
| target_gpa | FLOAT |
| predicted_gpa | FLOAT |
| success_probability | FLOAT |
| similar_student_count | INTEGER |
| prediction_date | DATE |
| created_at | DATETIME |

---

Relationship

```text
User 1 --- N PredictionHistory
```

---

# 4. Module Design

---

## 4.1 Auth Module

### Responsibilities

- Login
- Logout
- Session Management

### APIs

```text
POST /api/auth/login

POST /api/auth/logout
```

---

## 4.2 User Module

### Responsibilities

- Create User
- View User
- Lock User
- Unlock User

### APIs

```text
POST /api/admin/users

GET /api/admin/users

PUT /api/admin/users/{id}/lock

PUT /api/admin/users/{id}/unlock
```

---

## 4.3 Profile Module

### Responsibilities

- View Student Profile
- Update Student Profile

### APIs

```text
GET /api/profile/me

GET /api/admin/profiles

PUT /api/admin/profiles/{id}
```

---

## 4.4 Prediction Module

### Responsibilities

- Validate Request
- Execute Prediction
- Save History

### APIs

```text
POST /api/predictions

GET /api/predictions/today
```

---

# 5. Machine Learning Design

---

## 5.1 Overview

ML Service sử dụng mô hình LightGBM để dự đoán GPA.

Dataset huấn luyện:

```text
University Student Performance & Habits Dataset
```

Khoảng:

```text
5000 records
```

---

## 5.2 Training Phase

```text
Dataset
    |
Feature Engineering
    |
Data Preprocessing
    |
LightGBM Training
    |
Model File
```

---

Output:

```text
model.pkl
```

---

## 5.3 Runtime Phase

```text
Student Profile
       |
       v
Feature Vector
       |
       v
LightGBM Model
       |
       v
Predicted GPA
```

---

## 5.4 Similar Student Matching

Mục đích:

Tìm nhóm sinh viên có đặc điểm tương đồng với người dùng hiện tại.

---

Thuật toán:

```text
K-Nearest Neighbors (KNN)
```

---

Khoảng cách:

```text
Euclidean Distance
```

---

Pipeline:

```text
Student Profile
        |
        v
Feature Normalization
        |
        v
KNN Search
        |
        v
Top K Similar Students
```

---

## 5.5 Success Probability Calculation

Input:

```text
Predicted GPA

Target GPA

Top K Similar Students
```

---

Output:

```text
Success Probability (%)
```

---

Công thức cụ thể sẽ được xác định trong giai đoạn triển khai và thử nghiệm mô hình.

---

# 6. Business Process Design

---

## 6.1 Login Flow

```text
User
 |
Enter Credentials
 |
 v
Authentication
 |
 +--> Invalid
 |      |
 |      v
 |   Error
 |
 v
Session Created
 |
 v
Home Page
```

---

## 6.2 Prediction Flow

```text
Student
    |
    v
Input Target GPA
    |
    v
Validation
    |
    v
Load Student Profile
    |
    v
Predict GPA
    |
    v
Find Similar Students
    |
    v
Calculate Probability
    |
    v
Save History
    |
    v
Return Result
```

---

# 7. API Design

---

# 7.1 Authentication API

---

## Login

### Endpoint

```http
POST /api/auth/login
```

---

Request

```json
{
  "username": "student01",
  "password": "123456"
}
```

---

Response

```json
{
  "success": true,
  "message": "Login successful"
}
```

---

## Logout

### Endpoint

```http
POST /api/auth/logout
```

---

Response

```json
{
  "success": true
}
```

---

# 7.2 Profile API

---

## View Own Profile

### Endpoint

```http
GET /api/profile/me
```

---

Response

```json
{
  "student_code": "SE001",
  "full_name": "Nguyen Van A",
  "gender": "Male",
  "age": 21,
  "major": "Software Engineering",
  "attendance_percentage": 90,
  "study_hours_per_day": 4,
  "sleep_hours_per_day": 7,
  "social_hours_per_week": 5,
  "previous_cgpa": 3.2
}
```

---

# 7.3 Prediction API

---

## Submit Prediction

### Endpoint

```http
POST /api/predictions
```

---

Request

```json
{
  "target_gpa": 3.5
}
```

---

Response

```json
{
  "predicted_gpa": 3.28,
  "target_gpa": 3.50,
  "success_probability": 74.2,
  "similar_student_count": 120
}
```

---

Error Response

```json
{
  "success": false,
  "message": "Prediction already exists today."
}
```

---

## View Today Prediction

### Endpoint

```http
GET /api/predictions/today
```

---

Response

```json
{
  "predicted_gpa": 3.28,
  "target_gpa": 3.50,
  "success_probability": 74.2,
  "similar_student_count": 120,
  "prediction_date": "2025-09-06"
}
```

---

# 7.4 Admin User API

---

## Create User

### Endpoint

```http
POST /api/admin/users
```

---

Request

```json
{
  "username": "student02",
  "password": "123456",
  "role": "STUDENT"
}
```

---

Response

```json
{
  "success": true
}
```

---

## Lock User

### Endpoint

```http
PUT /api/admin/users/{id}/lock
```

---

## Unlock User

### Endpoint

```http
PUT /api/admin/users/{id}/unlock
```

---

# 8. Security Design

---

## Authentication

```text
Session-Based Authentication
```

---

## Password Storage

```text
Password Hashing
```

Khuyến nghị:

```text
bcrypt
```

---

## Authorization

Role-Based Access Control (RBAC)

---

Roles:

```text
ADMIN

STUDENT
```

---

# 9. Deployment Design

---

## Docker Components

```text
Frontend

Backend

SQLite Database File
```

---

## Deployment Diagram

```text
Docker Container
 |
 +-- FastAPI
 |
 +-- ML Model
 |
 +-- SQLite
```

---

# 10. Future Version Considerations

Không thuộc phạm vi Version 1:

- JWT Authentication
- Multi-Model Comparison
- Explainable AI
- Automatic Retraining
- External Database
- Mobile Client
- Cloud Deployment

---

END OF DOCUMENT