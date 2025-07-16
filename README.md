# MỤC LỤC

1. [Giới thiệu chung](#1-giới-thiệu-chung)
2. [Chuẩn bị](#2-chuẩn-bị)
3. [ĐI chơi](#3-đi-chơi)
4. [ĐI ngủ](#4-đi-ngủ)

---

## 1. Giới thiệu chung

### a. Sơ lược về mô hình ML và mục đích triển khai
- Mô hình Machine Learning trong Github Repo được huấn luyện với bộ dữ liệu chứa 45.000 bản ghi về người đăng ký vay vốn, với nhiều thuộc tính khác nhau liên quan đến:
  - Thông tin nhân khẩu học cá nhân
  - Tình hình tài chính
  - Chi tiết khoản vay
- Bộ dữ liệu được sử dụng cho:
  - Mô hình hóa dự đoán
  - Đánh giá rủi ro tín dụng
  - Dự đoán khả năng vỡ nợ
- Mô hình được Data Preprocessing bởi các phương pháp Label Encoding và Standard Scaler.
- Sau khi train model thành công, triển khai model trên hệ thống Cluster (cụm máy) trên Google Cloud Platform để nhận request từ người dùng

### b. Các công cụ cần cài đặt sẵn trên hệ điều hành Ubuntu
- Gcloud CLI
- Git
- Kubectl
- Ngrok
- Terraform
- Helm
## 2. Chuẩn bị

### a. Kéo Repo (Kho chứa các file và folder) trên Github về:
Mở 1 folder trống bất kỳ trên máy Local bằng VS Code (hoặc IDE khác như Trae, Pycharm, Eclipse,..), xong mở Terminal và gõ lần lượt các lệnh sau: 
```git init```
```git pull ```
