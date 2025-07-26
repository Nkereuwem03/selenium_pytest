pipeline {
    agent any  // Using any Jenkins agent instead of a Docker container

    environment {
        DATABASE_HOST = '127.0.0.1'
        DATABASE_PORT = '3306'
        DATABASE_USER = 'root'
        DATABASE_PASSWORD = 'root'
        DATABASE_NAME = 'test_data'
        ALLURE_RESULTS = 'allure-results'
        REPORTS_DIR = 'reports'
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Prepare Environment') {
            steps {
                ansiColor('xterm') {
                    sh '''
                        echo "Updating pip and installing dependencies"
                        python3 -m pip install --upgrade pip
                        pip3 install -r requirements.txt
                    '''
                }
            }
        }

        stage('Start MySQL') {
            steps {
                ansiColor('xterm') {
                    sh '''
                        docker run --name test-mysql -e MYSQL_ROOT_PASSWORD=${DATABASE_PASSWORD} -e MYSQL_DATABASE=${DATABASE_NAME} -p ${DATABASE_PORT}:3306 -d mysql:latest

                        echo "Waiting for MySQL to be ready..."
                        for i in {1..30}; do
                            if docker exec test-mysql mysqladmin ping -uroot -p${DATABASE_PASSWORD} --silent; then
                                break
                            fi
                            sleep 2
                        done

                        docker cp init.sql test-mysql:/init.sql
                        docker exec test-mysql bash -c "mysql -uroot -p${DATABASE_PASSWORD} ${DATABASE_NAME} < /init.sql"
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                ansiColor('xterm') {
                    sh '''
                        pytest --maxfail=1 --disable-warnings \
                               --alluredir=${ALLURE_RESULTS} \
                               --html=${REPORTS_DIR}/report.html --self-contained-html
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${ALLURE_RESULTS}/**", allowEmptyArchive: true
                    archiveArtifacts artifacts: "${REPORTS_DIR}/report.html", allowEmptyArchive: true
                }
                failure {
                    mail to: 'team@example.com',
                         subject: "Test Failure: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                         body: "Tests failed. See Jenkins for details."
                }
            }
        }

        stage('Publish Allure Report') {
            steps {
                allure includeProperties: false, jdk: '', results: [[path: "${ALLURE_RESULTS}"]]
            }
        }
    }

    post {
        always {
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
