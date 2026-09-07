# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## Target GPA Achievement Prediction System

## Document Information

| Item | Value |
| --- | --- |
| Project Name | Target GPA Achievement Prediction System |
| Vietnamese Name | Hệ thống dự đoán khả năng đạt GPA mục tiêu |
| Version | 1.0 |
| Document Type | Software Requirements Specification |
| Development Team | 2 Members |
| Project Duration | 12 Weeks |
| Status | Draft |

# 1. Introduction

## 1.1 Purpose

Tài liệu này mô tả các yêu cầu chức năng và phi chức năng của hệ thống dự đoán khả năng đạt GPA mục tiêu.

Mục đích của hệ thống là hỗ trợ sinh viên đánh giá khả năng đạt được GPA mong muốn dựa trên hồ sơ học tập hiện tại và dữ liệu lịch sử đã được sử dụng để huấn luyện mô hình Machine Learning.

Tài liệu này là cơ sở cho các hoạt động:

- Thiết kế hệ thống (SDD)
- Phát triển phần mềm
- Kiểm thử
- Triển khai

## 1.2 Scope

Hệ thống cho phép:

- Quản lý tài khoản người dùng.
- Quản lý hồ sơ sinh viên.
- Dự đoán GPA kỳ vọng.
- Ước lượng xác suất đạt GPA mục tiêu.
- Xem kết quả dự đoán.
- Xem lịch sử dự đoán trong ngày.

Phiên bản 1 tập trung vào việc cung cấp chức năng dự đoán cơ bản và quản trị người dùng.

## 1.3 Intended Audience

Tài liệu dành cho:

- Nhóm phát triển.
- Giảng viên hướng dẫn.
- Người kiểm thử.
- Người đánh giá đồ án.

## 1.4 References

- SPEC v2
- Project Proposal (Short Version)
- Project Proposal (Detailed Version)
- SRS Preparation v1

# 2. Overall Description

## 2.1 Product Perspective

Hệ thống là một ứng dụng web bao gồm:

- Frontend
- Backend API
- Machine Learning Prediction Service
- Database

Mô hình tổng quát:

```text
Student
    │
    ▼
Web Application
    │
    ▼
Prediction Service
    │
    ▼
SQLite Database
```

## 2.2 Product Functions

Các chức năng chính:

### Student

- Đăng nhập.
- Xem hồ sơ cá nhân.
- Thực hiện dự đoán.
- Xem kết quả dự đoán.
- Xem lịch sử dự đoán trong ngày.
- Đăng xuất.

### Admin

- Đăng nhập.
- Tạo tài khoản.
- Quản lý tài khoản.
- Quản lý hồ sơ sinh viên.
- Khóa tài khoản.
- Mở khóa tài khoản.
- Đăng xuất.

---

## 2.3 User Classes

### Student

Người sử dụng chính của hệ thống.

Quyền:

- View Profile
- Predict GPA Achievement
- View Prediction History

### Admin

Người quản trị hệ thống.

Quyền:

- User Management
- Student Profile Management

## 2.4 Operating Environment

### Backend

- Python
- FastAPI

### Machine Learning

- LightGBM
- Scikit-Learn

### Database

- SQLite

### Deployment

- Docker
- Docker Compose

### Runtime

- CPU Only

## 2.5 Constraints

- Không sử dụng GPU.
- Chỉ hỗ trợ Web Application.
- Chỉ cho phép một lần dự đoán mỗi ngày.
- Student không được tự đăng ký tài khoản.
- Student không được sửa hồ sơ cá nhân.

## 2.6 Assumptions

- Dataset huấn luyện đã được chuẩn bị trước.
- Model đã được huấn luyện trước khi triển khai.
- Admin chịu trách nhiệm cập nhật dữ liệu hồ sơ sinh viên.

# 3. System Actors

## A1. Student

### Description

Người sử dụng chức năng dự đoán.

### Permissions

- Login
- View Profile
- Submit Prediction Request
- View Prediction Result
- View Prediction History
- Logout

## A2. Admin

### Description

Người quản trị hệ thống.

