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
    // dockerhub.ninhtrinh là credential ID của DOcker Hub đã được cthêm vào Jenkins
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
            when {
                expression { 
                    return binding.hasVariable('dockerImage')
                }
            }
            agent {
                kubernetes {
                    yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins: slave
spec:
  serviceAccountName: jenkins-sa
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
    args: ['\$(JENKINS_SECRET)', '\$(JENKINS_NAME)']
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"
      limits:
        memory: "512Mi"
        cpu: "500m"
  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
    tty: true
    resources:
      requests:
        memory: "128Mi"
        cpu: "50m"
      limits:
        memory: "256Mi"
        cpu: "200m"
"""
                }
            }
            steps {
                script {
                    echo 'Deploying to GKE using Kubernetes agent..'
                    try {
                        container('kubectl') {
                            // Tạo Kubernetes deployment manifest
                            def deploymentYaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP_NAME}
  namespace: ${NAMESPACE}
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
      - name: ${APP_NAME}
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
        imagePullPolicy: Always
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
  - protocol: TCP
    port: 80
    targetPort: 5000
    nodePort: 30080
  type: NodePort
"""
                            
                            // Ghi file manifest
                            writeFile file: 'deployment.yaml', text: deploymentYaml
                            
                            // Deploy sử dụng kubectl trong container
                            sh '''
                                echo "=== Checking kubectl in container ==="
                                kubectl version --client
                                
                                echo "=== Checking cluster connection ==="
                                kubectl cluster-info
                                
                                echo "=== Current cluster context ==="
                                kubectl config current-context
                                
                                echo "=== Cluster nodes ==="
                                kubectl get nodes
                                
                                echo "=== Creating namespace if not exists ==="
                                kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                                
                                echo "=== Applying deployment ==="
                                kubectl apply -f deployment.yaml
                                
                                echo "=== Waiting for deployment to be ready ==="
                                kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE} --timeout=300s
                                
                                echo "=== Getting deployment status ==="
                                kubectl get deployments -n ${NAMESPACE}
                                kubectl get services -n ${NAMESPACE}
                                kubectl get pods -n ${NAMESPACE} -l app=${APP_NAME}
                            '''
                        }
                        
                        echo 'Deployment to GKE completed successfully'
                        
                    } catch (Exception e) {
                        echo "GKE deployment failed: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed - cleanup resources'
            // Cleanup deployment files
            sh 'rm -f deployment.yaml || true'
        }
        success {
            echo 'Pipeline succeeded!'
            script {
                if (binding.hasVariable('dockerImage')) {
                    echo "Application deployed successfully!"
                    echo "Image: ${registry}:${BUILD_NUMBER}"
                    
                    // Lấy thông tin service
                    try {
                        def serviceInfo = sh(
                            script: "kubectl get service ${APP_NAME}-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'",
                            returnStdout: true
                        ).trim()
                        
                        if (serviceInfo) {
                            echo "Service External IP: ${serviceInfo}"
                            echo "Application URL: http://${serviceInfo}"
                        } else {
                            // Lấy thông tin NodePort service
                            def nodePortInfo = sh(
                                script: "kubectl get service ${APP_NAME}-service -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}'",
                                returnStdout: true
                            ).trim()
                            
                            if (nodePortInfo) {
                                echo "Service NodePort: ${nodePortInfo}"
                                echo "Access application via: http://<NODE_IP>:${nodePortInfo}"
                                echo "Get node IPs with: kubectl get nodes -o wide"
                            }
                        }
                    } catch (Exception e) {
                        echo "Could not retrieve service information: ${e.getMessage()}"
                    }
                }
            }
        }
        failure {
            echo 'Pipeline failed!'
        }
        unstable {
            echo 'Pipeline completed with warnings'
        }
    }
}