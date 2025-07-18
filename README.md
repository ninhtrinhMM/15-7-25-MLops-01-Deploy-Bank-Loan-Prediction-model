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

## **4. Khởi tạo Jaeger Tracing:**  

Vì Jaeger là 1 công cụ theo dõi Trace được định nghĩa sẵn trong file ML-app.py (file main) nên chúng ta cần triển khai Jaegar trước có thể theo dõi Trace ngay khi app khởi động.  

Trước hết đảm bảo vào đúng trong Cluster được tạo ở bước trước bằng command sau:  

```gcloud container clusters get-credentials <Tên Cluster> --zone <Nơi đặt máy> --project <Tên Project>```  

Xong chạy file Jaegar-deployment.yaml bằng command:  

```kubectl apply -f Jaegar-deployment.yaml```  

Chạy xong, kiểm tra bằng command: ```kubectl get pod``` và ```kubectl get svc```  

<img width="1177" height="383" alt="Image" src="https://github.com/user-attachments/assets/4d48cf68-7ee4-44ae-8eca-5dbad6c0b221" />  

Để truy cập được vào Jaeger, sử dụng port-forward: ```kubectl port-forward svc/jaeger 16686:16686``` sau đó truy cập vào localhost:16686, nếu thấy giao diện Jaeger hiện lên tức thành công.  

<img width="960" height="524" alt="Image" src="https://github.com/user-attachments/assets/1eb5169d-8581-4bbe-94ef-a552b6af305f" />  

**NOTE: Tất cả các thao tác mới với Terminal phả làm trên Terminal mới. Terminal hiện tại là để chứa Log của Jaeger.** 

## **5. Khởi tạo Github Repo**  
Truy cập github.com, tạo tài khoản nếu chưa có và khởi tạo 1 Repository ( Kho lưu trữ các file ) mới, điền Repository Name và để ở chế độ **PUBLIC**.   

<img width="327" height="148" alt="Image" src="https://github.com/user-attachments/assets/8c25622d-d712-48f0-ab1d-3edbbfc86ed6" />  

Trở về VS Code, chạy lệnh: ```git add .``` để add tất cả các Folder hiện tại vào Stageing Area.  
Chạy lệnh: ```git commit -m <Tên commit>``` để tạo 1 bản ghi Commit mới.  
Chạy lệnh: ```git remote add origin <Link Github Repo bạn vừa mới tạo>``` để tạo 1 remote tên origin nhằm liên kểt Repo dưới Local (toàn bộ file và folder đang được mở bằng VS Code) với Github Repo mới của bạn. 
Đồng hóa ( Synchronize ) giữa Repo dưới Local với Github repo: ```git push -u origin main```  
Từ giờ khi có 1 Commit mới được tạo ra thì để đẩy lên Github Repo chỉ cần chạy ```git push```  

## **6 Thiết lập Jenkins**  

### a. Khởi tạo Jenkins ở local  

Jenkins có vai trò tự động hóa trong các bước Test-kiểm, Build và Deploy- Triển khai. Để chạy Jenkins, nhập command vào Terminal:  

```docker run -d -p 8080:8080 -p 50000:50000 \-u root \-v jenkins_home:/var/jenkins_home \-v /var/run/docker.sock:/var/run/docker.sock \-v $(which docker):/usr/bin/docker \--name jenkins-new \jenkins/jenkins:lts-jdk17```

Trong quá trình khởi tạo Container, sẽ hiện ra Password như sau dùng để đăng nhập Jenkins, copy và lưu lại. Nếu không hiển thị như trong ảnh trên, vào Container Jenkins bằng command sau: ```docker logs jenkins-new```  để thấy được Password.

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

Trước hết cần kết nối Github Repo với Jenkins để mỗi lần Github Repo được đẩy Commit mới hoặc tạo Branch (nhánh) mới thì Jenkins có thể nhận biết được và triển khai luồng CI/CD. Chúng ta sử dụng Webhook API.  
Trước hết sử dụng công cụ Ngrok để tạo 1 đường hầm Pubic cho Jenkins dưới Local. Truy cập page https://dashboard.ngrok.com/ và đăng nhập (tạo tài khoản nếu chưa có). Sau đó vào "Your Authtoken", chúng ta sẽ thấy token authen và copy đoạn mã token này.   

