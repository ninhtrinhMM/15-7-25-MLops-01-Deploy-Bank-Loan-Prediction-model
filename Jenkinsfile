pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        timestamps()
    }
    
    environment {
        registry = 'ninhtrinhmm/loan-prediction-ml'
        registryCredential = 'dockerhubninhtrinh'
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
                    which python3 || echo "Python3 not found"
                    which python || echo "Python not found"
                    which pip3 || echo "Pip3 not found"
                    which pip || echo "Pip not found"
                    
                    echo "=== Current Directory ==="
                    pwd
                    ls -la
                    
                    echo "=== Environment Variables ==="
                    env | grep -E "(PATH|JAVA|PYTHON)" || true
                '''
            }
        }
        
        stage('Test') {
            steps {
                script {
                    echo 'Starting test stage..'
                    
                    // Kiểm tra có file requirements.txt không
                    def hasRequirements = fileExists('requirements.txt')
                    
                    if (hasRequirements) {
                        echo 'Found requirements.txt'
                        sh 'cat requirements.txt'
                    } else {
                        echo 'No requirements.txt found, skipping dependency installation'
                    }
                    
                    // Kiểm tra có file test không
                    def hasTests = fileExists('test_*.py') || fileExists('tests/') || fileExists('*test*.py')
                    
                    if (hasTests) {
                        echo 'Found test files'
                        sh 'find . -name "*test*.py" -o -name "test_*.py" | head -10'
                    } else {
                        echo 'No test files found'
                    }
                    
                    // Tạm thời skip test thực tế
                    echo 'Test stage completed (mocked for now)'
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    echo 'Starting build stage..'
                    
                    // Kiểm tra có Dockerfile không
                    def hasDockerfile = fileExists('Dockerfile')
                    
                    if (hasDockerfile) {
                        echo 'Found Dockerfile'
                        sh 'cat Dockerfile'
                    } else {
                        echo 'No Dockerfile found, skipping Docker build'
                    }
                    
                    // Tạm thời skip build thực tế
                    echo 'Build stage completed (mocked for now)'
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed - cleanup resources'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}