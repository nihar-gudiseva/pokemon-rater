@echo off
REM Pokemon Rater Windows Commands
REM Use 'make.bat help' to see available commands

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="build" goto build
if "%1"=="init" goto init
if "%1"=="start" goto start
if "%1"=="dev" goto dev
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="clean" goto clean
if "%1"=="clean-db" goto clean-db
if "%1"=="reset" goto reset
if "%1"=="test" goto test
if "%1"=="status" goto status
if "%1"=="shell" goto shell
if "%1"=="manual-setup" goto manual-setup
if "%1"=="manual-start" goto manual-start
if "%1"=="check-env" goto check-env
if "%1"=="backup-db" goto backup-db
if "%1"=="db-admin" goto db-admin
if "%1"=="clean-hard" goto clean-hard

echo Unknown command: %1
goto help

:help
echo Pokemon Rater - Available Commands:
echo.
echo   help           Show this help message
echo   setup          Setup environment and initialize database
echo   build          Build the Docker image
echo   init           Initialize database with Pokemon data
echo   start          Start the application (includes database initialization)
echo   dev            Start in development mode with live reload
echo   stop           Stop all containers
echo   restart        Restart the application
echo   logs           Show application logs
echo   clean          Clean up containers, volumes, and images
echo   clean-db       Clean only the database
echo   reset          Reset database with fresh data
echo   test           Run a quick test to check if the app is running
echo   status         Show container status
echo   shell          Open a shell in the running container
echo   manual-setup   Setup for manual (non-Docker) development
echo   manual-start   Start manually without Docker
echo   check-env      Check if .env file exists
echo   backup-db      Backup the database
echo   db-admin       Start database admin interface
echo   clean-hard     Stop containers, prune networks, delete database file
echo.
echo Quick Start:
echo   make.bat setup    # First time setup
echo   make.bat start    # Start the application
goto end

:setup
echo Setting up Pokemon Rater...
if not exist .env (
    echo Creating .env file from template...
    copy env.template .env
    echo .env file created! Edit it to customize settings.
) else (
    echo .env file already exists
)
if not exist data mkdir data
echo Setup complete! Run 'make.bat start' to begin.
goto end

:build
echo Building Docker image...
docker compose build
goto end

:init
echo Initializing database (one-off job)...
docker compose --profile init run --rm db-init
goto end

:start
echo Starting Pokemon Rater...
echo Checking if database exists...
if not exist data\pokemon_rater.db (
    echo Database not found, initializing...
    call :init
)
echo Starting application...
docker compose up app
goto end

:dev
echo Starting in development mode...
docker compose up app
goto end

:stop
echo Stopping containers...
docker compose down
goto end

:restart
call :stop
call :start
goto end

:logs
docker compose logs -f app
goto end

:clean
echo Cleaning up...
docker-compose down -v --remove-orphans
docker-compose down --rmi local
if exist data (
    echo Removing data directory...
    rmdir /s /q data
)
goto end

:clean-db
echo Cleaning database...
if exist data (
    rmdir /s /q data
    echo Database cleaned
)
goto end

:reset
call :clean-db
call :init
goto end

:test
echo Testing application...
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel%==0 (
    echo App is running!
) else (
    echo App is not responding
)
goto end

:status
docker compose ps
goto end

:shell
docker compose exec app /bin/bash
goto end

:manual-setup
echo Manual setup...
pip install -r requirements.txt
python scripts/import_csv.py
goto end

:manual-start
echo Starting manually...
python run.py
goto end

:check-env
if exist .env (
    echo .env file exists
    echo Environment variables:
    type .env | findstr /v "^#" | findstr /v "^$"
) else (
    echo .env file not found. Run 'make.bat setup' first.
)
goto end

:backup-db
if exist data\pokemon_rater.db (
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
    copy data\pokemon_rater.db data\pokemon_rater_backup_%mydate%_%mytime%.db
    echo Database backed up
) else (
    echo No database found to backup
)
goto end

:db-admin
echo Starting database admin interface...
echo Database admin will be available at http://localhost:8080
echo Ensuring project network exists by starting app (detached)...
docker compose up -d app
docker compose --profile admin up -d db-admin
goto end

:clean-hard
echo Stopping containers and removing volumes...
docker compose down -v --remove-orphans
echo Pruning unused Docker networks...
docker network prune -f
echo Deleting local SQLite database file if it exists...
if exist data\pokemon_rater.db del /q data\pokemon_rater.db
echo Done. You can re-initialize with: make.bat start
goto end

:end