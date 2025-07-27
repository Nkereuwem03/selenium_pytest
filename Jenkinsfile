pipeline {
    agent any

    environment {
        DATABASE_HOST = '127.0.0.1'
        DATABASE_PORT = '3306'
        DATABASE_USER = 'root'
        DATABASE_PASSWORD = 'root'
        DATABASE_NAME = 'test_data'
        ALLURE_RESULTS = 'allure-results'
        REPORTS_DIR = 'reports'
        VENV_DIR = 'venv'
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        ansiColor('xterm')
    }

    stages {
        stage('Prepare Environment') {
            steps {
                sh '''
                    echo "Setting up Python virtual environment..."
                    
                    # Remove any existing virtual environment
                    rm -rf ${VENV_DIR}
                    
                    # Create virtual environment
                    python3 -m venv ${VENV_DIR}
                    
                    # Activate virtual environment and upgrade pip
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    
                    # Install dependencies
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    else
                        echo "requirements.txt not found, installing common packages..."
                        pip install pytest selenium allure-pytest pytest-html
                    fi
                    
                    echo "Virtual environment setup complete"
                '''
            }
        }

        stage('Check Python') {
            steps {
                sh '''
                    echo "Checking Python and virtual environment..."
                    . ${VENV_DIR}/bin/activate
                    which python
                    python --version
                    which pip
                    pip --version
                    pip list
                '''
            }
        }

        stage('Start MySQL') {
            steps {
                sh '''
                    echo "Starting MySQL container..."
                    
                    # Stop and remove any existing container
                    docker stop test-mysql || true
                    docker rm test-mysql || true
                    
                    # Start new MySQL container
                    docker run --name test-mysql \
                        -e MYSQL_ROOT_PASSWORD=${DATABASE_PASSWORD} \
                        -e MYSQL_DATABASE=${DATABASE_NAME} \
                        -p ${DATABASE_PORT}:3306 \
                        -d mysql:latest

                    echo "Waiting for MySQL to be ready..."
                    for i in $(seq 1 30); do
                        if docker exec test-mysql mysqladmin ping -uroot -p${DATABASE_PASSWORD} --silent 2>/dev/null; then
                            echo "MySQL is ready!"
                            break
                        fi
                        echo "Waiting... (attempt $i/30)"
                        sleep 2
                    done

                    # Initialize database if init.sql exists
                    if [ -f init.sql ]; then
                        echo "Initializing database with init.sql..."
                        docker cp init.sql test-mysql:/init.sql
                        docker exec test-mysql bash -c "mysql -uroot -p${DATABASE_PASSWORD} ${DATABASE_NAME} < /init.sql"
                    else
                        echo "No init.sql found, skipping database initialization"
                    fi
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "Running tests..."
                    . ${VENV_DIR}/bin/activate
                    
                    # Create reports directory
                    mkdir -p ${REPORTS_DIR}
                    mkdir -p ${ALLURE_RESULTS}
                    
                    # Run pytest with proper error handling
                    pytest --maxfail=1 --disable-warnings \
                        --alluredir=${ALLURE_RESULTS} \
                        --html=${REPORTS_DIR}/report.html --self-contained-html \
                        || exit 1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${ALLURE_RESULTS}/**", allowEmptyArchive: true
                    archiveArtifacts artifacts: "${REPORTS_DIR}/report.html", allowEmptyArchive: true
                }
                failure {
                    mail to: 'team@example.com',
                         subject: "Test Failure: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                         body: "Tests failed. See Jenkins for details: ${env.BUILD_URL}"
                }
            }
        }

        stage('Publish Allure Report') {
            steps {
                script {
                    try {
                        allure includeProperties: false, 
                               jdk: '', 
                               results: [[path: "${ALLURE_RESULTS}"]]
                    } catch (Exception e) {
                        echo "Allure report generation failed: ${e.getMessage()}"
                        echo "This might be due to missing Allure plugin or no test results"
                    }
                }
            }
        }
    }

    post {
        always {
            sh '''
                # Cleanup Docker container
                docker stop test-mysql || true
                docker rm test-mysql || true
            '''
            cleanWs()
        }
        success {
            echo 'Build and tests succeeded!'
        }
        failure {
            echo 'Build or tests failed!'
        }
    }
}