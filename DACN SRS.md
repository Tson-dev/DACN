# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)

## Target GPA Achievement Prediction System

## Document Information

|Item|Value|
|---|---|
|Project Name|Target GPA Achievement Prediction System|
|Vietnamese Name|Hệ thống dự đoán khả năng đạt GPA mục tiêu|
|Version|1.1.3|
|Document Type|Software Requirements Specification|
|Status|Draft|

# 1. Introduction

## 1.1 Purpose

Tài liệu này mô tả các yêu cầu chức năng và phi chức năng của hệ thống dự đoán khả năng đạt GPA mục tiêu.

Mục đích của hệ thống là hỗ trợ sinh viên đánh giá khả năng đạt được GPA mong muốn dựa trên hồ sơ học tập hiện tại và dữ liệu lịch sử đã được sử dụng để huấn luyện mô hình Machine Learning.

Tài liệu này là cơ sở cho các hoạt động:

Thiết kế hệ thống (SDD)
Phát triển phần mềm
Kiểm thử
Triển khai

## 1.2 Scope

Hệ thống cho phép:

Quản lý tài khoản người dùng.
Quản lý hồ sơ sinh viên.
Dự đoán GPA kỳ vọng.
Ước lượng xác suất đạt GPA mục tiêu.
Xem kết quả dự đoán.
Xem lịch sử dự đoán trong ngày.

Phiên bản 1 tập trung vào việc cung cấp chức năng dự đoán cơ bản và quản trị người dùng.

## 1.3 Intended Audience

Tài liệu dành cho:

Nhóm phát triển.
Giảng viên hướng dẫn.
Người kiểm thử.
Người đánh giá đồ án.

## 1.4 References

SPEC v1.3.2
Project Proposal (Short Version)
Project Proposal (Detailed Version)
SRS Preparation v1

# 2. Overall Description

## 2.1 Product Perspective

Hệ thống là một ứng dụng web bao gồm:

Frontend
Backend API
Machine Learning Prediction Service
Database

Mô hình tổng quát:

```mermaid

flowchart TB
FE[Frontend]
BE[Backend]
PS[Prediction Service]
DB[SQLite Database]

FE --> BE
BE--> PS
PS --> DB
```

## 2.2 Product Functions

Các chức năng chính:

### Student

Đăng nhập.
Xem hồ sơ cá nhân.
Thực hiện dự đoán.
Xem kết quả dự đoán.
Xem lịch sử dự đoán trong ngày.
Đăng xuất.

### Admin

Đăng nhập.
Tạo tài khoản.
Quản lý tài khoản.
Quản lý hồ sơ sinh viên.
Khóa tài khoản.
Mở khóa tài khoản.
Đăng xuất.

## 2.3 User Classes

|Tên|Mô tả|Quyền|
|---|---|---|
|Student|Người sử dụng chính của hệ thống|View Profile<br>Predict GPA Achievement<br>View Prediction History|
|Admin|Người quản trị hệ thống|User Management<br>Student Profile Management|

## 2.4 Operating Environment

|Name|Environment|
|---|---|
|Backend|Python<br>FastAPI|
|Machine Learning|LightGBM<br>Scikit-Learn|
|Database|SQLite|
|Deployment|Docker<br>Docker Conpose|
|Rutime|CPU Only|

## 2.5 Constraints

Không sử dụng GPU.
Chỉ hỗ trợ Web Application.
Chỉ cho phép một lần dự đoán mỗi ngày.
Student không được tự đăng ký tài khoản.
Student không được sửa hồ sơ cá nhân.

## 2.6 Assumptions

Dataset huấn luyện đã được chuẩn bị trước.
Model đã được huấn luyện trước khi triển khai.
Admin chịu trách nhiệm cập nhật dữ liệu hồ sơ sinh viên.

# 3. System Actors

|Actor|Name|Description|Permissions|
|---|---|---|---|
|A1|Student|Người sử dụng chức năng dự đoán|Login<br>View Profile<br>Submit Prediction Request<br>View Prediction Result<br>View Prediction History<br>Logout|
|A2|Admin|Người quản trị hệ thống|Login<br>Create User<br>Manage User<br>Manage Student Profile<br>Lock User<br>Unlock User<br>Logout|

# 4. Functional Requirements

