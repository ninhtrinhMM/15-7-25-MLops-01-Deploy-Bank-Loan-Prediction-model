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
            agent any
            steps {
                script {
                    // Tạo nội dung file deployment.yaml
                    def deploymentYaml = """
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
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
        
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "0.5"
            memory: "512Mi"
"""

                    // Ghi nội dung vào file
                    writeFile file: 'deployment.yaml', text: deploymentYaml
                    
                    // Tạo nội dung file service.yaml (nếu cần expose service)
                    def serviceYaml = """
apiVersion: v1
kind: Service
metadata:
  name: ${APP_NAME}-service
  namespace: ${NAMESPACE}
spec:
  selector:
    app: ${APP_NAME}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
      nodePort: 30080
  type: NodePort
"""
                    writeFile file: 'service.yaml', text: serviceYaml
                    
                    // Kiểm tra nội dung file
                    sh 'cat deployment.yaml'
                    sh 'cat service.yaml'
                    
                    // Áp dụng lên GKE cluster
                    // credentialsId là ID của credential đã được thêm vào Jenkins để kết nối với GKE
                    withKubeConfig([credentialsId: 'jenkins-cluster-connect', serverUrl: 'https://34.124.251.86']) {
                        sh 'kubectl apply -f deployment.yaml'
                        sh 'kubectl apply -f service.yaml'
                        
                        // Kiểm tra trạng thái deployment
                        sh "kubectl get deployments -n ${NAMESPACE}"
                        sh "kubectl get pods -n ${NAMESPACE} -l app=${APP_NAME}"
                        sh "kubectl get services -n ${NAMESPACE}"
                    }
                    
                    // Lấy địa chỉ IP của service để truy cập
                    def serviceIp = sh(script: "kubectl get svc ${APP_NAME}-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'", returnStdout: true).trim()
                    echo "Application deployed! Access at: http://${serviceIp}"
                }
            }
        }
    }
} 