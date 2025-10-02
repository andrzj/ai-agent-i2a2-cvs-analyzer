#!/bin/bash

# CSV Analyzer AI Agent - Environment Test Script
# This script verifies your environment is properly configured

echo "🔍 CSV Analyzer AI Agent - Environment Check"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
CHECKS_PASSED=0
TOTAL_CHECKS=0

# Function to print check result
check_result() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $2"
        if [ ! -z "$3" ]; then
            echo -e "  ${YELLOW}→${NC} $3"
        fi
    fi
}

echo "1. Checking Python installation..."
python3 --version > /dev/null 2>&1
check_result $? "Python 3 is installed" "Install Python 3.8+ from python.org"

echo ""
echo "2. Checking virtual environment..."
if [ -d "venv" ]; then
    check_result 0 "Virtual environment exists"
else
    check_result 1 "Virtual environment not found" "Run: python3 -m venv venv"
fi

echo ""
echo "3. Checking if virtual environment is activated..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    check_result 0 "Virtual environment is activated"
else
    check_result 1 "Virtual environment not activated" "Run: source venv/bin/activate"
fi

echo ""
echo "4. Checking required packages..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    python3 -c "import streamlit" > /dev/null 2>&1
    check_result $? "Streamlit is installed" "Run: pip install -r requirements.txt"
    
    python3 -c "import langchain" > /dev/null 2>&1
    check_result $? "LangChain is installed" "Run: pip install -r requirements.txt"
    
    python3 -c "import pandas" > /dev/null 2>&1
    check_result $? "Pandas is installed" "Run: pip install -r requirements.txt"
    
    python3 -c "import plotly" > /dev/null 2>&1
    check_result $? "Plotly is installed" "Run: pip install -r requirements.txt"
else
    echo -e "${YELLOW}⚠${NC} Skipping package checks (activate venv first)"
fi

echo ""
echo "5. Checking configuration..."
if [ -f ".env" ]; then
    check_result 0 ".env file exists"
    
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        check_result 0 "OpenAI API key is configured"
    elif grep -q "OPENAI_API_KEY=" .env; then
        check_result 1 "OpenAI API key is empty" "Add your API key to .env file"
    else
        check_result 1 "OpenAI API key not found in .env" "Add OPENAI_API_KEY=your-key to .env"
    fi
else
    check_result 1 ".env file not found" "Run: cp .env.example .env and configure it"
fi

echo ""
echo "6. Checking project structure..."
[ -d "src" ] && check_result 0 "src/ directory exists" || check_result 1 "src/ directory not found"
[ -f "src/app.py" ] && check_result 0 "app.py exists" || check_result 1 "app.py not found"
[ -f "requirements.txt" ] && check_result 0 "requirements.txt exists" || check_result 1 "requirements.txt not found"

echo ""
echo "7. Checking sample data..."
if [ -f "sample_data_sales.csv" ] || [ -f "sample_data_employees.csv" ] || [ -f "sample_data_customers.csv" ]; then
    check_result 0 "Sample data files found"
else
    check_result 1 "No sample data files found" "Run: cd src && python3 generate_sample_data.py"
fi

echo ""
echo "=============================================="
echo -e "Result: ${GREEN}${CHECKS_PASSED}${NC}/${TOTAL_CHECKS} checks passed"
echo ""

if [ $CHECKS_PASSED -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}✓ All checks passed! You're ready to go!${NC}"
    echo ""
    echo "To start the application, run:"
    echo "  cd src"
    echo "  streamlit run app.py"
elif [ $CHECKS_PASSED -ge $((TOTAL_CHECKS * 2 / 3)) ]; then
    echo -e "${YELLOW}⚠ Most checks passed, but some issues need attention.${NC}"
    echo "Review the failed checks above and fix them."
else
    echo -e "${RED}✗ Several issues detected. Please fix them before running.${NC}"
    echo ""
    echo "Quick setup:"
    echo "  1. python3 -m venv venv"
    echo "  2. source venv/bin/activate"
    echo "  3. pip install -r requirements.txt"
    echo "  4. cp .env.example .env"
    echo "  5. Edit .env and add your OpenAI API key"
fi

echo ""
