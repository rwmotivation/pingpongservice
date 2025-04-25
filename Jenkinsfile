pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        FLASK_APP = 'app.py'  // Change to your Flask app entry point
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning source code...'
                checkout scm
            }
        }

        stage('Set Up Environment') {
            steps {
                echo 'Creating virtual environment and installing dependencies...'
                sh 'python3 -m venv $VENV_DIR'
                sh './$VENV_DIR/bin/pip install --upgrade pip'
                sh './$VENV_DIR/bin/pip install -r requirements.txt'
            }
        }

        stage('Lint (flake8)') {
            steps {
                echo 'Linting with flake8...'
                sh './$VENV_DIR/bin/flake8 . || true' // Avoid failing the build on lint errors
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                sh './$VENV_DIR/bin/pytest tests/' // Adjust path if needed
            }
        }

        // Optional: Only for manual/development environments
        stage('Run Flask App') {
            when {
                expression { return params.RUN_FLASK == true }
            }
            steps {
                echo 'Starting Flask server...'
                sh '''
                    source $VENV_DIR/bin/activate
                    FLASK_APP=$FLASK_APP FLASK_ENV=development nohup flask run &
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh 'rm -rf $VENV_DIR'
        }
        success {
            echo '✅ Pipeline succeeded.'
        }
        failure {
            echo '❌ Pipeline failed.'
        }
    }
}