|ID|Functional Requirement|Description|Input|Processing|Operations|Output|
|---|---|---|---|---|---|---|
|<span style="white-space: nowrap;">FR-01</span>|Login|Hệ thống cho phép người dùng đăng nhập bằng tài khoản được cấp|Username<br>Password|1. Xác thực thông tin đăng nhập.<br>2. Kiểm tra trạng thái tài khoản|-|Đăng nhập thành công.<br>Hoặc thông báo lỗi|
|FR-02|Logout|Hệ thống cho phép người dùng đăng xuất khỏi hệ thống|-|-|-|-|
|FR-03|View Profile|Student có thể xem hồ sơ cá nhân|-|-|-|Hiển thị:<br>Student Code<br>Full Name<br>Gender<br>Age<br>Major<br>Attendance Percentage<br>Study Hours<br>Sleep Hours<br>Social Hours<br>Previous CGPA|
|FR-04|Submit Prediction Request|Student gửi yêu cầu dự đoán khả năng đạt GPA mục tiêu|Target GPA|1. Kiểm tra điều kiện dự đoán.<br>2. Lấy dữ liệu Student Profile.<br>3. Tính Predicted GPA.<br>4. Tìm nhóm sinh viên tương đồng.<br>5. Tính Success Probability.<br>6. Lưu lịch sử|-|Prediction Result|
|FR-05|View Prediction Result|Hiển thị kết quả dự đoán|-|-|-|Predicted GPA<br>Target GPA<br>Success Probability<br>Number of Similar Students<br><br>Ví dụ:<br>Predicted GPA: 3.28<br>Target GPA: 3.50<br>Success Probability: 74.0%<br>Based on 120 Similar Students|
|FR-06|View Prediction History|Student có thể xem kết quả dự đoán trong ngày hiện tại|-|-|-|Prediction Result của ngày hiện tại|
|FR-07|Create User|Admin có thể tạo tài khoản mới|Username<br>Password<br>Role|-|-|User mới được tạo|
|FR-08|View User List|Admin có thể xem danh sách người dùng|-|-|-|User List|
|FR-09|Lock User|Admin có thể khóa tài khoản người dùng|-|-|-|-|
|FR-10|Unlock User|Admin có thể mở khóa tài khoản người dùng|-|-|-|-|
|FR-11|Manage Student Profile|Admin có thể quản lý hồ sơ sinh viên|-|-|Update Profile<br>View Profile|-|

# 5. Use Case Specifications

|Use Case|Actor|Pre-condition|Main Flow|Alternative Flow|Post-condition|
|---|---|---|---|---|---|
|UC-01 Login|Student, Admin|Tài khoản tồn tại|1. Người dùng nhập Username.<br>2. Người dùng nhập Password.<br>3. Hệ thống xác thực.<br>4. Hệ thống tạo phiên đăng nhập.<br>5. Chuyển tới màn hình chính|A1. Sai thông tin đăng nhập.<br>−> Hiển thị lỗi.<br><br>A2. Tài khoản bị khóa.<br>−> Từ chối đăng nhập|Người dùng đăng nhập thành công|
|UC-02 Submit Prediction Request|Student|Đã đăng nhập.<br>Chưa thực hiện dự đoán trong ngày|1. Student mở Prediction Page.<br>2. Hệ thống tải Student Profile.<br>3. Student nhập Target GPA.<br>4. Student nhấn Predict.<br>5. Hệ thống kiểm tra dữ liệu.<br>6. Hệ thống thực hiện dự đoán GPA.<br>7. Hệ thống tìm nhóm sinh viên tương đồng.<br>8. Hệ thống tính Success Probability.<br>9. Hệ thống lưu Prediction History.<br>10. Hệ thống hiển thị kết quả|A1. Student đã dự đoán trong ngày.<br>−> Từ chối yêu cầu.<br><br>A2. Invalid Target GPA<br><br>Điều kiện:<br>`target_gpa <= 0` hoặc `target_gpa > 4.0`<br><br>A3. Student Profile không tồn tại<br><br>1. Hệ thống không tìm thấy Student Profile.<br>2. Hệ thống từ chối yêu cầu dự đoán.<br>3. Hệ thống hiển thị thông báo: `"Student Profile not found."`|Prediction History được tạo|
|UC-03 View Prediction Result|Student|Đã có Prediction Result|1. Student thực hiện dự đoán.<br>2. Hệ thống hiển thị kết quả|-|Không có|
|UC-04 View Prediction History|Student|-|1. Student mở History Page.<br>2. Hệ thống lấy lịch sử trong ngày.<br>3. Hiển thị kết quả|-|-|
|UC-05 Manage Student Profile|Admin|-|1. Admin chọn Student Profile.<br>2. Admin xem hoặc cập nhật dữ liệu.<br>3. Hệ thống lưu thay đổi|-|Student Profile được cập nhật|
|UC-06 Create User|Admin|Admin đã đăng nhập|1. Admin mở chức năng Create User.<br>2. Admin nhập username, password và role.<br>3. Hệ thống kiểm tra dữ liệu.<br>4. Hệ thống tạo User mới.<br>5. Hệ thống tự động tạo Student Profile rỗng tương ứng.<br>6. Hệ thống hiển thị thông báo thành công|A1. Username đã tồn tại<br>−> từ chối tạo|User được tạo.<br>Student Profile rỗng được tạo tương ứng|
|UC-07 View User List|Admin|-|1. Admin mở danh sách User.<br>2. Hệ thống hiển thị danh sách User.<br>3. Admin xem thông tin User|-|-|
|UC-08 Lock User|Admin|-|1. Admin chọn User.<br>2. Admin chọn Lock Account.<br>3. Hệ thống cập nhật trạng thái LOCKED.<br>4. Hệ thống hiển thị thông báo thành công|-|User được lên lịch chuyển sang trạng thái LOCKED từ ngày tiếp theo|
|UC-09 Unlock User|Admin|-|1. Admin chọn User.<br>2. Admin chọn Unlock Account.<br>3. Hệ thống cập nhật trạng thái ACTIVE.<br>4. Hệ thống hiển thị thông báo thành công|-|User ở trạng thái ACTIVE|

