#!/bin/bash

# CSV Analyzer AI Agent - Complete Setup Script
# This script will set up everything you need to run the application

set -e  # Exit on error

echo "=================================="
echo "CSV Analyzer AI Agent - Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "📂 Project directory: $PROJECT_DIR"
echo ""

# Step 1: Check Python
echo "Step 1/6: Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo ""

# Step 2: Create virtual environment
echo "Step 2/6: Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi
echo ""

# Step 3: Activate and install dependencies
echo "Step 3/6: Installing dependencies..."
source venv/bin/activate

echo "Installing packages (this may take a few minutes)..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All dependencies installed successfully"
else
    echo -e "${RED}✗${NC} Failed to install dependencies"
    exit 1
fi
echo ""

# Step 4: Configure environment
echo "Step 4/6: Configuring environment..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} .env file already exists"
    echo "Current API key status:"
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo -e "${GREEN}✓${NC} API key is configured"
    else
        echo -e "${YELLOW}⚠${NC} API key needs to be added"
        echo ""
        echo "Please edit .env and add your OpenAI API key:"
        echo "  nano .env"
        echo ""
        echo "Or run:"
        echo '  echo "OPENAI_API_KEY=your-key-here" > .env'
    fi
else
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file from template"
    echo ""
    echo -e "${YELLOW}ACTION REQUIRED:${NC}"
    echo "Please edit .env and add your OpenAI API key:"
    echo "  nano .env"
    echo ""
    echo "Get an API key at: https://platform.openai.com/api-keys"
fi
echo ""

# Step 5: Generate sample data
echo "Step 5/6: Generating sample data..."
cd src
if [ -f "../sample_data_sales.csv" ]; then
    echo -e "${YELLOW}⚠${NC} Sample data already exists, skipping..."
else
    python3 generate_sample_data.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Sample data generated"
    else
        echo -e "${YELLOW}⚠${NC} Could not generate sample data (optional)"
    fi
fi
cd ..
echo ""

# Step 6: Verify setup
echo "Step 6/6: Verifying setup..."
./check_environment.sh
echo ""

# Final instructions
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "To start the application:"
echo ""
echo -e "${GREEN}  source venv/bin/activate${NC}"
echo -e "${GREEN}  cd src${NC}"
echo -e "${GREEN}  streamlit run app.py${NC}"
echo ""
echo "Or simply run:"
echo -e "${GREEN}  ./run.sh${NC}"
echo ""
echo "📖 Documentation:"
echo "  • Quick start: GETTING_STARTED.md"
echo "  • Architecture: ARCHITECTURE.md"
echo "  • Full docs: README.md"
echo ""
