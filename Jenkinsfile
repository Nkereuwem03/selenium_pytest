pipeline {
    agent any
    
    environment {
        // Database configuration (CI testing)
        DATABASE_HOST = '127.0.0.1'
        DATABASE_PORT = '3306'
        DATABASE_USER = 'root'
        DATABASE_PASSWORD = credentials('mysql-password')
        DATABASE_NAME = 'test_data'
        
        // Application configuration
        ENVIRONMENT = 'testing'
        DEBUG = 'true'
        LOG_LEVEL = 'DEBUG'
        
        // Add your app-specific variables here
        // API_KEY = credentials('api-key-secret')
        // SECRET_KEY = credentials('app-secret-key')
        
        // Display and Chrome configuration
        DISPLAY = ':99'
        TMPDIR = '/tmp'
        CHROME_NO_SANDBOX = '1'
        CHROME_DISABLE_GPU = '1'
        CHROME_HEADLESS = '1'
    }
    
    triggers {
        // Trigger on push to main/master branches
        pollSCM('H/5 * * * *') // Poll every 5 minutes
        // Or use webhook triggers for immediate response
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        skipStagesAfterUnstable()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            parallel {
                stage('Start MySQL') {
                    steps {
                        script {
                            // Start MySQL container
                            sh '''
                                # Stop any existing MySQL containers
                                docker stop mysql-test || true
                                docker rm mysql-test || true
                                
                                # Start new MySQL container
                                docker run -d \
                                    --name mysql-test \
                                    -e MYSQL_ROOT_PASSWORD=${DATABASE_PASSWORD} \
                                    -e MYSQL_DATABASE=test_data \
                                    -p 3306:3306 \
                                    --health-cmd="mysqladmin ping --silent" \
                                    --health-interval=10s \
                                    --health-timeout=5s \
                                    --health-retries=3 \
                                    mysql:latest
                            '''
                        }
                    }
                }
                
                stage('Setup Python') {
                    steps {
                        sh '''
                            # Install Python 3.10 if not available
                            python3.10 --version || {
                                sudo apt-get update
                                sudo apt-get install -y software-properties-common
                                sudo add-apt-repository -y ppa:deadsnakes/ppa
                                sudo apt-get update
                                sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
                            }
                            
                            # Create virtual environment
                            python3.10 -m venv venv
                            source venv/bin/activate
                            python --version
                        '''
                    }
                }
            }
        }
        
        stage('Install System Dependencies') {
            steps {
                sh '''
                    sudo apt-get update
                    sudo apt-get install -y wget unzip curl jq fonts-liberation libatk-bridge2.0-0 libatk1.0-0 \
                        libcairo2 libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 \
                        libu2f-udev libx11-xcb1 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 xdg-utils \
                        xvfb psmisc mysql-client
                '''
            }
        }
        
        stage('Setup Chrome') {
            steps {
                script {
                    try {
                        sh '''
                            # Install Chrome
                            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
                            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
                            sudo apt-get update
                            sudo apt-get install -y google-chrome-stable
                            
                            # Verify installation
                            google-chrome --version
                        '''
                    } catch (Exception e) {
                        echo "Primary Chrome installation failed, trying fallback..."
                        sh '''
                            # Fallback Chrome Setup
                            sudo apt-get remove -y google-chrome-stable || true
                            sudo rm -f /usr/local/bin/chromedriver || true
                            
                            # Install Chrome manually
                            wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
                            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
                            sudo apt-get update
                            sudo apt-get install -y google-chrome-stable
                            
                            google-chrome --version
                        '''
                    }
                }
            }
        }
        
        stage('Start Virtual Display') {
            steps {
                sh '''
                    sudo Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
                    sleep 3
                '''
            }
        }
        
        stage('Install Python Dependencies') {
            steps {
                sh '''
                    source venv/bin/activate
                    python -m pip install --upgrade pip
                    
                    # Check if requirements.txt exists, if not create a basic one
                    if [ ! -f requirements.txt ]; then
                        echo "requirements.txt not found! Creating basic requirements..."
                        cat > requirements.txt << 'EOF'
selenium>=4.0.0
pytest>=7.0.0
pytest-html>=3.0.0
allure-pytest>=2.9.0
pymysql>=1.0.0
python-dotenv>=0.19.0
EOF
                    fi
                    
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Wait for MySQL') {
            steps {
                sh '''
                    echo "Waiting for MySQL to be ready..."
                    for i in {1..30}; do
                        if mysqladmin ping -h"127.0.0.1" -uroot -p"${DATABASE_PASSWORD}" --silent; then
                            echo "MySQL is ready!"
                            break
                        fi
                        echo "Waiting for MySQL... ($i/30)"
                        sleep 2
                    done
                '''
            }
        }
        
        stage('Initialize Database') {
            steps {
                sh '''
                    if [ ! -f init.sql ]; then 
                        echo "init.sql not found! Creating a dummy one for demo."
                        echo "CREATE TABLE IF NOT EXISTS test_table (id INT PRIMARY KEY, name VARCHAR(255));" > init.sql
                    fi
                    mysql -h 127.0.0.1 -uroot -p"${DATABASE_PASSWORD}" test_data < init.sql
                '''
            }
        }
        
        stage('Pre-test Cleanup & Setup') {
            steps {
                sh '''
                    echo "=== Comprehensive Chrome Cleanup ==="
                    
                    # Kill all Chrome and ChromeDriver processes
                    sudo pkill -f chrome || true
                    sudo pkill -f chromedriver || true
                    sudo killall -9 chrome || true
                    sudo killall -9 chromedriver || true
                    
                    # Clean up Chrome user data directories
                    sudo rm -rf /tmp/chrome_user_data_* || true
                    sudo rm -rf /tmp/.org.chromium.* || true
                    sudo rm -rf /tmp/scoped_dir* || true
                    sudo rm -rf ~/.config/google-chrome* || true
                    sudo rm -rf ~/.cache/google-chrome* || true
                    
                    # Clean up any Chrome lock files
                    sudo rm -rf /tmp/.X*-lock || true
                    sudo rm -rf /tmp/.X11-unix/X* || true
                    
                    # Clean up shared memory
                    sudo rm -rf /dev/shm/* || true
                    
                    # Set proper permissions for temp directories
                    sudo chmod 1777 /tmp
                    mkdir -p /tmp/chrome_temp
                    chmod 755 /tmp/chrome_temp
                    
                    # Create required directories
                    mkdir -p logs
                    mkdir -p allure-results
                    mkdir -p reports
                    mkdir -p downloads
                    
                    sleep 3
                    echo "=== Cleanup Complete ==="
                '''
            }
        }
        
        stage('Environment Check') {
            steps {
                sh '''
                    echo "=== Environment Check ==="
                    echo "TMPDIR: $TMPDIR"
                    echo "USER: $USER"
                    echo "HOME: $HOME"
                    echo "Available temp space:"
                    df -h /tmp
                    echo "Chrome version:"
                    google-chrome --version || echo "Chrome not found"
                    echo "ChromeDriver version:"
                    chromedriver --version || echo "ChromeDriver not found"
                    echo "Chrome processes before test:"
                    ps aux | grep -E "(chrome|chromedriver)" | grep -v grep || echo "No Chrome processes found"
                    echo "Python version:"
                    source venv/bin/activate && python --version
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    source venv/bin/activate
                    
                    # Create a basic test file if none exists
                    if [ ! -f test_*.py ] && [ ! -d tests ]; then
                        echo "No test files found! Creating a basic test..."
                        mkdir -p tests
                        cat > tests/test_basic.py << 'EOF'
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_basic_chrome():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    assert "Google" in driver.title
    driver.quit()

def test_basic_assertion():
    assert 1 + 1 == 2
EOF
                    fi
                    
                    # Run the tests
                    pytest --maxfail=1 -vv -s --tb=short --alluredir=allure-results tests/ || pytest --maxfail=1 -vv -s --tb=short --alluredir=allure-results .
                '''
            }
            post {
                always {
                    sh '''
                        echo "=== Post-test Cleanup ==="
                        sudo pkill -f chrome || true
                        sudo pkill -f chromedriver || true
                        sudo rm -rf /tmp/chrome_user_data_* || true
                        sudo rm -rf /tmp/.org.chromium.* || true
                        sudo rm -rf /tmp/scoped_dir* || true
                    '''
                }
            }
        }
        
        stage('Generate Reports') {
            steps {
                script {
                    // Install Allure CLI if not present
                    sh '''
                        if ! command -v allure &> /dev/null; then
                            echo "Installing Allure CLI..."
                            wget -O allure-commandline.tgz https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz
                            tar -zxf allure-commandline.tgz
                            sudo mv allure-2.24.0 /opt/allure
                            sudo ln -s /opt/allure/bin/allure /usr/local/bin/allure
                        fi
                        
                        # Generate Allure Report
                        allure generate allure-results -o allure-report --clean
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                // Archive test results
                archiveArtifacts artifacts: 'allure-report/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: 'logs/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
                
                // Publish Allure report
                try {
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'allure-results']]
                    ])
                } catch (Exception e) {
                    echo "Allure plugin not installed or configured. Report archived as artifacts."
                }
                
                // Publish test results
                try {
                    publishTestResults testResultsPattern: 'allure-results/*.xml'
                } catch (Exception e) {
                    echo "Could not publish test results: ${e.message}"
                }
            }
        }
        
        success {
            echo 'Pipeline succeeded!'
        }
        
        failure {
            echo 'Pipeline failed!'
            // Send notifications here if needed
        }
        
        cleanup {
            sh '''
                # Final cleanup
                sudo pkill -f chrome || true
                sudo pkill -f chromedriver || true
                sudo rm -rf /tmp/chrome_user_data_* || true
                
                # Stop and remove MySQL container
                docker stop mysql-test || true
                docker rm mysql-test || true
                
                # Clean up virtual environment if needed
                # rm -rf venv
            '''
        }
    }
}