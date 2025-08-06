#!/bin/bash

# Pokemon Rater Setup Script

echo "🎮 Setting up Pokemon Rater..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created!"
    echo "⚠️  Please edit .env to customize your settings"
else
    echo "✅ .env file already exists"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "🐳 Docker and Docker Compose are available"

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

echo "🚀 Setup complete! You can now run:"
echo ""
echo "  # Initialize database (first time only):"
echo "  docker-compose --profile init up db-init"
echo ""
echo "  # Start the application:"
echo "  docker-compose up app"
echo ""
echo "  # Or both in one command:"
echo "  docker-compose --profile init up db-init && docker-compose up app"
echo ""
echo "📱 App will be available at: http://localhost:8000"
echo "🔑 Default login: admin / admin123 (change in .env file)"