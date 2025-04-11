#!/bin/bash
# Run script for Property Analysis System

# Exit on error
set -e

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# If virtual environment exists, activate it
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Function to display help
show_help() {
    echo "Property Analysis Crew - Command Line Tool"
    echo ""
    echo "Usage: ./run.sh [OPTIONS] [STOCK_NUMBER]"
    echo ""
    echo "Options:"
    echo "  --help, -h      Show this help message"
    echo "  --list, -l      List available properties"
    echo "  --env, -e       Print environment configuration"
    echo "  --mock, -m      Use mock implementation (no real LLM)"
    echo ""
    echo "Examples:"
    echo "  ./run.sh NY-00004         Analyze property NY-00004"
    echo "  ./run.sh --list           List all available properties"
    echo "  ./run.sh --mock NY-00004  Analyze property NY-00004 with mock implementation"
    echo ""
}

# Function to list available properties
list_properties() {
    echo "Available properties:"
    echo ""
    python -c "
from src.data.loader import PropertyDataLoader
loader = PropertyDataLoader()
properties = loader.get_property_list()
for p in properties:
    stock_number = p.get('StockNumber', 'Unknown')
    address = p.get('Property Address', 'Unknown Address')
    city = p.get('City', 'Unknown')
    state = p.get('State', 'Unknown')
    acres = p.get('Land Area (AC)', 'Unknown')
    print(f'{stock_number.ljust(10)} | {address.ljust(40)} | {city}, {state} | {acres} acres')
"
}

# Function to print environment configuration
print_env() {
    echo "Environment Configuration:"
    echo ""
    
    # Check for .env file
    if [ -f "$PROJECT_ROOT/.env" ]; then
        echo "Using configuration from .env file:"
        echo ""
        cat "$PROJECT_ROOT/.env" | grep -v "^#" | grep -v "^$"
    else
        echo "No .env file found. Using default configuration."
    fi
    
    echo ""
}

# Check if no arguments were provided
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Parse command line arguments
USE_MOCK=false
STOCK_NUMBER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --list|-l)
            list_properties
            exit 0
            ;;
        --env|-e)
            print_env
            exit 0
            ;;
        --mock|-m)
            USE_MOCK=true
            shift
            ;;
        *)
            STOCK_NUMBER=$1
            shift
            ;;
    esac
done

# If no stock number is provided, show help
if [ -z "$STOCK_NUMBER" ]; then
    show_help
    exit 1
fi

# Run the analysis
if [ "$USE_MOCK" = true ]; then
    echo "Using mock implementation for property analysis (no real LLM)"
    python "$PROJECT_ROOT/examples/mock_crew.py" "$STOCK_NUMBER"
else
    python "$PROJECT_ROOT/examples/analyze_property.py" "$STOCK_NUMBER"
fi 