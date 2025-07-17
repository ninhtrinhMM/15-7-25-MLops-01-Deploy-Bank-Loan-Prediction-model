# MỤC LỤC

1. [Giới thiệu chung](#1-giới-thiệu-chung)
2. [Chuẩn bị](#2-chuẩn-bị)
3. [Khởi tạo Cluster (cụm máy) trên GCP thông qua Terraform](#3-Khởi-tạo-Cluster-(cụm-máy)-trên-GCP-thông-qua-Terraform)
4. [Khởi tạo Github Repo](#4-Khởi-tạo-Github-Repo)
5. [Thiết lập luồng tự động hóa CI/CD vói Jenkins](#5-Thiết-lập-luồng-tự-động-hóa-CI/CD-với-Jenkins)

-------

## 1. Giới thiệu tổng quát

### a. Sơ lược về mô hình ML và mục đích triển khai
- Mô hình Machine Learning trong Github Repo được huấn luyện với bộ dữ liệu chứa 45.000 bản ghi về người đăng ký vay vốn, với nhiều thuộc tính khác nhau liên quan đến:
  - Thông tin nhân khẩu học cá nhân
  - Tình hình tài chính
  - Chi tiết khoản vay
- Bộ dữ liệu được sử dụng cho:
  - Mô hình hóa dự đoán
  - Đánh giá rủi ro tín dụng
  - Dự đoán khả năng vỡ nợ
- Mô hình được Data Preprocessing bởi các phương pháp Label Encoding, Standard Scaler và sử dụng phương pháp GridsearchCV để tìm ra Hyper Parameter tốt nhát cho model. Kết quả là model đạt được Metric Accuracy lên đến 93%.  
- Sau khi train model thành công, chúng ta triển khai model trên hệ thống Cluster (cụm máy) trên Google Cloud Platform, vận hành và xây dựng bởi luồng CI/CD Jenkins tự động tích hợp với Cloud K8S để nhận request từ người dùng.

### b. Các công cụ cần cài đặt sẵn trên hệ điều hành Ubuntu
- Gcloud CLI
- Git
- Kubectl
- Ngrok
- Terraform
- Helm
## 2. Chuẩn bị
### a. Kéo Repo (Kho chứa các file và folder) trên Github về:
Mở 1 folder trống bất kỳ trên máy Local bằng VS Code (hoặc IDE khác như Trae, Pycharm, Eclipse,..), xong mở Terminal trong đó và gõ lần lượt các lệnh sau: 
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
## **3. Khởi tạo Cluster (cụm máy) trên GCP thông qua Terraform**
Truy cập vào https://console.cloud.google.com/ và đăng nhập bằng tài khoản Google.  
Click vào My First Project → chọn "New Project" để tạo Project mới.  
<img width="1033" height="54" alt="Image" src="https://github.com/user-attachments/assets/a61fa180-a3b1-4e5b-8345-9e4d612e2905" />  

**Lưu ý khi điền tên của Project phải trùng với tên Project của phần provider “google” trong file Terraform.**
<img width="579" height="313" alt="Image" src="https://github.com/user-attachments/assets/b84d9d3e-d6a5-4646-a648-a24b6ace13b1" />  

Tạo xong project, trở lại VS Code, chạy Termianl command sau: ```gcloud auth login``` và chọn tài khoản Google cá nhân.  
Tạo config cho Gcloud lấy đúng Project: ```gcloud config set project <Tên Project trong file Terraform>```  
Tạo Application Default Credentials cho Terraform: ```gcloud auth application-default login``` và chọn lại đúng tài khoản Google cá nhân.  
Khởi động các APIs cần thiết bằng 3 command sau:  
```gcloud services enable compute.googleapis.com```  
```gcloud services enable container.googleapis.com```  
```gcloud services enable storage.googleapis.com```  
Chạy các lệnh sau để kiểm tra Terraform đã sẵn sàng và syntax trong file Terraform chưa:  
```terraform init```  
```terraform plan```  
Chạy file Terraform: ```terraform apply```, sau đó chọn "Y".  
Sau khi chạy xong, truy cập https://console.cloud.google.com/ --> My First Project --> <Tên Project trong file Terraform> --> Kubenetes Engines --> Cluster để kiểm tra   

<img width="1033" height="539" alt="Image" src="https://github.com/user-attachments/assets/ceffd75e-a224-43be-a3fe-776306e76fb3" />  

Nếu thấy tên của Cluster trùng với tên Cluster được thiết lập trong file Terraform nghĩa là thành công tạo 1 cụm máy Cluster, bên trong có 3 máy ảo VM Instance có cấu hình là E2 Medium.  

<img width="928" height="456" alt="Image" src="https://github.com/user-attachments/assets/2c0ff572-2368-48a4-a709-06a4e47d3897" />  
<img width="503" height="307" alt="Image" src="https://github.com/user-attachments/assets/fc71fe0a-2b1f-440f-9303-3a46c3e8c655" />  

## **4. Khởi tạo Github Repo**  
Truy cập github.com, tạo tài khoản nếu chưa có và khởi tạo 1 Repository ( Kho lưu trữ các file ) mới, điền Repository Name và để ở chế độ **PUBLIC**.   

<img width="327" height="148" alt="Image" src="https://github.com/user-attachments/assets/8c25622d-d712-48f0-ab1d-3edbbfc86ed6" />  

Trở về VS Code, chạy lệnh: ```git add .``` để add tất cả các Folder hiện tại vào Stageing Area.  
Chạy lệnh: ```git commit -m <Tên commit>``` để tạo 1 bản ghi Commit mới.  
Chạy lệnh: ```git remote add origin <Link Github Repo bạn vừa mới tạo>``` để tạo 1 remote tên origin nhằm liên kểt Repo dưới Local (toàn bộ file và folder đang được mở bằng VS Code) với Github Repo mới của bạn. 
Đồng hóa ( Synchronize ) giữa Repo dưới Local với Github repo: ```git push -u origin main```  
Từ giờ khi có 1 Commit mới được tạo ra thì để đẩy lên Github Repo chỉ cần chạy ```git push```  

## **5. Thiết lập luồng tự động hóa CI/CD vói Jenkins**
### a. Thiết lập Jenkins ở local  
Jenkins có vai trò tự động hóa trong các bước Test-kiểm, Build và Deploy- Triển khai. Để chạy Jenkins, trước hết đảm bảo về đúng folder chứa Repo local: ```cd ~/<Path Repo Local>```  
Chạy compose-jenkins.yaml bằng câu lệnh: ```docker compose -f compose-jenkins.yaml up -d```  
Khi docker compose đang chạy, sẽ hiện ra Password như sau dùng để đăng nhập Jenkins, copy và lưu lại. Nếu không hiển thị như trong ảnh trên, vào Container Jenkins bằng command sau: ```docker logs jenkins```  để thấy được Password.

<img width="942" height="294" alt="Image" src="https://github.com/user-attachments/assets/e7c59994-f456-45a3-8ce3-f5c76e4811cf" />  

Tiếp theo truy cập vào Jenkins bằng cách vào http://localhost:8081 và nhập Password ban nãy xong chọn Continue.  

<img width="882" height="566" alt="Image" src="https://github.com/user-attachments/assets/10c339e0-48f0-462d-a9e1-04bb5399ab22" />  

Tiếp theo chọn Install Suggested Plugin ( Sử dụng hệ điều hành Ubuntu sẽ đỡ dính fail cài đặt hơn là Windown ) và chờ cài đặt hoàn tất.    

<img width="882" height="566" alt="Image" src="https://github.com/user-attachments/assets/d7265985-f2f1-406e-83d5-6c42744615b9" />  

Sau khi cài đặt các Plugin đề xuất xong, Popup đăng ký tên và password hiện lên, chọn Skip as admin.  

<img width="892" height="576" alt="Image" src="https://github.com/user-attachments/assets/02ced131-6847-4297-9fab-af60dd94ed83" />  

Xong chọn Save and Finish --> Start using Jenkins.  

<img width="882" height="332" alt="Image" src="https://github.com/user-attachments/assets/3ef433bf-52c8-4368-b094-3f6b1a8f897a" />   

Đăng nhập Jenkins thành công với tên tài khoản là admin, password đã được lưu. 

<img width="1289" height="558" alt="Image" src="https://github.com/user-attachments/assets/e0b9eb2c-c083-4ac0-9d20-448c1eca6af6" />  

Vào Manage Jenkins --> Plugin --> Availabale Plugins và search rồi cài đặt các Plugin cần thiết như:  
* Docker
* Docker Pipeline
* Docker Slaves
* Kubenetes
* Kubenetes CLI
* Kubenetes Credential

<img width="1271" height="421" alt="Image" src="https://github.com/user-attachments/assets/bf144381-0475-4a59-94a2-15eebd990bd7" />  
<img width="931" height="406" alt="Image" src="https://github.com/user-attachments/assets/734fa365-3b66-4b4c-8a2f-dac1a4b1b5cd" />  

### b. Kết nối Github Repo với Jenkins:  
**Trước hết cần kết nối Github Repo với Jenkins để mỗi lần Github Repo được đẩy Commit mới hoặc tạo Branch (nhánh) mới thì Jenkins có thể nhận biết được và triển khai luồng CI/CD. Chúng ta sử dụng công cụ Ngrok.  
Truy cập page https://dashboard.ngrok.com/ và đăng nhập (tạo tài khoản nếu chưa có). Sau đó vào "Your Authtoken", chúng ta sẽ thấy token authen và copy đoạn mã token này.   

<img width="894" height="439" alt="Image" src="https://github.com/user-attachments/assets/2674bf58-6d92-496a-8360-035b2ef19c67" />  
<img width="692" height="167" alt="Image" src="https://github.com/user-attachments/assets/f2ff36a0-66a7-403f-8520-3a5760419540" />  

Bật Terminal của Vs code và chạy command: ```ngrok config add-authtoken <AUTHTOKEN lúc nãy>```  
Tiếp theo chạy: ```ngrok http 8081``` ( 8081 là Port của Jenkins )
Xong khu vực Terminal sẽ hiển thị giao diện như sau:  

<img width="818" height="319" alt="Image" src="https://github.com/user-attachments/assets/9ef74fc9-90ff-409d-92f1-bc352edc9736" />

Đoạn khoanh đỏ trong hình chính là địa chỉ web kết nối trực tiếp ( Tạo thành 1 "đường hầm" ) với Jenkins ở máy local, thay vì truy cập vào localhost:8081, chúng ta có thể truy cập Jenkins thông qua địa chỉ web này. Tiến hành copy địa chỉ web trên.  
Trở lại Github Repo, 



