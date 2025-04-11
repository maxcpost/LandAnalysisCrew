#!/bin/bash
# Setup script for Property Analysis System

# Navigate to project root directory (assuming this script is in scripts/)
cd "$(dirname "$0")/.."

# Create directory structure
echo "Creating directory structure..."
mkdir -p src/{agents,tools,data,models,utils,visualization}
mkdir -p examples
mkdir -p tests
mkdir -p docs

# Create __init__.py files for Python packages
echo "Creating package files..."
touch src/__init__.py
touch src/agents/__init__.py
touch src/tools/__init__.py
touch src/data/__init__.py
touch src/models/__init__.py
touch src/utils/__init__.py
touch src/visualization/__init__.py

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify environment
echo "Verifying installation..."
python -c "import crewai; print('CrewAI version:', crewai.__version__)"

echo "Setup complete!"
echo "Use './scripts/run.sh' to run the application." 