<img width="894" height="439" alt="Image" src="https://github.com/user-attachments/assets/2674bf58-6d92-496a-8360-035b2ef19c67" />  
<img width="692" height="167" alt="Image" src="https://github.com/user-attachments/assets/f2ff36a0-66a7-403f-8520-3a5760419540" />  

Bật Terminal của Vs code và chạy command: ```ngrok config add-authtoken <AUTHTOKEN lúc nãy>```  
Tiếp theo chạy: ```ngrok http 8081``` ( 8081 là Port của Jenkins )
Xong khu vực Terminal sẽ hiển thị giao diện như sau:  

<img width="818" height="319" alt="Image" src="https://github.com/user-attachments/assets/9ef74fc9-90ff-409d-92f1-bc352edc9736" />

Đoạn khoanh đỏ trong hình chính là địa chỉ web kết nối trực tiếp ( Tạo thành 1 "đường hầm" ) với Jenkins ở máy local, thay vì truy cập vào localhost:8081, chúng ta có thể truy cập Jenkins thông qua địa chỉ web này. Tiến hành copy địa chỉ web trên.  
Trở lại Github Repo, chọn Setting  

<img width="838" height="143" alt="Image" src="https://github.com/user-attachments/assets/d2ad92ba-e844-42de-9923-96dbab305f42" />  

Chọn Webhook --> Add Webhook  

<img width="1059" height="563" alt="Image" src="https://github.com/user-attachments/assets/2fa0e13e-911c-475b-b3f4-fa9ef0953b0b" />  

Giao diện Add Webhook hiện ra, phần Payload URL* điền link địa chỉ web lúc nãy kèm theo đuôi "/github-webhook/" để Jenkins nhận biết Webhook API. Phần Content Type* để Application Json.  

<img width="990" height="439" alt="Image" src="https://github.com/user-attachments/assets/70424728-2fb1-4167-a6e5-0c9e44ada9cb" />

Phần Which events would you like to trigger this webhook? chọn "Let me select individual events." và tích chọn Push và Pull request để Jenkins nhận biết 2 dạng sự kiện thay đổi này từ Github. Xong kéo xuống chọn "Add Webhook"  

<img width="609" height="397" alt="Image" src="https://github.com/user-attachments/assets/ce9cf452-736c-4ee0-8abc-5a23f380489a" />  

Hoàn thành Add Webhook API của Jenkins cho Github. Mở 1 Terminal mới ở VS Code, thử nghiệm tạo 1 commit mới dưới Repo Local và đẩy commit đó lên Github Repo. Nếu thấy tích xanh nghĩa là Webhook API đã hoạt động tốt.  

<img width="1000" height="402" alt="Image" src="https://github.com/user-attachments/assets/042522c2-a6ac-4400-b0cd-cf41c644e7c2" />  

## **7. Tạo liên kết giữa Jenkins với các platform khác**  

### a. Kết nối Jenkins với Dockerhub:  
   
Đầu tiên lấy Dockerhub Access Token, truy cập https://hub.docker.com/, click vào biểu tượng tài khoản và chọn Account Setting --> Personal Access Token --> Generate New Token --> Điền tên và chọn ngày hết hạn --> Chọn "Generate"  

<img width="684" height="439" alt="Image" src="https://github.com/user-attachments/assets/510a84b4-6db1-4008-868e-7f4bd4d83fbc" />  

Đoạn mã khoanh đỏ chính là Dockerhub Access Token. Copy và lưu Dockerhub Access Token.  

<img width="591" height="529" alt="Image" src="https://github.com/user-attachments/assets/918fa120-da57-4810-aeda-0b4a37c12675" />   

Để Jenkins có thể truy cập vào Dockerhub thực hiện các tác vụ, chúng ta cần tạo 1 Credential ( *Credential là tấm thẻ để truy cập vào nền tảng khác* ) để Jenkins có thể truy cập vào Dockerhub.  
Truy cập vào localhost:8081, chọn Manage Jenkins --> Credential --> Click vào "system"  

<img width="856" height="320" alt="Image" src="https://github.com/user-attachments/assets/0b48619b-f67c-46c4-86e1-abebd9fffd8e" />  

Xong chọn tiếp "Global credentials (unrestricted)" --> Add Credentials  

