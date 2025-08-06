# Pokemon Rater

A web application for rating Pokemon and analyzing your preferences, built with FastAPI and SQLite.

## Features

- **Rate Pokemon**: Give numerical ratings to Pokemon with optional comments
- **Search & Filter**: Find Pokemon by name or browse unrated Pokemon
- **Real-time Analytics**: View top/bottom rated Pokemon, statistics by type and generation
- **Authentication**: Secure login system for data protection
- **Pokemon Data**: Integrated with PokeAPI for Pokemon images and data

## Quick Start with Docker (Recommended)

### Prerequisites

- Docker and Docker Compose installed

### 1. Set Up Environment

```bash
# Copy the environment template
cp env.template .env

# Edit .env with your preferred settings (optional)
# The defaults will work for local development
```

### 2. Start the Application

```bash
# Initialize the database (first time only)
docker-compose --profile init up db-init

# Start the application
docker-compose up app
```

The application will be available at: **http://localhost:8000**

### 3. Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

## Manual Setup (Alternative)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
python scripts/import_csv.py
```

### 3. Start the Application

```bash
python run.py
```

The application will be available at: **http://localhost:8000**

## Usage

### Rating Pokemon

1. Go to `/rate`
2. Login with the admin credentials
3. Search for a Pokemon or click "Get Random Unrated"
4. Enter a numerical rating (any number, including negatives)
5. Add an optional comment
6. Submit the rating

### Viewing Analytics

1. Go to `/analytics`
2. View statistics including:
   - Total Pokemon and ratings
   - Top 10 and bottom 10 rated Pokemon
   - Filter by Pokemon type or generation
   - Overall rating statistics

## File Structure

```
pokemonrater/
├── app/                 # FastAPI application
├── templates/           # HTML templates
├── static/             # CSS and static files
├── scripts/            # Database import scripts
├── data/              # Database storage (Docker)
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
└── requirements.txt   # Python dependencies
```

## Development

### Using Docker for Development

```bash
# Start with live reload
docker-compose up app

# The code is mounted as a volume, so changes will reload automatically
```

### Manual Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run with live reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Security

### Environment Variables

This project uses environment variables to keep secrets secure:

- **env.template**: Template file showing all required variables
- **.env**: Your actual environment file (never commit this!)
- **.gitignore**: Ensures .env files are not tracked by git

### Important Security Notes

1. **Change default credentials** in your .env file before deployment
2. **Generate a strong SECRET_KEY** for production use
3. **Use strong passwords** for admin accounts
4. The .env file is automatically excluded from git commits

## Production Deployment

1. Copy `env.template` to `.env` and update all values
2. Generate a strong secret key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Use a production database (PostgreSQL)
4. Use a production WSGI server like Gunicorn
5. Set up proper SSL/TLS certificates

## Troubleshooting

### Docker Issues

- Make sure Docker and Docker Compose are installed
- Run `docker-compose down` to clean up containers
- Check `docker-compose logs` for error messages

### Database Issues

- Delete the `data/` directory and re-run the initialization
- Check that the CSV file is in the correct location

### Import Errors

- Make sure all dependencies are installed
- Check Python version (3.8+ required)

## Contributing

This is a personal project, but feel free to fork and modify for your own use!
