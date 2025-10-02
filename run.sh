#!/bin/bash

# CSV Analyzer AI Agent - Quick Run Script
# Activates environment and launches the application

# Get project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 Starting CSV Analyzer AI Agent..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗${NC} Virtual environment not found!"
    echo "Please run: ./setup.sh"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗${NC} .env file not found!"
    echo "Please run: ./setup.sh"
    exit 1
fi

# Check if API key is configured
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${YELLOW}⚠${NC} OpenAI API key not configured in .env"
    echo "Please add your API key to .env file"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo -e "${RED}✗${NC} Streamlit not installed!"
    echo "Please run: ./setup.sh"
    exit 1
fi

# Launch the application
echo -e "${GREEN}✓${NC} Starting Streamlit application..."
echo ""
echo "📱 Access the app at:"
echo "   • http://localhost:8501"
echo "   • http://127.0.0.1:8501"
echo "   • Network URL (shown by Streamlit below)"
echo ""
cd src
streamlit run app.py
