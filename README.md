# Property Analysis Crew

A CrewAI-powered application for comprehensive property analysis to support real estate development decision-making, using Llama 3 model via Ollama.

## Overview

This application uses a team of AI agents (a "crew") to analyze property data and provide insights and recommendations for attainable housing development with a focus on locations experiencing both economic growth and housing affordability challenges.

## Quick Start Guide

1. **Run the setup script** for your platform:
   - Windows: Double-click `setup.bat` or run it from command prompt
   - macOS/Linux: Run `./setup.sh` in terminal

2. **Place your property data** in the DATA directory as `master.csv`

3. **Run the application**:
   ```
   python main.py
   ```

4. **Enter a stock number** when prompted to analyze that property

That's it! The setup script handles everything else automatically.

## How It Works

The application:
1. Automatically uses Llama 3 8B via Ollama if installed (free, runs locally)
2. Falls back to Claude via Anthropic API if you've provided an API key
3. Analyzes your property data through multiple specialized AI agents:
   - **Property Data Analyst**: Evaluates raw property metrics and demographics
   - **Housing & Economic Research Specialist**: Researches local market conditions
   - **Attainable Housing Financial Analyst**: Provides ROI analysis
   - **Attainable Housing Development Strategist**: Creates strategic recommendations

## Detailed Setup Instructions

### Automatic Setup (Recommended)

The easiest way to get started is using our setup scripts:

#### On macOS:
1. Open Terminal in the project directory
2. Make the script executable: `chmod +x setup.sh`
3. Run the script: `./setup.sh`
4. Follow the on-screen instructions

The setup script will:
- Create a Python virtual environment
- Install required dependencies
- Check for Ollama and help install it if needed
- Download the Llama 3 model if needed
- Set up fallback to Anthropic if Ollama isn't available

### Manual Setup

If you prefer to set up manually:

1. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Choose your AI model**:

   **Option A: Llama 3 (Free, Local)**:
   - Install Ollama from [ollama.com](https://ollama.com/)
   - Start Ollama (it runs as a service on most systems)
   - Pull the Llama 3 model: `ollama pull llama3`

   **Option B: Claude (Requires API Key)**:
   - Copy `.env.example` to `.env`
   - Add your Anthropic API key to the `.env` file

4. **Prepare your data**:
   - Create a `DATA` directory
   - Place your property CSV file as `DATA/master.csv`

## CSV Data Format

Your CSV file should include these columns:
- `StockNumber`: Unique identifier for each property 
- Location information: `Property Address`, `City`, `State`, `Zip`
- Property details: `For Sale Price`, `Land Area (AC)`, `Zoning`
- Demographic/economic metrics (refer to column descriptions in the code)

## Troubleshooting

### Ollama Issues
- **"Ollama is not installed"**: Download from [ollama.com](https://ollama.com/)
- **"Ollama is not running"**: Start it with `ollama serve`
- **Slow model download**: The Llama 3 model is ~4GB. Ensure good internet connection.

### Performance Notes
- First-time analysis may be slower as the model warms up
- Llama 3 requires at least 8GB RAM, preferably 16GB
- Analysis typically takes 5-15 minutes with Llama 3

## Using Claude Instead of Llama 3

If you prefer using Claude (which may produce better results but requires an API key):

1. Create a `.env` file (or edit the one created by the setup script)
2. Add your Anthropic API key: `ANTHROPIC_API_KEY=your_key_here`
3. Run the application normally - it will detect and use Claude automatically

## System Requirements

- Python 3.9+
- 8GB+ RAM recommended (16GB preferred for Llama 3)
- Internet connection for web search functionality
- For Llama 3: Ollama installed

# Land Analysis Crew

A property analysis system using CrewAI to evaluate land for attainable housing development.

## Quick Start for Mac Users

For Mac users, we provide a single all-in-one startup script that handles everything:

1. Download this repository and navigate to its directory
2. Make the script executable:
   ```bash
   chmod +x startup.sh
   ```
3. Run the script:
   ```bash
   ./startup.sh
   ```

That's it! The script will automatically:
- Check for and install all required dependencies (Python, Homebrew, Ollama)
- Set up the Python environment
- Install and configure the Llama 3 AI model
- Create all necessary directories and configuration
- Run the application

The script keeps you informed of progress at each step and handles both first-time setup and subsequent runs.

## Understanding the Data

The system analyzes properties using a comprehensive dataset with demographic, economic, and geographic information. To understand what each column in the data means:

1. Check the [Data Dictionary](docs/data_dictionary.md) for detailed descriptions of all data columns
2. The most important metrics for property analysis include:
   - Population growth (5-mile radius)
   - Median household income (5-mile radius)
   - Median home values (5-mile radius)
   - Composite score (overall property rating)

## For Windows and Linux Users

For Windows and Linux users, follow these steps:

1. Run the appropriate setup script:
   ```bash
   # For Windows
   setup.bat
   
   # For Linux
   chmod +x setup.sh
   ./setup.sh
   ```

2. Place your property data in the `DATA` directory as `master.csv`

3. Run the application:
   ```bash
   python main.py
   ```

## Troubleshooting

### Ollama Issues

- If Ollama doesn't install or start automatically, you can install it manually from [https://ollama.com/](https://ollama.com/)
- Start Ollama manually with `ollama serve` if it doesn't start automatically
- Verify Llama 3 is installed with `ollama list`

### Using Claude Instead of Llama

If you prefer using Claude AI or can't run Ollama:

1. Get an API key from [Anthropic](https://console.anthropic.com/)
2. Edit the `.env` file to add your key: `ANTHROPIC_API_KEY=your_key_here`
3. Set `USE_CLAUDE=True` in the `.env` file

## Additional Documentation

For more detailed information:
- [Mac Setup Guide](docs/mac_setup_guide.md)
- [Data Dictionary](docs/data_dictionary.md)

