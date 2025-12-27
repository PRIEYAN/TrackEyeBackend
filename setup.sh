#!/bin/bash

echo "Setting up TradeFlow AI Flask Backend..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p uploads

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your credentials"
fi

# Initialize database migrations
echo "Initializing database migrations..."
flask db init || echo "Migrations already initialized"

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database and API credentials"
echo "2. Run: flask db migrate -m 'Initial migration'"
echo "3. Run: flask db upgrade"
echo "4. Run: python run.py"

