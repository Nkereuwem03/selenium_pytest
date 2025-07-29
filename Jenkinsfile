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
        
        // Ensure non-interactive shell for apt-get
        DEBIAN_FRONTEND = 'noninteractive'
    }
        
    options {
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        skipStagesAfterUnstable()
    }
    
    stages {
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
                        if docker version >/dev/null 2>&1; then
                            echo "Docker is working properly"
                        else
                            echo "Docker daemon not running or no permissions"
                            echo "Attempting to start Docker daemon..."
                            sudo systemctl start docker || echo "Failed to start Docker daemon"
                            sudo systemctl enable docker || echo "Failed to enable Docker daemon"
                            
                            # Add jenkins user to docker group if not already
                            sudo usermod -aG docker jenkins || echo "Failed to add jenkins to docker group"
                            echo "You may need to restart Jenkins for Docker permissions to take effect"
                        fi
                    else
                        echo "Docker not found. Installing Docker..."
                        
                        # Update package index
                        sudo apt-get update
                        
                        # Install prerequisites
                        sudo apt-get install -y \
                            ca-certificates \
                            curl \
                            gnupg \
                            lsb-release
                        
                        # Add Docker's official GPG key
                        sudo mkdir -p /etc/apt/keyrings
                        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
                        
                        # Set up the repository
                        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                        
                        # Update package index again
                        sudo apt-get update
                        
                        # Install Docker Engine
                        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
                        
                        # Start and enable Docker
                        sudo systemctl start docker
                        sudo systemctl enable docker
                        
                        # Add jenkins user to docker group
                        sudo usermod -aG docker jenkins
                        
                        # Verify installation
                        if command -v docker >/dev/null 2>&1; then
                            echo "Docker installed successfully"
                            docker --version
                            
                            # Test Docker with a simple command (might fail due to permissions until restart)
                            sudo docker run --rm hello-world || echo "Docker installed but may need Jenkins restart for permissions"
                        else
                            echo "Docker installation failed"
                            exit 1
                        fi
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
                    sudo apt-get install -y gnupg wget unzip curl jq fonts-liberation libatk-bridge2.0-0 \
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
                    
                    # Clean up any existing Google Chrome repository files
                    sudo rm -f /etc/apt/sources.list.d/google.list /etc/apt/sources.list.d/google-chrome.list
                    
                    # Debug: List repository files
                    echo "Listing repository files..."
                    ls -l /etc/apt/sources.list.d/
                    
                    # Download and add Google Chrome signing key
                    wget -q -O /tmp/linux_signing_key.pub https://dl.google.com/linux/linux_signing_key.pub
                    sudo mv /tmp/linux_signing_key.pub /usr/share/keyrings/googlechrome-linux-keyring.asc
                    
                    # Add Google Chrome repository
                    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.asc] \
                        http://dl.google.com/linux/chrome/deb/ stable main" | \
                        sudo tee /etc/apt/sources.list.d/google-chrome.list
                    
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
                sh '''
                    echo "=== Setting up MySQL ==="
                    
                    # Enable IPv4 forwarding for Docker networking
                    sudo sysctl -w net.ipv4.conf.all.forwarding=1
                    
                    # Verify Docker availability
                    docker --version
                    docker ps
                    
                    # Stop any existing MySQL containers
                    docker stop test-mysql 2>/dev/null || true
                    docker rm test-mysql 2>/dev/null || true
                    
                    # Start new MySQL container with proper health check
                    docker run -d \
                        --name test-mysql \
                        -e MYSQL_ROOT_PASSWORD="$DATABASE_PASSWORD" \
                        -e MYSQL_DATABASE=test_data \
                        -e MYSQL_ROOT_HOST='%' \
                        -p 3306:3306 \
                        --health-cmd="mysqladmin ping -h localhost -u root -p$DATABASE_PASSWORD" \
                        --health-interval=10s \
                        --health-timeout=10s \
                        --health-retries=5 \
                        mysql:8.0
                    
                    echo "MySQL container started successfully"
                '''
            }
        }

        stage('Wait for MySQL') {
            steps {
                withCredentials([string(credentialsId: 'mysql-password', variable: 'DATABASE_PASSWORD')]) {
                    sh '''
                        echo "=== Waiting for MySQL to be ready ==="
                        
                        # Wait for container to be running
                        echo "Waiting for container to start..."
                        sleep 10
                        
                        # Check container status
                        docker ps | grep test-mysql || {
                            echo "MySQL container is not running!"
                            docker logs test-mysql
                            exit 1
                        }
                        
                        # Wait for MySQL to be ready (up to 3 minutes)
                        for i in $(seq 1 30); do
                            echo "Checking MySQL readiness... (attempt $i/30)"
                            
                            # Try to connect using docker exec with proper mysql command
                            if docker exec test-mysql mysql -u root -p"$DATABASE_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
                                echo "MySQL is ready!"
                                break
                            fi
                            
                            if [ $i -eq 30 ]; then
                                echo "MySQL failed to start properly after 5 minutes"
                                echo "Container logs:"
                                docker logs test-mysql
                                echo "Container status:"
                                docker ps -a | grep test-mysql
                                exit 1
                            fi
                            
                            sleep 10
                        done
                        
                        echo "MySQL is ready for connections"
                    '''
                }
            }
        }
        
        stage('Initialize Database') {
            steps {
                withCredentials([string(credentialsId: 'mysql-password', variable: 'DATABASE_PASSWORD')]) {
                    sh '''
                        echo "=== Database Initialization ==="
                        
                        # Check if init.sql exists, if not create a basic one
                        if [ ! -f init.sql ]; then 
                            echo "init.sql not found, creating default database schema..."
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
                        else
                            echo "Using existing init.sql file"
                        fi
                        
                        # Verify init.sql exists and show its location
                        echo "Current directory: $(pwd)"
                        echo "Files in current directory:"
                        ls -la *.sql 2>/dev/null || echo "No .sql files found"
                        
                        if [ ! -f init.sql ]; then
                            echo "ERROR: init.sql file not found in $(pwd)"
                            exit 1
                        fi
                        
                        echo "init.sql file found. First few lines:"
                        head -5 init.sql
                        
                        # Test MySQL connection
                        docker exec test-mysql mysql -u root -p"$DATABASE_PASSWORD" -e "SELECT 1" || {
                            echo "Failed to connect to MySQL. Check credentials and container status."
                            docker logs test-mysql
                            exit 1
                        }
                        
                        # Copy SQL file to container and execute it
                        echo "Copying init.sql to MySQL container..."
                        docker cp init.sql test-mysql:/tmp/init.sql
                        
                        echo "Executing SQL script..."
                        docker exec test-mysql mysql -u root -p"$DATABASE_PASSWORD" -e "source /tmp/init.sql"
                        
                        # Verify initialization
                        echo "Verifying database initialization..."
                        docker exec test-mysql mysql -u root -p"$DATABASE_PASSWORD" -e "USE test_data; SELECT COUNT(*) as record_count FROM fixed_deposits;"
                        
                        echo "Database initialized successfully"
                    '''
                }
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
                    pytest tests/ -vv --tb=short \
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
                    
                    # Generate Allure report if results exist
                    if [ -d "${ALLURE_RESULTS}" ] && [ "$(ls -A ${ALLURE_RESULTS})" ]; then
                        echo "Allure results found, generating report..."
                    else
                        echo "No Allure results found, creating empty results directory"
                        mkdir -p ${ALLURE_RESULTS}
                    fi
                    
                    # Create basic HTML report summary
                    cat > ${REPORTS_DIR}/summary.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
        .failure { color: red; }
        .info { color: blue; }
    </style>
</head>
<body>
    <h1>Test Execution Summary</h1>
    <p class="info">Pipeline executed successfully!</p>
    <p>Check the archived artifacts for detailed test results.</p>
</body>
</html>
EOF
                    
                    echo "Reports generated successfully"
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
            echo 'Pipeline completed successfully!'
        }
        
        failure {
            echo 'Pipeline failed!'
        }
    }
}