<img width="1043" height="212" alt="Image" src="https://github.com/user-attachments/assets/1916705f-9912-4781-8ef6-10552e6385d8" />  
<img width="1201" height="227" alt="Image" src="https://github.com/user-attachments/assets/8f1f2e00-481d-4182-aa15-847c6df9a367" />  

Bảng New Credential hiện lên, lần lượt điền các thông tin như sau:  
1. Điền User name cho Credential này.  
2. Password chính là Dockerhub Access Token vừa nãy lưu.  
3. Điền ID cho Credential, ID này dùng để xác định chính xác Credential nào Jenkins sẽ sử dụng.  

<img width="1189" height="607" alt="Image" src="https://github.com/user-attachments/assets/a2b1767f-6c03-470f-80ff-d59935849c02" />  

XOng ấn "Create" để tạo Dockerhub Credential. Trở lại Manage Jenkins/Credential và thấy Credential hiện lên như trong hình dưới nghĩa là tạo thành công.  

<img width="1111" height="368" alt="Image" src="https://github.com/user-attachments/assets/2f5236d0-007a-4c72-ab9e-7d26195077d2" />  

### b. Kết nối Jenkins với GCP Cluster:  
Để Jenkins có thể truy cập vào chính xác cụm máy Cluster mà chúng ta tạo ở mục 3, trở về trang chủ Jenkins --> Manage Jenkins --> Clouds --> New Cloud. Sau đó điền tên cho Cloud và chọn type là Kubenetes xong nhấn "Create".  

<img width="896" height="353" alt="Image" src="https://github.com/user-attachments/assets/af5bac3e-d569-46f2-8d00-ec024cab129f" />  

Bảng New Cloud hiện lên, với các ô cần điền như **Kubenetes URL** và **Kubernetes server certificate key** và Credential cho Cloud.  

<img width="1067" height="444" alt="Image" src="https://github.com/user-attachments/assets/2f34d07a-594e-49fc-804b-bf2cf631d3d0" />   

   #### *b.1. Lấy Kubenetes URL:*  
Để lấy được Kubenetes URL của Cluster mà chúng ta tạo ở bước 3, chạy đoạn command sau:  

```gcloud container clusters describe <Tên Cluster> --zone=<Tên vùng> --format="value(endpoint)"```  

Kết quả hiện ra sẽ ở dưới dạng như 34.124.333.33 thì giá trị để điền vào ô Kubenetes URL sẽ là: ```https://34.124.333.33```  

   #### *b.2. Kubernetes server certificate key:*  

Chạy command sau:  

```gcloud container clusters describe <Tên Cluster> --zone=<Tên vùng> --format="value(masterAuth.clusterCaCertificate)"```  

Copy dãy Certificate và paste vào phần Kubernetes server certificate key.  

   #### *b.3. Tạo Credential cho Jenkins Cloud:*  
Để tạo Credential cho Jenkins Cloud kết nối tới Cluster, đầu tiên truy cập lại GCP https://console.cloud.google.com và chọn đúng project đang có Cluster.  
Tiến hành tạo Service Account (*Service Account dùng để truy cập vào các nền tảng khác như Kubenetes thay vì đăng nhập bằng tài khoản Google bình thường* ), vào IAM & Admin --> Service Accounts --> CREATE SERVICE ACCOUNT --> Đặt tên cho Service Account --> Done.  

<img width="1050" height="594" alt="Image" src="https://github.com/user-attachments/assets/5a33d119-fcb0-4bfe-b92d-38afa63dd736" />  
<img width="927" height="130" alt="Image" src="https://github.com/user-attachments/assets/85c6280d-8016-4a6c-ba3d-f5714c9bc3e4" />  
<img width="547" height="488" alt="Image" src="https://github.com/user-attachments/assets/70aff664-a4d6-4fc2-9383-3831727b4de6" />  

Tiếp theo chúng ta gán thêm quyền truy cập Kubenetes cho Service Account vừa tạo, vào IAM --> Grant Access  

<img width="816" height="295" alt="Image" src="https://github.com/user-attachments/assets/ddb3e6b7-ab2b-41a5-bd83-7876eff13eb5" />  

Bảng Grant Access hiện lên, điền các thông tin theo thứ tự sau:  
1. <tên service account>@<tên project>.iam.gserviceaccount.com  
2. Phần Assign Role chọn option Kubernetes Engine Admin.  
3. Thêm Assign Role chọn option Kubernetes Engine Cluster Admin. 

