pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'museum_ai_chatbot'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                // Jenkins handles this automatically if configured with SCM
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image ${DOCKER_IMAGE}..."
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }

        stage('Run Logic Tests') {
            steps {
                script {
                    echo 'Running internal bot logic verification...'
                    // Run the test script inside a temporary container
                    docker.image("${DOCKER_IMAGE}").inside {
                        sh 'python test_bot.py'
                    }
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                script {
                    echo 'Deploying application using Docker Compose...'
                    sh 'docker-compose up -d --build'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished.'
        }
        success {
            echo 'Build and Deployment successful!'
        }
        failure {
            echo 'Build or Deployment failed. Please check the logs.'
        }
    }
}
