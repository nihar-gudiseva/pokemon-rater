@echo off
REM Pokemon Rater Setup Script for Windows

echo 🎮 Setting up Pokemon Rater...

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy env.template .env
    echo ✅ .env file created!
    echo ⚠️  Please edit .env to customize your settings
) else (
    echo ✅ .env file already exists
)

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo 🐳 Docker and Docker Compose are available

REM Create data directory
echo 📁 Creating data directory...
if not exist data mkdir data

echo 🚀 Setup complete! You can now run:
echo.
echo   # Initialize database (first time only):
echo   docker-compose --profile init up db-init
echo.
echo   # Start the application:
echo   docker-compose up app
echo.
echo   # Or both in one command:
echo   docker-compose --profile init up db-init ^&^& docker-compose up app
echo.
echo 📱 App will be available at: http://localhost:8000
echo 🔑 Default login: admin / admin123 (change in .env file)
pause