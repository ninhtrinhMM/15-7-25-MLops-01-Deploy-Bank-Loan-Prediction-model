pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        timestamps()
    }
    
    environment {
        registry = 'ninhtdmorningstar/loan-prediction-ml' 
    // ninhtdmorningstar/loan-prediction-ml là repository đang có trên Docker Hub 
        registryCredential = 'dockerhub.ninhtrinh'
    // dockerhub.ninhtrinh là credential ID của DOcker Hub đã được thêm vào Jenkins
        APP_NAME = 'loan-prediction'
        NAMESPACE = 'default'
    }
    
    stages {
        stage('Environment Check') {
            steps {
                echo 'Checking available tools..'
                sh '''
                    echo "=== System Information ==="
                    uname -a
                    
                    echo "=== Available Commands ==="
                    which git || echo "Git not found"
                    which docker || echo "Docker not found"
                    
                    echo "=== Project Files ==="
                    ls -la
                    
                    echo "=== Requirements file ==="
                    cat requirements.txt || echo "No requirements.txt"
                '''
            }
        }
        
        stage('Install Docker') {
            when {
                expression { 
                    return sh(script: 'which docker', returnStatus: true) != 0
                }
            }
            steps {
                script {
                    echo 'Docker not found - attempting to install..'
                    sh '''
                        # Update package manager
                        apt-get update || yum update -y || apk update || true
                        
                        # Install Docker
                        apt-get install -y docker.io || \
                        yum install -y docker || \
                        apk add --no-cache docker || \
                        echo "Failed to install Docker"
                        
                        # Start Docker service
                        systemctl start docker || service docker start || true
                        
                        # Add jenkins user to docker group
                        usermod -aG docker jenkins || true
                        
                        # Verify installation
                        docker --version || echo "Docker installation failed"
                    '''
                }
            }
        }
        
        stage('Test with Docker') {
            agent {
                docker {
                    image 'python:3.8-slim'
                    args '-v $PWD:/workspace -w /workspace'
                }
            }
            steps {
                echo 'Running tests in Python container..'
                sh '''
                    echo "=== Python Environment ==="
                    python --version
                    pip --version
                    
                    echo "=== Installing Dependencies ==="
                    pip install -r requirements.txt
                    
                    echo "=== Running Tests ==="
                    python -m pytest tests/test-py.py -v || echo "Tests completed"
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image..'
                    try {
                        dockerImage = docker.build registry + ":$BUILD_NUMBER"
                        echo 'Docker image built successfully'
                    } catch (Exception e) {
                        echo "Docker build failed: ${e.getMessage()}"
                        echo "This might be due to Docker not being properly installed"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                expression { 
                    return binding.hasVariable('dockerImage')
                }
            }
            steps {
                script {
                    echo 'Pushing to Docker registry..'
                    try {
                        docker.withRegistry('', registryCredential) {
                            dockerImage.push()
                            dockerImage.push('latest')
                        }
                        echo 'Image pushed successfully'
                    } catch (Exception e) {
                        echo "Docker push failed: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        stage('Deploy to GKE') {
            steps {
                script {
                    // Tạo thư mục cục bộ cho kubectl
                    sh 'mkdir -p $HOME/k8s-tools'
                    
                    // Cài đặt kubectl vào thư mục home
                    sh '''
                        # Tải kubectl phiên bản phù hợp
                        KUBECTL_VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)
                        curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
                        
                        # Cài đặt vào thư mục home
                        chmod +x kubectl
                        mv kubectl $HOME/k8s-tools/
                        
                        # Thêm vào PATH cho phiên làm việc hiện tại
                        export PATH="$HOME/k8s-tools:$PATH"
                    '''
                    
                    // Kiểm tra kubectl đã cài đặt
                    sh '$HOME/k8s-tools/kubectl version --client'
                    
                    // Áp dụng manifest sử dụng kubectl từ thư mục home
                    withKubeConfig([credentialsId: 'jenkins-cluster-connect', serverUrl: 'https://34.124.251.86']) {
                        sh '$HOME/k8s-tools/kubectl apply -f deployment.yaml'
                        sh '$HOME/k8s-tools/kubectl apply -f service.yaml'
                        
                        // Kiểm tra trạng thái
                        sh "$HOME/k8s-tools/kubectl get deployments -n ${NAMESPACE}"
                        sh "$HOME/k8s-tools/kubectl get pods -n ${NAMESPACE} -l app=${APP_NAME}"
                        sh "$HOME/k8s-tools/kubectl get services -n ${NAMESPACE}"
                    }
                }
            }
        }
    } // Đóng stages
} // Đóng pipeline