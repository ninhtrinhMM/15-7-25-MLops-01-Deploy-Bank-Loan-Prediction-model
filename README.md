# MỤC LỤC

1. [Giới thiệu chung](#1-giới-thiệu-chung)
2. [Chuẩn bị](#2-chuẩn-bị)
3. [ĐI chơi](#3-đi-chơi)
4. [ĐI ngủ](#4-đi-ngủ)

-------

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
- ```git init```
- ```git pull https://github.com/ninhtrinhMM/15-7-25-MLops-01-Deploy-Bank-Loan-Prediction-model```
- Ngay sau đó toàn bộ Github Repo từ trong link sẽ được tải về máy local.
### b. Cấu trúc của Github Repo
- jupyter-notebook-model     ## **Folder chứa file Jupyter-notebook và model được tải về**
  - ML_DL_Loan_Deal_Classification.ipynb     
  - model_ml.joblib 
- prometheus     ## **Folder chứa cấu hình của prometheus và service monitor của Prometheus**
  - prometheus-values.yaml
  - service-monitor.yaml
- tests     ##**Folder chứa file Pytest cho model**
  - test-py.py
- compose-jenkins.yaml
- Dockerfile
- Jaegar-deployment.yaml
- Jenkinsfile
- ML-app.py
- requirements.txt
- note-attention.txt
- terraform.tf
## 3. Khởi tạo Cluster (cụm máy) thông qua Terraform
Truy cập vào https://console.cloud.google.com/ và đăng nhập bằng tài khoản Google.  
Click vào My First Project → New Project.   
**Tên của Project phải trùng với giá trị Project của phần provider “google” trong file Terraform.**
<img width="579" height="313" alt="Image" src="https://github.com/user-attachments/assets/b84d9d3e-d6a5-4646-a648-a24b6ace13b1" />
