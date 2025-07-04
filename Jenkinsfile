pipeline {
    agent any  // Chạy pipeline trên bất kỳ máy chủ Jenkins nào có sẵn
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))  // Giữ tối đa 5 build log
        timestamps()  // Thêm timestamp vào log
    }
    
    environment {
        registry = 'ninhtrinhmm/loan-prediction-ml'  // Tên image Docker
        registryCredential = 'dockerhubninhtrinh'  // ID credentials DockerHub
    }
    
    stages {
        stage('Test') {
            agent {
                docker {
                    image 'python:3.8'  // Sử dụng container Python 3.8
                    args '-v $HOME/.cache/pip:/root/.cache/pip'  // Cache pip packages (tùy chọn)
                }
            }
            steps {
                echo 'Testing model correctness..'
                sh 'pip install -r requirements.txt && pytest'
            }
        }
        
        stage('Build') {
            agent any  // Có thể bỏ nếu muốn chạy trên cùng agent với stage trước
            steps {
                script {
                    echo 'Building image for deployment..'
                    dockerImage = docker.build registry + ":$BUILD_NUMBER"
                    
                    echo 'Pushing image to dockerhub..'
                    docker.withRegistry('', registryCredential) {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed - cleanup resources'
            // Có thể thêm bước cleanup ở đây
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}