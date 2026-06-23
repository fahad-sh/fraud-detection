pipeline {
    agent any

    environment {
        AWS_REGION       = 'us-east-1'
        AWS_ACCOUNT_ID   = '529496937706'
        ECR_REPO         = 'fraud-detection-app'
        IMAGE_TAG        = "v${BUILD_NUMBER}"
        ECR_URI          = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"

        S3_BUCKET        = 'fraud-detection-transactions-1782195986'
        S3_KEY           = 'transactions.json'
        DYNAMODB_TABLE   = 'fraud_results'
        SNS_TOPIC_ARN    = 'arn:aws:sns:us-east-1:529496937706:NegativeFeedbackAlert'
    }

    stages {

        stage('1. Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                git branch: 'main',
                    url: 'https://github.com/fahad-sh/fraud-detection.git',
                    credentialsId: 'github-credentials'
            }
        }

        stage('2. Test') {
            steps {
                echo 'Running basic Python checks...'
                sh '''
                    python3 -m py_compile app/main.py app/fraud_rules.py
                    echo "Python syntax check passed."
                '''
            }
        }

        stage('3. Build Image') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t ${ECR_REPO}:${IMAGE_TAG} ."
            }
        }

        stage('4. Push to ECR') {
            steps {
                echo 'Pushing image to ECR...'
                sh """
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}
                    docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}
                    docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URI}:latest
                    docker push ${ECR_URI}:${IMAGE_TAG}
                    docker push ${ECR_URI}:latest
                """
            }
        }

        stage('5. Deploy') {
            steps {
                echo 'Pulling fresh image and running the fraud detection app...'
                sh """
                    docker pull ${ECR_URI}:latest
                    docker rm -f fraud-detection-running || true
                    docker run --name fraud-detection-running --rm \\
                        -e S3_BUCKET=${S3_BUCKET} \\
                        -e S3_KEY=${S3_KEY} \\
                        -e DYNAMODB_TABLE=${DYNAMODB_TABLE} \\
                        -e SNS_TOPIC_ARN=${SNS_TOPIC_ARN} \\
                        -e AWS_REGION=${AWS_REGION} \\
                        ${ECR_URI}:latest
                """
            }
        }

        stage('6. Cleanup') {
            steps {
                echo 'Cleaning up dangling images...'
                sh '''
                    docker image prune -f
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the stage logs above.'
        }
    }
}
