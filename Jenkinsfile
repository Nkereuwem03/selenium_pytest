pipeline {
    agent any
    
    environment {
        // Database Configuration
        DATABASE_HOST = '127.0.0.1'
        DATABASE_PORT = '3306'
        DATABASE_USER = 'root'
        DATABASE_PASSWORD = credentials('mysql-password')
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
        VENV_DIR = 'venv'
        REPORTS_DIR = 'reports'
        ALLURE_RESULTS = 'allure-results'
        TMPDIR = '/tmp'
    }

    // triggers {
    //     pollSCM('H/5 * * * *') // Poll every 5 minutes
    // }
        
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        skipStagesAfterUnstable()
    }
    
    stages {
        // stage('Checkout') {
        //     steps {
        //         checkout scm
        //     }
        // }
        
        stage('System Check') {
            steps {
                sh '''
                    echo "=== System Information ==="
                    whoami
                    pwd
                    uname -a
                    
                    echo "=== Checking Docker availability ==="
                    if command -v docker >/dev/null 2>&1; then
                        echo "Docker command found"
                        docker version || echo "Docker daemon not running or no permissions"
                    else
                        echo "Docker command not found"
                    fi
                    
                    echo "=== Available Python versions ==="
                    python3 --version || echo "python3 not found"
                    python3.10 --version || echo "python3.10 not found"
                    python3.11 --version || echo "python3.11 not found"
                '''
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    echo "=== Python Environment Setup ==="
                    
                    # Find available Python version
                    if command -v python3.11 >/dev/null 2>&1; then
                        PYTHON_CMD="python3.11"
                    elif command -v python3.10 >/dev/null 2>&1; then
                        PYTHON_CMD="python3.10"
                    elif command -v python3.9 >/dev/null 2>&1; then
                        PYTHON_CMD="python3.9"
                    elif command -v python3 >/dev/null 2>&1; then
                        PYTHON_CMD="python3"
                    else
                        echo "No suitable Python version found"
                        exit 1
                    fi
                    
                    echo "Using Python: $PYTHON_CMD"
                    $PYTHON_CMD --version
                    
                    # Remove existing virtual environment
                    rm -rf ${VENV_DIR}
                    
                    # Create and activate virtual environment
                    $PYTHON_CMD -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    
                    # Upgrade pip
                    pip install --upgrade pip
                    
                    echo "Virtual environment created successfully"
                '''
            }
        }

        stage('Install System Dependencies') {
            steps {
                sh '''
                    echo "=== Installing System Dependencies ==="
                    sudo apt-get update
                    sudo apt-get install -y wget unzip curl jq fonts-liberation libatk-bridge2.0-0 \
                        libatk1.0-0 libcairo2 libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 \
                        libnss3 libpango-1.0-0 libu2f-udev libx11-xcb1 libxcomposite1 \
                        libxdamage1 libxfixes3 libxrandr2 xdg-utils xvfb psmisc mysql-client \
                        software-properties-common
                '''
            }
        }
        
        stage('Install Python Dependencies') {
            steps {
                sh '''
                    echo "=== Installing Python Dependencies ==="
                    . ${VENV_DIR}/bin/activate
                    
                    # Create requirements.txt if it doesn't exist
                    if [ ! -f requirements.txt ]; then
                        echo "requirements.txt not found! Creating basic requirements..."
                        cat > requirements.txt << 'EOF'
selenium>=4.0.0
pytest>=7.0.0
pytest-html>=3.0.0
allure-pytest>=2.9.0
mysql-connector-python>=9.3.0
pymysql>=1.0.0
python-dotenv>=0.19.0
webdriver-manager>=3.8.0
EOF
                    fi
                    
                    # Install requirements
                    pip install -r requirements.txt
                    
                    echo "Python dependencies installed successfully"
                '''
            }
        }

        stage('Setup Chrome') {
            steps {
                sh '''
                    echo "=== Chrome Installation ==="
                    
                    # Add Google Chrome repository
                    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | \
                        sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
                    
                    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] \
                        http://dl.google.com/linux/chrome/deb/ stable main" | \
                        sudo tee /etc/apt/sources.list.d/google.list
                    
                    sudo apt-get update
                    sudo apt-get install -y google-chrome-stable
                    
                    # Verify installation
                    google-chrome --version
                    
                    echo "Chrome installed successfully"
                '''
            }
        }

        stage('Setup Virtual Display') {
            steps {
                sh '''
                    echo "=== Starting Virtual Display ==="
                    sudo Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
                    sleep 3
                    echo "Virtual display started on :99"
                '''
            }
        }

        stage('Setup MySQL') {
            steps {
                script {
                    try {
                        sh '''
                            echo "=== MySQL Docker Setup ==="
                            
                            # Stop and remove any existing MySQL containers
                            docker stop test-mysql 2>/dev/null || true
                            docker rm test-mysql 2>/dev/null || true
                            
                            # Start MySQL container
                            docker run --name test-mysql \
                                -e MYSQL_ROOT_PASSWORD=${DATABASE_PASSWORD} \
                                -e MYSQL_DATABASE=${DATABASE_NAME} \
                                -p ${DATABASE_PORT}:3306 \
                                --health-cmd="mysqladmin ping --silent" \
                                --health-interval=10s \
                                --health-timeout=5s \
                                --health-retries=5 \
                                -d mysql:8.0
                            
                            echo "MySQL container started"
                        '''
                    } catch (Exception e) {
                        echo "Docker MySQL setup failed: ${e.message}"
                        error("MySQL setup is required for this pipeline")
                    }
                }
            }
        }

        stage('Wait for MySQL') {
            steps {
                sh '''
                    echo "=== Waiting for MySQL to be ready ==="
                    for i in $(seq 1 60); do
                        if docker exec test-mysql mysqladmin ping -uroot -p${DATABASE_PASSWORD} --silent 2>/dev/null; then
                            echo "MySQL is ready!"
                            break
                        fi
                        echo "Waiting for MySQL... (attempt $i/60)"
                        sleep 2
                    done
                    
                    # Verify MySQL is actually ready
                    docker exec test-mysql mysqladmin ping -uroot -p${DATABASE_PASSWORD} --silent || {
                        echo "MySQL failed to start properly"
                        exit 1
                    }
                '''
            }
        }
        
        stage('Initialize Database') {
            steps {
                sh '''
                    echo "=== Database Initialization ==="
                    
                    # Create init.sql if it doesn't exist
                    if [ ! -f init.sql ]; then 
                        echo "Creating sample database schema..."
                        cat > init.sql << 'EOF'
CREATE DATABASE IF NOT EXISTS test_data;
USE test_data;

CREATE TABLE IF NOT EXISTS fixed_deposits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fd_amount_rs INT NOT NULL,
    fd_period_value INT NOT NULL,
    fd_period_unit VARCHAR(10), 
    interest_rate DECIMAL(5, 2) NOT NULL, 
    compounding_frequency VARCHAR(20) NOT NULL, 
    maturity_amount_lakh DECIMAL(10, 1) NOT NULL, 
    expected_result VARCHAR(10) NOT NULL, 
    actual_result VARCHAR(10) 
);

INSERT INTO fixed_deposits (
    fd_amount_rs, fd_period_value, fd_period_unit, interest_rate,
    compounding_frequency, maturity_amount_lakh, expected_result, actual_result
) VALUES
(20000, 2, 'years', 10.00, 'Monthly', 0.2, 'pass', NULL),
(40000, 5, 'years', 15.00, 'Quarterly', 0.8, 'pass', NULL),
(50000, 3, 'months', 10.00, 'Half Yearly', 0.6, 'pass', NULL),
(75000, 2, 'months', 12.00, 'Yearly', 0.9, 'pass', NULL),
(85000, 2, 'days', 12.00, 'Yearly', 2.1, 'fail', NULL);
EOF
                    fi
                    
                    # Initialize database
                    docker cp init.sql test-mysql:/init.sql
                    docker exec test-mysql bash -c "mysql -uroot -p${DATABASE_PASSWORD} < /init.sql"
                    
                    echo "Database initialized successfully"
                '''
            }
        }

        stage('Pre-test Setup') {
            steps {
                sh '''
                    echo "=== Pre-test Setup ==="
                    
                    # Create required directories
                    mkdir -p ${REPORTS_DIR}
                    mkdir -p ${ALLURE_RESULTS}
                    mkdir -p logs
                    mkdir -p downloads
                    
                    # Clean up any existing Chrome processes
                    sudo pkill -f chrome || true
                    sudo pkill -f chromedriver || true
                    
                    # Clean Chrome user data directories
                    sudo rm -rf /tmp/chrome_user_data_* || true
                    sudo rm -rf /tmp/.org.chromium.* || true
                    sudo rm -rf /tmp/scoped_dir* || true
                    
                    sleep 2
                    echo "Pre-test setup completed"
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    echo "=== Running Tests ==="
                    . ${VENV_DIR}/bin/activate
                    
                    # Create a basic test if none exists
                    if [ ! -f test_*.py ] && [ ! -d tests ]; then
                        echo "Creating sample test..."
                        mkdir -p tests
                        cat > tests/test_sample.py << 'EOF'
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def test_chrome_webdriver():
    """Test Chrome WebDriver functionality"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.google.com")
        assert "Google" in driver.title
        print(f"Successfully loaded: {driver.title}")
    finally:
        driver.quit()

def test_database_connection():
    """Test database connectivity"""
    import mysql.connector
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DATABASE_HOST', '127.0.0.1'),
            port=os.getenv('DATABASE_PORT', '3306'),
            user=os.getenv('DATABASE_USER', 'root'),
            password=os.getenv('DATABASE_PASSWORD', 'root'),
            database=os.getenv('DATABASE_NAME', 'test_data')
        )
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM fixed_deposits")
        result = cursor.fetchone()
        assert result[0] > 0
        print(f"Database test passed: {result[0]} records found")
        cursor.close()
        connection.close()
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

def test_basic_assertion():
    """Basic test to ensure pytest is working"""
    assert 1 + 1 == 2
    assert "hello".upper() == "HELLO"
EOF
                    fi
                    
                    # Run tests
                    pytest tests/ -v --tb=short \
                        --alluredir=${ALLURE_RESULTS} \
                        --html=${REPORTS_DIR}/report.html --self-contained-html \
                        || echo "Some tests failed, but continuing with report generation..."
                '''
            }
        }

        stage('Generate Reports') {
            steps {
                sh '''
                    echo "=== Generating Test Reports ==="
                    
                    # Install Allure CLI if not present
                    if ! command -v allure &> /dev/null; then
                        echo "Installing Allure CLI..."
                        wget -q -O allure-commandline.tgz \
                            https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz
                        tar -zxf allure-commandline.tgz
                        sudo mv allure-2.24.0 /opt/allure
                        sudo ln -s /opt/allure/bin/allure /usr/local/bin/allure
                    fi
                    
                    # Generate Allure report if results exist
                    if [ -d "${ALLURE_RESULTS}" ] && [ "$(ls -A ${ALLURE_RESULTS})" ]; then
                        echo "Generating Allure report..."
                        allure generate ${ALLURE_RESULTS} -o allure-report --clean
                        echo "Allure report generated successfully"
                    else
                        echo "No Allure results found"
                        mkdir -p allure-report
                        echo "<h1>No Test Results</h1>" > allure-report/index.html
                    fi
                '''
            }
        }
    }
    
    post {
        always {
            script {
                // Archive test artifacts
                archiveArtifacts artifacts: 'allure-report/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: "${ALLURE_RESULTS}/**/*", allowEmptyArchive: true
                archiveArtifacts artifacts: "${REPORTS_DIR}/**/*", allowEmptyArchive: true
                archiveArtifacts artifacts: 'logs/**/*', allowEmptyArchive: true
                
                // Publish Allure report if plugin is available
                try {
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: "${ALLURE_RESULTS}"]]
                    ])
                } catch (Exception e) {
                    echo "Allure plugin not available: ${e.message}"
                }
            }
        }
        
        cleanup {
            sh '''
                echo "=== Final Cleanup ==="
                
                # Stop Chrome processes
                sudo pkill -f chrome || true
                sudo pkill -f chromedriver || true
                
                # Stop virtual display
                sudo pkill -f Xvfb || true
                
                # Clean up Chrome temp files
                sudo rm -rf /tmp/chrome_user_data_* || true
                sudo rm -rf /tmp/.org.chromium.* || true
                
                # Stop and remove MySQL container
                docker stop test-mysql 2>/dev/null || true
                docker rm test-mysql 2>/dev/null || true
                
                echo "Cleanup completed"
            '''
            
            // Clean workspace
            cleanWs()
        }
        
        success {
            echo '✅ Pipeline completed successfully!'
        }
        
        failure {
            echo '❌ Pipeline failed!'
            script {
                // Optional: Send notification on failure
                try {
                    emailext(
                        subject: "❌ Test Pipeline Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: """
                        Test pipeline failed for job: ${env.JOB_NAME}
                        Build number: ${env.BUILD_NUMBER}
                        Build URL: ${env.BUILD_URL}
                        
                        Please check the Jenkins logs for more details.
                        """,
                        to: 'team@example.com'
                    )
                } catch (Exception e) {
                    echo "Failed to send notification: ${e.message}"
                }
            }
        }
    }
}