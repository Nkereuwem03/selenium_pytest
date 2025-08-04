pipeline {
    agent any
    
    environment {
        // Database Configuration
        DATABASE_HOST = '127.0.0.1'
        DATABASE_PORT = '3306'
        DATABASE_USER = 'appuser'
        DATABASE_NAME = 'test_data'
        
        // Application Environment
        ENVIRONMENT = 'testing'
        DEBUG = 'true'
        LOG_LEVEL = 'DEBUG'
        
        // Chrome Configuration
        DISPLAY = ':99'
        CHROME_NO_SANDBOX = '1'
        CHROME_DISABLE_GPU = '1'
        CHROME_HEADLESS = '1'
        
        // Directory Configuration
        REPORTS_DIR = 'reports'
        ALLURE_RESULTS = 'allure-results'
        LOGS_DIR = 'logs'
        TMPDIR = '/tmp'

        // Docker configuration
        IMAGE_NAME = 'selenium-pytest'
        IMAGE_TAG = "${BUILD_NUMBER}"
        DOCKERHUB_REPO = 'devopswithnkereuwem'
        
        // Ensure non-interactive shell for apt-get
        DEBIAN_FRONTEND = 'noninteractive'
        COMPOSE_FILE = 'docker-compose.yml'
    }
        
    options {
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20', daysToKeepStr: '30'))
        skipStagesAfterUnstable()
        retry(1)
        timestamps()
        ansiColor('xterm')
    } 
    
    stages {
        stage('Checkout') {
            steps {
                echo "=== CHECKOUT STAGE ==="
                script {
                    cleanWs()
                    checkout scm
                }
            }
        }

        stage('Prepare Environment') {
            steps {
                echo "=== PREPARE ENVIRONMENT STAGE ==="

                withCredentials([string(credentialsId: 'mysql-root-password', variable: 'ROOT_PASSWORD'), 
                    string(credentialsId: 'mysql-user-password', variable: 'USER_PASSWORD')]) {
                    script {
                        sh '''
                            mkdir -p ${REPORTS_DIR} ${ALLURE_RESULTS} ${LOGS_DIR}
                            chmod 755 ${REPORTS_DIR} ${ALLURE_RESULTS} ${LOGS_DIR}
                            
                            echo ">> Checking Docker Swarm status..."
                            if ! docker info | grep -q "Swarm: active"; then
                                echo ">> Swarm not active. Initializing..."
                                docker swarm init || echo ">> Swarm may already be active"
                            fi

                            echo ">> Checking and creating Docker secrets..."

                            if ! docker secret ls | grep -q mysql_root_password; then
                                echo "$ROOT_PASSWORD" | docker secret create mysql_root_password -
                                echo ">> Secret mysql_root_password created."
                            else
                                echo ">> Secret mysql_root_password already exists."
                            fi

                            if ! docker secret ls | grep -q mysql_user_password; then
                                echo "$USER_PASSWORD" | docker secret create mysql_user_password -
                                echo ">> Secret mysql_user_password created."
                            else
                                echo ">> Secret mysql_user_password already exists."
                            fi
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "=== BUILD DOCKER IMAGE STAGE ==="
                script {
                    try {
                        sh '''
                            echo "Building docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
                            docker build \
                                --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VCS_REF=${GIT_COMMIT} \
                                --build-arg BUILD_NUMBER=${BUILD_NUMBER} \
                                -t ${IMAGE_NAME}:${IMAGE_TAG} \
                                -t ${IMAGE_NAME}:latest \
                                .
                            
                            echo "Image build successful"
                            docker images | grep ${IMAGE_NAME}
                        '''
                    } catch (Exception e) {
                        error "Docker build failed: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'master'
                    branch 'develop'
                }
            }
            steps {
                echo "=== PUSH TO REGISTRY STAGE ==="
                withCredentials([usernamePassword(credentialsId: 'dockerhub-pat', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
                    script {
                        try {
                            sh '''
                                echo "Tagging images..."
                                docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_USER}/${DOCKERHUB_REPO}:${IMAGE_TAG}
                                docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_USER}/${DOCKERHUB_REPO}:latest
                                
                                echo "Logging into Docker Hub..."
                                echo $DOCKER_TOKEN | docker login -u $DOCKER_USER --password-stdin
                                
                                echo "Pushing images..."
                                docker push ${DOCKER_USER}/${DOCKERHUB_REPO}:${IMAGE_TAG}
                                docker push ${DOCKER_USER}/${DOCKERHUB_REPO}:latest
                                
                                echo "Image push successful"
                            '''
                        } catch (Exception e) {
                            error "Docker push failed: ${e.getMessage()}"
                        }
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo "=== RUNNING TESTS STAGE ==="
                withCredentials([string(credentialsId: 'mysql-password', variable: 'DATABASE_PASSWORD')]) {
                    script {
                        try {
                            sh '''
                                echo "Starting test environment..."
                                export DOCKER_USER=${DOCKER_USER}
                                export DOCKERHUB_REPO=${DOCKERHUB_REPO}
                                export BUILD_NUMBER=${BUILD_NUMBER}
                                
                                # Start services
                                docker-compose -f ${COMPOSE_FILE} up -d --build
                                
                                echo "Waiting for services to be ready..."
                                sleep 30
                                
                                echo "Running tests..."
                                docker-compose -f ${COMPOSE_FILE} exec -T app pytest \
                                    --maxfail=5 \
                                    --disable-warnings \
                                    -v \
                                    --tb=short \
                                    --html=reports/report.html \
                                    --self-contained-html \
                                    --alluredir=allure-results \
                                    --junitxml=reports/junit.xml \
                                    tests/
                                
                                echo "Generating Allure report..."
                                docker-compose -f ${COMPOSE_FILE} exec -T app allure generate allure-results -o allure-report --clean
                                
                                echo "Tests completed successfully"
                            '''
                        } catch (Exception e) {
                            currentBuild.result = 'UNSTABLE'
                            echo "Tests failed: ${e.getMessage()}"
                        }
                    }
                }
            }
        }

        stage('Collect Test Results') {
            steps {
                echo "=== COLLECTING TEST RESULTS STAGE ==="
                script {
                    sh '''
                        echo "Copying test results..."
                        docker-compose -f ${COMPOSE_FILE} cp app:/app/reports ./reports || true
                        docker-compose -f ${COMPOSE_FILE} cp app:/app/allure-results ./allure-results || true
                        docker-compose -f ${COMPOSE_FILE} cp app:/app/allure-report ./allure-report || true
                        docker-compose -f ${COMPOSE_FILE} cp app:/app/logs ./logs || true
                        
                        # Check if results exist
                        ls -la reports/ || echo "No reports directory"
                        ls -la allure-results/ || echo "No allure-results directory"
                        ls -la allure-report/ || echo "No allure-report directory"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo "=== POST-BUILD STAGE ==="
            script {
                // Stop and remove containers
                sh '''
                    echo "Stopping Docker Compose services..."
                    docker-compose -f ${COMPOSE_FILE} down -v --remove-orphans || true
                    
                    echo "Cleaning up Docker resources..."
                    docker container prune -f || true
                    docker image prune -f || true
                    docker volume prune -f || true
                    
                    # Remove secrets (optional, for testing)
                    # docker secret rm mysql_root_password mysql_user_password || true
                '''
                
                // Archive artifacts
                try {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/**/*", allowEmptyArchive: true, fingerprint: true
                    archiveArtifacts artifacts: "${ALLURE_RESULTS}/**/*", allowEmptyArchive: true
                    archiveArtifacts artifacts: "allure-report/**/*", allowEmptyArchive: true
                    archiveArtifacts artifacts: "${LOGS_DIR}/**/*", allowEmptyArchive: true
                } catch (Exception e) {
                    echo "Failed to archive artifacts: ${e.getMessage()}"
                }
                
                // Publish test results
                try {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "${REPORTS_DIR}",
                        reportFiles: 'report.html',
                        reportName: 'Pytest HTML Report'
                    ])
                } catch (Exception e) {
                    echo "Failed to publish HTML report: ${e.getMessage()}"
                }
                
                try {
                    publishTestResults testResultsPattern: "${REPORTS_DIR}/junit.xml"
                } catch (Exception e) {
                    echo "Failed to publish test results: ${e.getMessage()}"
                }
                
                // Publish Allure report
                try {
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: "${ALLURE_RESULTS}"]]
                    ])
                } catch (Exception e) {
                    echo "Allure plugin not available or failed: ${e.getMessage()}"
                }
            }
        }
        
        cleanup {
            echo "=== CLEANUP STAGE ==="
            cleanWs(
                cleanWhenAborted: true,
                cleanWhenFailure: true,
                cleanWhenNotBuilt: true,
                cleanWhenSuccess: true,
                cleanWhenUnstable: true,
                deleteDirs: true
            )
        }
        
        success {
            echo 'Pipeline completed successfully!'
            script {
                if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
                    echo "Main branch build succeeded - consider deployment"
                }
            }
        }
        
        failure {
            echo 'Pipeline failed!'
            script {
                echo "Build failed for branch: ${env.BRANCH_NAME}"
            }
        }
        
        unstable {
            echo 'Pipeline unstable - some tests failed!'
        }
    }
}