<img width="935" height="613" alt="Image" src="https://github.com/user-attachments/assets/0d7d62c2-35f0-4cf5-9ab9-16cd782b660f" />  

Xong nhấn Save để hoàn thành thêm quyền.  

Trở lại về Service Account vừa tạo, click vào Service Account đó và chuyển sang tab Key ở bên cạnh và chọn Add Key --> Create New Key --> Tích chọn Json --> nhấn Create và file Json sẽ được tải xuống.  

<img width="1203" height="540" alt="Image" src="https://github.com/user-attachments/assets/b56a43b4-b340-465a-aa48-c61544537447" />  

<img width="761" height="461" alt="Image" src="https://github.com/user-attachments/assets/9219ab02-554d-4bcd-a464-85bf65feb1b5" />  

Tiếp theo tiến hành lấy Access Token đại diện cho Servie Account, chạy command sau:  

```gcloud auth activate-service-account <tên service account>@<tên project>.iam.gserviceaccount.com --key-file=<Path chứa Json Key vừa tải>```  
```gcloud auth print-access-token```  
Đoạn Access Token sẽ được hiển thị như sau, Copy và lưu lại.  

<img width="1009" height="209" alt="Image" src="https://github.com/user-attachments/assets/0589cfc4-ffbb-4764-9b22-28ef334ec8fb" />  

Trở lại với Jenkins, kéo xuống phần Credential của giao diện New Cloud, Chọn Add --> Jenkins  

<img width="1141" height="340" alt="Image" src="https://github.com/user-attachments/assets/88bbaa9e-2267-4dd8-b3c7-266e46ebb58a" />  

GIao diện Add Credential hiện lên, điền các thông tin như sau: 
1. Để kind là Secret Text
2. Paste Access Token ban nãy vừa lưu lại.
3. Điền ID để quản lý.
Xong chọn Save để hoàn thành.

<img width="936" height="500" alt="Image" src="https://github.com/user-attachments/assets/e8b40924-a76a-4f38-82fb-ef19dce7895a" />  

Quay trở lại chỗ Credential và chọn đúng ID của Credential vừa tạo. Xong ấn "Test Connection" để xem đã kết nối được với Cluster chưa, nếu hiển thị như trong hình tức là đã kết nối thành công, xong nhấn "Save" để hoàn thành tạo Cloud kết nối Jenkins với Cluster. 

<img width="1112" height="195" alt="Image" src="https://github.com/user-attachments/assets/4c7a21e9-f15e-4a2c-a540-70935972ef90" />  

<img width="1221" height="259" alt="Image" src="https://github.com/user-attachments/assets/7535e086-2179-4eae-bf6e-f35edffd9035" />  

## **8. Khởi tạo luồng CI/CD Jenkins**  

### a. Lấy Github Access Token:  

Jenkins cần có Github Access Token để có thể trigger (nhận biết) vào từng Branch (nhánh) của Github để nhận biết Jenkinsfile và Dockerhub Access Token để truy cập vào Dockerhub. Trước hết lấy Github Access Token bằng cách click vào Avatar Github --> Setting --> Developer Settings

<img width="994" height="550" alt="Image" src="https://github.com/user-attachments/assets/16086200-a4e0-4e42-92b9-d76216115eaf" />  

Vào Personal Access Token --> Token Classic --> Generate new token --> Generate new token (Classic)  

<img width="1055" height="376" alt="Image" src="https://github.com/user-attachments/assets/ced75b73-7167-4182-b9b0-3ff77d91106c" />  
<img width="1039" height="358" alt="Image" src="https://github.com/user-attachments/assets/421a5b4e-f7c9-4e86-95f5-038be15d5b78" />  

Điền tên cho Github Access Token và chọn ngày hết hạn. Phần "Select Scope" có thể tích hết các Option.  

<img width="916" height="548" alt="Image" src="https://github.com/user-attachments/assets/05561388-82de-4963-9f94-e6be9dcb1b75" />  

Hoàn thành xong kéo xuống nhấn "Generate Token" để tạo Github Access Token. Giao diện chứa mã Github Access Token hiện lên. Tiến hành lưu mã Github Access Token ở nơi khác. Vì nếu mất không thể có lại được nữa.  

<img width="1010" height="444" alt="Image" src="https://github.com/user-attachments/assets/13852c0f-f9e8-4379-822e-d24b9443e881" />