### Permissions

- Login
- Create User
- Manage User
- Manage Student Profile
- Lock User
- Unlock User
- Logout

# 4. Functional Requirements

## FR-01 Login

### Description

Hệ thống phải cho phép người dùng đăng nhập bằng tài khoản được cấp.

### Input

- Username
- Password

### Processing

- Xác thực thông tin đăng nhập.
- Kiểm tra trạng thái tài khoản.

### Output

- Đăng nhập thành công.
- Hoặc thông báo lỗi.

## FR-02 Logout

### Description

Hệ thống phải cho phép người dùng đăng xuất khỏi hệ thống.

## FR-03 View Profile

### Description

Student phải có khả năng xem hồ sơ cá nhân.

### Output

Hiển thị:

- Student Code
- Full Name
- Gender
- Age
- Major
- Attendance Percentage
- Study Hours
- Sleep Hours
- Social Hours
- Previous CGPA

## FR-04 Submit Prediction Request

### Description

Student gửi yêu cầu dự đoán khả năng đạt GPA mục tiêu.

### Input

- Target GPA

### Processing

1. Kiểm tra điều kiện dự đoán.
2. Lấy dữ liệu Student Profile.
3. Tính Predicted GPA.
4. Tìm nhóm sinh viên tương đồng.
5. Tính Success Probability.
6. Lưu lịch sử.

### Output

- Prediction Result

## FR-05 View Prediction Result

### Description

Hiển thị kết quả dự đoán.

### Output

- Predicted GPA
- Target GPA
- Success Probability
- Number of Similar Students

Ví dụ:

```text
Predicted GPA: 3.28

Target GPA: 3.50

Success Probability: 74.0%

Based on 120 Similar Students
```

## FR-06 View Prediction History

### Description

Student có thể xem kết quả dự đoán trong ngày hiện tại.

### Output

- Prediction Result của ngày hiện tại.

## FR-07 Create User

### Description

Admin có thể tạo tài khoản mới.

### Input

- Username
- Password
- Role

### Output

- User mới được tạo.

## FR-08 View User List

### Description

Admin có thể xem danh sách người dùng.

### Output

- User List

## FR-09 Lock User

### Description

Admin có thể khóa tài khoản người dùng.

## FR-10 Unlock User

### Description

Admin có thể mở khóa tài khoản người dùng.

## FR-11 Manage Student Profile

### Description

Admin có thể quản lý hồ sơ sinh viên.

### Operations

- Create Profile
- Update Profile
- View Profile

# 5. Use Case Specifications

## UC-01 Login

### Actor

Student, Admin

### Pre-condition

Tài khoản tồn tại.

### Main Flow

1. Người dùng nhập Username.
2. Người dùng nhập Password.
3. Hệ thống xác thực.
4. Hệ thống tạo phiên đăng nhập.
5. Chuyển tới màn hình chính.

### Alternative Flow

A1. Sai thông tin đăng nhập.

→ Hiển thị lỗi.

A2. Tài khoản bị khóa.

→ Từ chối đăng nhập.

### Post-condition

Người dùng đăng nhập thành công.

## UC-02 Submit Prediction Request

### Actor

Student

### Pre-condition

- Đã đăng nhập.
- Chưa thực hiện dự đoán trong ngày.

### Main Flow

1. Student mở Prediction Page.
2. Hệ thống tải Student Profile.
3. Student nhập Target GPA.
4. Student nhấn Predict.
5. Hệ thống kiểm tra dữ liệu.
6. Hệ thống thực hiện dự đoán GPA.
7. Hệ thống tìm nhóm sinh viên tương đồng.
8. Hệ thống tính Success Probability.
9. Hệ thống lưu Prediction History.
10. Hệ thống hiển thị kết quả.

### Alternative Flow

A1. Student đã dự đoán trong ngày.

→ Từ chối yêu cầu.

A2. Target GPA không hợp lệ.

→ Hiển thị lỗi.

### Post-condition

Prediction History được tạo.

## UC-03 View Prediction Result

### Actor

Student

### Pre-condition

