# Getting Started with Land Analysis Crew

This guide will help you set up and start using the Land Analysis Crew application.

## Prerequisites

Before you begin, ensure you have:

- Python 3.9+ installed on your system
- [Ollama](https://ollama.com/) installed locally for running Llama AI models
- Basic command-line knowledge
- Property data in CSV format (sample provided in the repository)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/land-analysis-crew.git
   cd land-analysis-crew
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root:
   ```
   # Ollama configuration
   USE_OLLAMA=true
   OLLAMA_MODEL=llama3
   OLLAMA_API_BASE=http://localhost:11434
   
   # Optional: For testing without a real LLM
   # USE_MOCK_LLM=false
   
   # AI temperature (lower = more focused, higher = more creative)
   CREW_TEMPERATURE=0.5
   ```

## Running Ollama

1. **Install Ollama** from [ollama.com](https://ollama.com/)

2. **Start the Ollama service:**
   ```bash
   ollama serve
   ```
   
3. **Download the Llama model:**
   ```bash
   ollama pull llama3
   ```
   
   Note: This will download the model which may take several minutes depending on your connection.

## Analyzing Properties

### Basic Analysis

To analyze a specific property:

```bash
python examples/analyze_property.py NY-00004
```

Replace `NY-00004` with the stock number of the property you want to analyze.

### Comparing Properties

To compare multiple properties:

```bash
python examples/compare_properties.py NY-00004 NY-00005
```

You can compare as many properties as needed by adding more stock numbers.

### Viewing Available Properties

To see a list of all available properties:

```bash
./scripts/run.sh --list
```

## Understanding the Results

The analysis will create several files in the `outputs/reports` directory:

1. **Full Report**: Comprehensive analysis of the property
2. **Executive Summary**: High-level overview of findings and recommendations
3. **Investment Summary**: Key metrics and financial considerations

Each report is saved as a Markdown file that can be viewed in any text editor or Markdown viewer.

## Troubleshooting

- **Ollama not running**: Ensure Ollama is installed and the service is running with `ollama serve`
- **Model not found**: Make sure you've pulled the model with `ollama pull llama3`
- **Slow performance**: Llama models can be resource-intensive. Consider using a smaller model version if available, or ensure your system has adequate RAM (16GB+ recommended)
- **Connection errors**: Check that Ollama is running on the expected port (default: 11434)

## Advanced Usage

You can modify the following environment variables in your `.env` file:

- `OLLAMA_MODEL`: Change to a different Llama model version
- `CREW_TEMPERATURE`: Adjust from 0.0 (most focused) to 1.0 (most creative)
- `USE_MOCK_LLM`: Set to `true` for testing without using actual AI models 