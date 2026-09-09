# Target GPA Achievement Prediction System

Hệ thống dự đoán khả năng đạt được mục tiêu GPA dựa trên Machine Learning (LightGBM + KNN).

## Tính năng

- Đăng nhập với cookie session (admin / student)
- Quản lý người dùng và hồ sơ sinh viên (role ADMIN)
- Dự đoán GPA + xác suất đạt mục tiêu dựa trên hồ sơ sinh viên
- Giới hạn 1 lượt dự đoán mỗi ngày
- Lịch sử dự đoán
- Khóa/mở khóa tài khoản

## Công nghệ

- Backend: FastAPI + SQLAlchemy (SQLite)
- ML: LightGBM (dự đoán GPA), KNN K=50 (sinh viên tương đồng)
- Frontend: HTML + CSS + Vanilla JS

## Cài đặt

```bash
# Install dependencies
pip install -r requirements.txt

# Train ML model (tạo data/model_artifacts.pkl)
python train_model.py

# Start server
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Truy cập ứng dụng tại `http://localhost:8000`.

## Tài khoản mặc định

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |

## Hướng dẫn sử dụng cơ bản

### Bước 1: Đăng nhập tài khoản Admin

1. Mở trình duyệt, truy cập `http://localhost:8000`.
2. Nhập username `admin`, password `admin123` rồi bấm **Login**.
3. Bạn sẽ được chuyển đến **Admin Panel** với 3 trang: **Dashboard**, **Users**, **Profiles**.

### Bước 2: Tạo tài khoản sinh viên (Admin)

1. Click menu **Users** → bấm nút **+ Create User**.
2. Nhập username (tối thiểu 3 ký tự), password (tối thiểu 6 ký tự), chọn role **STUDENT**.
3. Bấm **Create**. Hệ thống tự tạo một hồ sơ sinh viên trống (student_code = `PENDING`).

### Bước 3: Cập nhật hồ sơ sinh viên (Admin)

Hồ sơ sinh viên phải đầy đủ thông tin thì mới dự đoán được:

1. Click menu **Profiles** → bấm nút **Setup** (hoặc **Edit**) ở hàng sinh viên tương ứng.
2. Điền đầy đủ: Mã SV, Họ tên, Giới tính, Tuổi, Ngành, Attendance %, Giờ học/ngày, Giờ ngủ/ngày, Giờ giao tiếp/tuần, CGPA hiện tại.
3. Bấm **Save**.

### Bước 4: Sinh viên đăng nhập và dự đoán

1. Đăng xuất admin (nút **Logout** trên thanh menu).
2. Sinh viên đăng nhập bằng username/password vừa được tạo ở Bước 2.
3. Trang **Dashboard** hiện thông tin hồ sơ của sinh viên.
4. Nhập **Target GPA** (ví dụ 3.5) vào ô *Make a Prediction* rồi bấm **Predict**.
5. Kết quả gồm: **Predicted GPA** (GPA dự đoán), **% xác suất đạt mục tiêu**, và số sinh viên tương đồng.
   - Mỗi sinh viên chỉ dự đoán **1 lần mỗi ngày**. Muốn dự đoán lại phải chờ ngày mới.
6. Xem **Lịch sử** dự đoán tại menu **History**.

### Bước 5: Quản lý người dùng (Admin)

- Menu **Users** → bấm **Lock** để khóa tài khoản (sinh viên khóa sẽ không đăng nhập được), bấm **Unlock** để mở lại.
- Khi sinh viên chưa có hồ sơ đầy đủ, hệ thống sẽ báo: *"Student profile is incomplete. Please ask admin to update your profile."*

## Docker

```bash
docker-compose up --build
```

SQLite database được lưu persistent qua volume `./data:/app/data`.

## Cấu trúc thư mục

```
backend/          # FastAPI app (config, models, schemas, routers, services, ml)
frontend/         # Templates + static assets (css, js)
data/             # DB + model artifacts
TrainingData/     # Dataset training
```