# 6. Business Rules

|Business Rule|Description|
|---|---|
|**BR-01**|Mỗi **Student** chỉ được phép thực hiện một lần dự đoán trong một ngày|
|**BR-02**|Nếu **Student** đã dự đoán trong ngày hiện tại thì hệ thống phải từ chối yêu cầu mới|
|**BR-03**|Chức năng View Prediction History chỉ hiển thị kết quả dự đoán của ngày hiện tại|
|**BR-04**|**Student** không được tự đăng ký tài khoản|
|**BR-05**|User có hai trạng thái: `"ACTIVE"` và `"LOCKED"`|
|**BR-06**|Khi tài khoản bị chuyển sang trạng thái `"LOCKED"`, thay đổi sẽ có hiệu lực từ ngày tiếp theo<br>Các phiên đăng nhập hiện tại vẫn được phép sử dụng đến hết ngày hiện tại|
|**BR-07**|Mọi tài khoản **Student** phải được tạo bởi **Admin**|
|**BR-08**|Student không được chỉnh sửa **Student Profile**|
|**BR-09**|Admin là đối tượng duy nhất được phép chỉnh sửa **Student Profile**|

# 7. Data Requirements

## 7.1 Role

|Field|Description|
|---|---|
|role_id|Định danh vai trò|
|role_name|Tên vai trò|

Ví dụ:

ADMIN
STUDENT

## 7.2 User

|Field|Description|
|---|---|
|user_id|Định danh người dùng|
|username|Tên đăng nhập|
|password_hash|Mật khẩu mã hóa|
|role_id|Vai trò|
|status|Trạng thái|
|created_at|Ngày tạo|
|updated_at|Ngày cập nhật|

## 7.3 StudentProfile

|Field|Description|
|---|---|
|profile_id|Định danh hồ sơ|
|user_id|Chủ sở hữu|
|student_code|Mã sinh viên|
|full_name|Họ tên|
|gender|Giới tính|
|age|Tuổi|
|major|Chuyên ngành|
|attendance_percentage|Tỷ lệ chuyên cần|
|study_hours_per_day|Số giờ học mỗi ngày|
|sleep_hours_per_day|Số giờ ngủ mỗi ngày|
|social_hours_per_week|Số giờ hoạt động xã hội|
|previous_cgpa|GPA hiện tại|

## 7.4 PredictionHistory

|Field|Description|
|---|---|
|history_id|Định danh|
|user_id|Người thực hiện|
|target_gpa|GPA mục tiêu|
|predicted_gpa|GPA dự đoán|
|success_probability|Xác suất thành công|
|similar_student_count|Số sinh viên tương đồng|
|prediction_date|Ngày dự đoán|
|created_at|Thời gian tạo|

## 7.5 Validation Rules

|Field|Rule|
|---|---|
|target_gpa|0 < GPA ≤ 4.0|
|attendance_percentage|0 ≤ value ≤ 100|
|previous_cgpa|0 ≤ GPA ≤ 4.0|
|age|> 0|
|study_hours_per_day|≥ 0|
|sleep_hours_per_day|≥ 0|
|social_hours_per_week|≥ 0|

# 8. Non-Functional Requirements
|Non-Functional Requirement|Description|
|---|---|
|**NFR-01 Performance**|Response Time: `< 100 ms` cho một yêu cầu dự đoán trong điều kiện bình thường.|
|**NFR-02 Resource Usage**|Memory Usage: `< 500 MB`|
|**NFR-03 Startup Time**|Cold Start: `< 3 seconds`|
|**NFR-04 Security**|Password phải được mã hóa.<br>Chỉ người dùng hợp lệ mới được truy cập hệ thống.<br>Student không được truy cập chức năng Admin.|
|**NFR-05 Maintainability**|Hệ thống phải được thiết kế theo kiến trúc module hóa.|
|**NFR-06 Portability**|Hệ thống phải triển khai được bằng Docker.|

# 9. Future Enhancements (Out of Scope)

Các chức năng sau không thuộc Version 1:

Explainable AI
Multi-model Comparison
Real-time Retraining
Cloud Deployment
Mobile Application
Student Self Registration
Historical Analytics Dashboard
Profile Completeness Validation
Pending Account Status

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
