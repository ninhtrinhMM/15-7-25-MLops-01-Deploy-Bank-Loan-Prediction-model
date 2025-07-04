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
            agent any  // THAY ĐỔI từ DOcker sang Any cho đỡ lấn cấn
            steps {
                echo 'Testing model correctness..'
                sh 'python -m pip install --user -r requirements.txt && pytest'
            }
        }
        
        stage('Build') {
            agent {
                docker {
                    image 'docker:dind'  // Sử dụng Docker-in-Docker
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
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
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}