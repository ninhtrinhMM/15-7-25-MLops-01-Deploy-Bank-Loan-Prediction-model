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
        stage('Test') {
            steps {
                script {
                    // Kiểm tra Docker có available không
                    def dockerAvailable = sh(script: 'command -v docker', returnStatus: true) == 0
                    
                    if (dockerAvailable) {
                        echo 'Using Docker for testing..'
                        docker.image('python:3.8').inside('-v $HOME/.cache/pip:/root/.cache/pip') {
                            echo 'Testing model correctness..'
                            sh 'pip install -r requirements.txt && pytest'
                        }
                    } else {
                        echo 'Docker not available, running tests locally..'
                        // Fallback: chạy test trực tiếp trên agent
                        sh '''
                            python3 -m venv test_env
                            source test_env/bin/activate
                            pip install -r requirements.txt
                            pytest
                        '''
                    }
                }
            }
        }
        
        stage('Build') {
            when {
                // Chỉ build khi có Docker available
                expression { 
                    return sh(script: 'command -v docker', returnStatus: true) == 0
                }
            }
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
            // Cleanup virtual environment nếu có
            sh 'rm -rf test_env || true'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}