Đã có Prediction Result.

### Main Flow

1. Student thực hiện dự đoán.
2. Hệ thống hiển thị kết quả.

### Post-condition

Không có.

## UC-04 View Prediction History

### Actor

Student

### Main Flow

1. Student mở History Page.
2. Hệ thống lấy lịch sử trong ngày.
3. Hiển thị kết quả.

## UC-05 Manage Student Profile

### Actor

Admin

### Main Flow

1. Admin chọn Student Profile.
2. Admin xem hoặc cập nhật dữ liệu.
3. Hệ thống lưu thay đổi.

### Post-condition

Student Profile được cập nhật.

# 6. Business Rules

## BR-01

Mỗi Student chỉ được phép thực hiện một lần dự đoán trong một ngày.

## BR-02

Nếu Student đã dự đoán trong ngày hiện tại thì hệ thống phải từ chối yêu cầu mới.

## BR-03

Prediction History chỉ tồn tại trong ngày hiện tại.

## BR-04

Student không được tự đăng ký tài khoản.

## BR-05

Mọi tài khoản Student phải được tạo bởi Admin.

## BR-06

Student không được chỉnh sửa Student Profile.

## BR-07

Admin là đối tượng duy nhất được phép chỉnh sửa Student Profile.

# 7. Data Requirements

## 7.1 Role

| Field | Description |
| --- | --- |
| role_id | Định danh vai trò |
| role_name | Tên vai trò |

Ví dụ:

- ADMIN
- STUDENT

## 7.2 User

| Field | Description |
| --- | --- |
| user_id | Định danh người dùng |
| username | Tên đăng nhập |
| password_hash | Mật khẩu mã hóa |
| role_id | Vai trò |
| status | Trạng thái |
| created_at | Ngày tạo |
| updated_at | Ngày cập nhật |

## 7.3 StudentProfile

| Field | Description |
| --- | --- |
| profile_id | Định danh hồ sơ |
| user_id | Chủ sở hữu |
| student_code | Mã sinh viên |
| full_name | Họ tên |
| gender | Giới tính |
| age | Tuổi |
| major | Chuyên ngành |
| attendance_percentage | Tỷ lệ chuyên cần |
| study_hours_per_day | Số giờ học mỗi ngày |
| sleep_hours_per_day | Số giờ ngủ mỗi ngày |
| social_hours_per_week | Số giờ hoạt động xã hội |
| previous_cgpa | GPA hiện tại |

## 7.4 PredictionHistory

| Field | Description |
| --- | --- |
| history_id | Định danh |
| user_id | Người thực hiện |
| target_gpa | GPA mục tiêu |
| predicted_gpa | GPA dự đoán |
| success_probability | Xác suất thành công |
| similar_student_count | Số sinh viên tương đồng |
| prediction_date | Ngày dự đoán |
| created_at | Thời gian tạo |

# 8. Non-Functional Requirements

## NFR-01 Performance

Response Time:

```text
< 100 ms
```

cho một yêu cầu dự đoán trong điều kiện bình thường.

## NFR-02 Resource Usage

Memory Usage:

```text
< 500 MB
```

## NFR-03 Startup Time

Cold Start:

```text
< 3 seconds
```

## NFR-04 Security

- Password phải được mã hóa.
- Chỉ người dùng hợp lệ mới được truy cập hệ thống.
- Student không được truy cập chức năng Admin.

## NFR-05 Maintainability

Hệ thống phải được thiết kế theo kiến trúc module hóa.

## NFR-06 Portability

Hệ thống phải triển khai được bằng Docker.

# 9. Future Enhancements (Out of Scope)

Các chức năng sau không thuộc Version 1:

- Explainable AI
- Multi-model Comparison
- Real-time Retraining
- Cloud Deployment
- Mobile Application
- Student Self Registration
- Historical Analytics Dashboard

# 10. Appendix

## System Context

```text
Student
    │
    ▼
Web Application
    │
    ▼
Prediction Service
    │
    ▼
SQLite Database

Admin
    │
    ▼
Web Application
```

END OF DOCUMENT
