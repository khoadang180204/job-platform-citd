# JobFAST - Website Sàn Tuyển Dụng Trực Tuyến

**Đồ án tốt nghiệp**  
**Sinh viên thực hiện:** Nguyễn Thành Khoa Đăng  
**MSSV:** 24410136  
**Giảng viên hướng dẫn:** ThS. Mai Xuân Hùng

---

## Giới thiệu

JobFAST là một nền tảng tuyển dụng trực tuyến được xây dựng bằng Django, cho phép:
- **Nhà tuyển dụng:** Đăng tin tuyển dụng, quản lý hồ sơ ứng tuyển
- **Ứng viên:** Tìm kiếm việc làm, ứng tuyển, nhận gợi ý việc làm phù hợp
- **Quản trị viên:** Quản lý toàn bộ hệ thống qua Django Admin

## Tính năng chính

### Module Người dùng
- Đăng ký, đăng nhập với phân quyền (Ứng viên/Nhà tuyển dụng)
- Quên mật khẩu với xác thực OTP qua email
- Quản lý hồ sơ cá nhân và kỹ năng

### Module Tuyển dụng
- CRUD tin tuyển dụng (Tạo, Xem, Sửa, Xóa)
- Tìm kiếm và lọc việc làm theo: từ khóa, địa điểm, ngành nghề, mức lương
- Ứng tuyển việc làm, lưu việc làm yêu thích

### Module NLP (Xử lý ngôn ngữ tự nhiên)
- Phân tích mô tả công việc và kỹ năng ứng viên
- Gợi ý việc làm phù hợp dựa trên TF-IDF và Cosine Similarity
- Hỗ trợ song ngữ Việt-Anh (Underthesea + TextBlob)

### Dashboard Phân tích
- Thống kê số liệu tuyển dụng
- Biểu đồ đơn ứng tuyển theo ngày
- Biểu đồ việc làm theo ngành nghề

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python 3.10+, Django 4.2+ |
| Database | SQLite3 |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| NLP | Underthesea, TextBlob, Scikit-learn |
| Charts | Chart.js |
| Icons | Font Awesome 6 |

## Cài đặt

### Yêu cầu hệ thống
- Python 3.10 trở lên
- pip (Python package manager)

### Các bước cài đặt

```bash
# 1. Clone repository
git clone https://github.com/khoadang180204/job-platform-citd
cd job-platform

# 2. Tạo môi trường ảo
python -m venv venv

# 3. Kích hoạt môi trường ảo
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Cài đặt dependencies
pip install -r requirements.txt

# 5. Chạy migrations
python manage.py migrate

# 6. Tạo superuser (tùy chọn)
python manage.py createsuperuser

# 7. Chạy server
python manage.py runserver
```

### Truy cập ứng dụng
- **Trang chủ:** http://127.0.0.1:8000/
- **Django Admin:** http://127.0.0.1:8000/admin/

## Cấu trúc dự án

```
job-platform/
├── accounts/           # Module quản lý người dùng
│   ├── models.py       # UserProfile, PasswordResetOTP
│   ├── views.py        # Login, Register, Profile
│   └── email_service.py # Gửi OTP qua email
├── jobs/               # Module quản lý việc làm
│   ├── models.py       # Job, Application, Skill, Company
│   ├── views.py        # Job list, detail, apply
│   ├── nlp_processor.py # Xử lý NLP
│   └── matching_service.py # Matching việc làm
├── dashboard/          # Dashboard nhà tuyển dụng
├── templates/          # HTML templates
├── static/             # CSS, JS, Images
└── manage.py
```

## Ghi chú phát triển

- Project được phát triển cho mục đích học tập và đồ án tốt nghiệp
- Database sử dụng SQLite3 cho đơn giản, có thể nâng cấp lên PostgreSQL cho production
- Email service sử dụng Gmail SMTP cho demo

## License

Dự án này được thực hiện cho mục đích học tập tại Trường Đại học Công nghệ Thông tin - ĐHQG TP.HCM.