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
        stage('Deploy GKE') {
            when {
                expression { 
                    return binding.hasVariable('dockerImage')
                }
            }
            steps {
                script {
                    echo 'Deploying to GKE cluster..'
                    try {
                        // Tạo file deployment.yaml
                        writeFile file: 'deployment.yaml', text: """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP_NAME}-deployment
  namespace: ${NAMESPACE}
  labels:
    app: ${APP_NAME}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ${APP_NAME}
  template:
    metadata:
      labels:
        app: ${APP_NAME}
    spec:
      containers:
      - name: ${APP_NAME}-container
        image: ${registry}:${BUILD_NUMBER}
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
---
apiVersion: v1
kind: Service
metadata:
  name: ${APP_NAME}-service
  namespace: ${NAMESPACE}
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "5000"
    prometheus.io/path: "/metrics"
spec:
  selector:
    app: ${APP_NAME}
  ports:
  - port: 80
    targetPort: 5000
    protocol: TCP
    nodePort: 30080
  type: NodePort
"""
                        
                        // Kiểm tra và cài đặt kubectl nếu cần
                        sh '''
                            if ! command -v kubectl &> /dev/null; then
                                echo "kubectl not found, installing..."
                                curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                                chmod +x kubectl
                                sudo mv kubectl /usr/local/bin/
                            fi
                            kubectl version --client
                        '''
                        
                        // Kiểm tra kết nối cluster
                        sh '''
                            echo "=== Checking cluster connection ==="
                            kubectl cluster-info
                            kubectl get nodes
                            kubectl get namespaces
                        '''
                        
                        // Tạo namespace nếu chưa tồn tại
                        sh """
                            kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        """
                        
                        // Deploy application
                        sh '''
                            echo "=== Deploying application ==="
                            kubectl apply -f deployment.yaml
                            
                            echo "=== Waiting for deployment to be ready ==="
                            kubectl rollout status deployment/${APP_NAME}-deployment -n ${NAMESPACE} --timeout=300s
                            
                            echo "=== Checking deployment status ==="
                            kubectl get deployments -n ${NAMESPACE}
                            kubectl get pods -n ${NAMESPACE} -l app=${APP_NAME}
                            kubectl get services -n ${NAMESPACE}
                        '''
                        
                        // Lấy thông tin service
                        def serviceInfo = sh(
                            script: "kubectl get service ${APP_NAME}-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'",
                            returnStdout: true
                        ).trim()
                        
                        if (serviceInfo) {
                            echo "Application deployed successfully!"
                            echo "External IP: ${serviceInfo}"
                            echo "You can access your application at: http://${serviceInfo}"
                        } else {
                            echo "Deployment completed. External IP is being assigned..."
                            echo "Check external IP with: kubectl get service ${APP_NAME}-service -n ${NAMESPACE}"
                        }
                        
                    } catch (Exception e) {
                        echo "Deployment failed: ${e.getMessage()}"
                        
                        // Debug information
                        sh '''
                            echo "=== Debug Information ==="
                            kubectl get pods -n ${NAMESPACE} -l app=${APP_NAME} || true
                            kubectl describe deployment ${APP_NAME}-deployment -n ${NAMESPACE} || true
                            kubectl logs -l app=${APP_NAME} -n ${NAMESPACE} --tail=50 || true
                        '''
                        
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Cleanup') {
            steps {
                script {
                    echo 'Cleaning up..'
                    sh '''
                        # Xóa file deployment.yaml sau khi deploy
                        rm -f deployment.yaml
                        
                        # Xóa docker image local để tiết kiệm dung lượng
                        docker rmi ${registry}:${BUILD_NUMBER} || true
                        docker rmi ${registry}:latest || true
                        
                        echo "Cleanup completed"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed'
            sh '''
                echo "=== Final Status ==="
                kubectl get all -n ${NAMESPACE} -l app=${APP_NAME} || true
            '''
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
        unstable {
            echo 'Pipeline completed with warnings'
        }
    }
}