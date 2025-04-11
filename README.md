# Land Analysis Crew 🏙️

A powerful AI-driven analysis tool for evaluating property development potential.

## Overview

This system uses a crew of specialized AI agents, powered by Llama AI models running locally via Ollama, to analyze properties for high-density residential development potential.

The AI agents work together to research the property, assess development potential, analyze the market, and generate a comprehensive report with specific recommendations.

## Features

- **Web Research**: Automatically researches property details, zoning regulations, demographics, and economic trends
- **Development Potential Analysis**: Evaluates property potential and constraints
- **Market Analysis**: Analyzes market trends, competition, and pricing
- **Comprehensive Reporting**: Generates detailed reports with executive summaries
- **Property Comparison**: Can compare multiple properties to identify the best investment opportunities
- **Local AI Processing**: All analysis runs locally using Llama AI via Ollama - no data leaves your machine

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com/) installed locally
- A Mac or Linux system (Windows support is experimental)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/land-analysis-crew.git
cd land-analysis-crew
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install [Ollama](https://ollama.com/) from the official website.

4. Create a `.env` file with your configuration:
```
# Use Llama model via Ollama
USE_OLLAMA=true
OLLAMA_MODEL=llama3
```

## Usage

### Analyzing a Property

To analyze a property from the database:

```bash
python examples/analyze_property.py NY-00004
```

The system will:
1. Research the property using publicly available data
2. Analyze its development potential
3. Generate a comprehensive report
4. Create an executive summary
5. Save everything to the outputs directory

### Comparing Properties

To compare multiple properties:

```bash
python examples/compare_properties.py NY-00004 NY-00005 FL-00003
```

This generates a comparison report highlighting the strengths and weaknesses of each property.

## How It Works

The system comprises several specialized AI agents:

1. **Web Researcher**: Gathers information about the property, local regulations, demographics, etc.
2. **Data Analyst**: Analyzes potential development scenarios and financial projections
3. **Market Analyst**: Assesses market conditions, competition, and demand
4. **Report Generator**: Creates comprehensive reports and summaries

These agents collaborate using the CrewAI framework to produce a holistic analysis.

## Configuration

Key environment variables:

```
# Ollama configuration (required)
USE_OLLAMA=true
OLLAMA_MODEL=llama3

# For faster testing with mock responses
USE_MOCK_LLM=false
```

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
- **Slow model download**: The Llama 3.3 70B model is ~50GB. Ensure good internet connection.

### Performance Notes
- First-time analysis may be slower as the model warms up
- Llama 3.3 70B requires at least 16GB RAM, preferably 32GB
- Analysis typically takes 10-30 minutes with Llama 3.3 70B

## System Testing

Before running the full analysis, you can verify that your system is properly configured with our test script:

```bash
python test_system.py
```

This will check:
- Python and required package installation
- Ollama installation and service status
- Llama 3.3 70B model availability
- CSV data file presence

The test will provide clear guidance on addressing any issues found before running the main application.

## Development

### Project Structure

```
LandAnalysisCrew/
├── data/               # Property dataset
├── examples/           # Example usage scripts
├── outputs/            # Generated reports
├── scripts/            # Utility scripts
├── src/                # Source code
│   ├── data/           # Data handling modules
│   ├── models/         # AI model implementations
│   ├── utils/          # Utility functions
│   └── main.py         # Main application entry point
├── .env                # Environment configuration
├── README.md           # This documentation
└── requirements.txt    # Python dependencies
```

### Testing Without Real LLM

For development and testing without using a real language model:

1. Set `USE_MOCK_LLM=true` in your `.env` file, or
2. Use the `--mock` flag with the run script: `./scripts/run.sh --mock NY-00004`

The mock implementation simulates the AI crew's behavior and generates reasonable sample outputs.

## Customization

### Adding Properties

To add new properties to the database:

1. Edit the CSV file in the `data` directory
2. Ensure it follows the same format as the existing data

### Advanced Configuration

For advanced configuration, edit the following files:

- `.env`: Environment variables and API configuration
- `src/models/crew.py`: Agent roles and crew structure
- `examples/mock_crew.py`: Mock implementation responses

## License

[MIT License](LICENSE)

## Contributors

- Your Name - Initial work

Feel free to contribute to this project by submitting issues or pull requests!