### b. Jenkinsfile: 



























### c. Thiết lập luồng CI/CD:  

Trở vè trang chủ Jenkins, chọn New Item.  

<img width="1144" height="349" alt="Image" src="https://github.com/user-attachments/assets/2ca9d739-ebee-4085-a960-af5425bb23e7" />  

Đặt tên cho Pipeline và chọn Multibranch Pipeline để quét toàn bộ các branch trong GitHub repo, xong nhấn OK.  

<img width="898" height="550" alt="Image" src="https://github.com/user-attachments/assets/1d26b847-bbdf-4626-b194-1b54c217f18d" />  

Giao diện General hiện lên. Điền tên Display Name, đây sẽ là tên hiển thị của luồng CI/CD.  
Kéo xuống ở phần Branch Source chọn Github, để Jenkins có thể xét toàn bộ các nhánh của Github Repo.  

<img width="897" height="486" alt="Image" src="https://github.com/user-attachments/assets/4dc4d976-37b0-46d6-92b4-3a374aa059eb" />  

Lập tức Github Credential hiện lên, chọn Add --> Chọn đúng tên Pipeline setup ban đầu.  

<img width="930" height="472" alt="Image" src="https://github.com/user-attachments/assets/dedac827-6b70-48f1-978f-25a60eb66b13" />  

Bảng Add Credential hiện lên. Điền các thông tin lần lượt như sau: 
1. Điền User name.             
2. Điền Github Access Token vào.  
3. Điền ID để quản lý.

<img width="963" height="491" alt="Image" src="https://github.com/user-attachments/assets/de53b89d-49c4-450d-a9ae-4c222b94021f" />  

Hoàn thiện xong nhấn Add. Quay trở lại giao diện Github Credential chọn đúng ID Credential vừa tạo **(1)**. Ở mục Repository HTTPS URL dán link của Github Repo vào **(2)**. Xong ấn Validate để kiểm tra kết nối **(3)**. Hiển thị "Credential OK" nghĩa là kết nối giữa Jenkins và Github Repo đã thành công. Xong nhấn   

<img width="888" height="406" alt="Image" src="https://github.com/user-attachments/assets/db62c007-64c7-4b46-a188-48b1242a1db7" />  

Xong nhấn "Save" để hoàn thiện xây dựng luồng CI/CD. Ngay khi ấn Save xong Jenkins sẽ quyét toàn bộ Github Repo, ở nhánh nào nếu có file Jenkinsfile thì Jenkins sẽ thực hiện các Stage và Step ( các giai đoạn và các bước ) đúng như trong file Jenkinsfile đề ra.  
Như trong hình, Jenkins đã quét ra được 1 file Jenkinsfile ở nhánh Main trong Github Repo.  

<img width="682" height="524" alt="Image" src="https://github.com/user-attachments/assets/dc6eee33-77e1-4008-ad8e-d2da6754adcc" />  

Vì Github Repo và Jenkins đã được trigger với nhau thông qua Webhook API ( ngrok ) nên Jenkins luôn tự động xem xét tìm kiếm Jenkinsfile ở trên mọi nhánh của Github Repo mỗi khi có Commit dưới local đẩy lên. Vì thế luồng tự động CI/CD được triển khai luôn ngay sau khi Pipeline (đoạn New Item) được tạo ra.  
Để theo dõi quá trình Jenkins thực thi, click vào tên Pipeline --> main --> Click vào số "1" ( Số 1 là số lần Jenkins chạy, Muốn chạy lần nữa click vào Build Now )  

<img width="1314" height="257" alt="Image" src="https://github.com/user-attachments/assets/44fc635c-abdb-4230-b8cd-6a02309517fb" />  
<img width="996" height="227" alt="Image" src="https://github.com/user-attachments/assets/7e5b099c-c748-414e-9fb3-02393cb1274c" />
<img width="665" height="412" alt="Image" src="https://github.com/user-attachments/assets/8867427a-0845-4fa4-8d66-5dba1f2a5531" />

Sau khi ấn vào số "1" xong, chọn "Console Output" để xem quá trình chạy của Jenkins.  

<img width="962" height="572" alt="Image" src="https://github.com/user-attachments/assets/d48438df-c6e0-4cdd-866b-d22d023b6ba2" />  
