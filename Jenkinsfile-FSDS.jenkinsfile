pipeline {
    agent any  // Chạy pipeline trên bất kỳ máy chủ Jenkins nào có sẵn
}
options {
    buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))  // Chỉ giữ tối đa 5 build log hoặc 5 ngày (tùy điều kiện nào đến trước)
    timestamps()  // Thêm timestamp vào log để dễ theo dõi thời gian thực thi
}
environment {
    registry = 'ninhtrinhmm/loan-prediction-ml'  // Tên image Docker trên Docker Hub
    registryCredential = 'dockerhubninhtrinh'  // ID credentials (username/password DockerHub) đã lưu trong Jenkins
}

stage('Test') {
    agent {
        docker {
            image 'python:3.8'  // Stage này sẽ được thực hiện trong Container python 3.8
        }
    }
    steps {
        echo 'Testing model correctness..'
        sh 'pip install -r requirements.txt && pytest'  // Cài dependencies 
        // và chạy Pytest-Chạy các file test trong thư mục tests/
    }
}

stage('Build') {
    steps {
        script {
            echo 'Building image for deployment..'
            dockerImage = docker.build registry + ":$BUILD_NUMBER"  // Build image với tên là đoạn registry, tag là số build tự động của Jenkins
            // docker.build: Build image từ Dockerfile trong repo (nếu không có Dockerfile, sẽ báo lỗi)
            // $BUILD_NUMBER: Số thứ tự build tự động tăng của Jenkins (ví dụ: 42)

            echo 'Pushing image to dockerhub..'
            docker.withRegistry( '', registryCredential ) {
                dockerImage.push()  // Push image với tag $BUILD_NUMBER
                dockerImage.push('latest')  // Push thêm tag 'latest'
            }
        }
    }
}