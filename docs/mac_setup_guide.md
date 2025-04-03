# Mac Setup Guide for Land Analysis Crew

This guide provides detailed instructions for setting up and running Land Analysis Crew on macOS.

## System Requirements

- macOS 10.15 (Catalina) or newer
- At least 8GB RAM (16GB recommended)
- 10GB free disk space
- Admin privileges for software installation

## One-Command Solution: startup.sh

We've created a single all-in-one script for Mac users that handles everything automatically:
- Detects and installs all required dependencies
- Sets up the Python environment
- Configures Ollama and downloads the Llama 3 model
- Runs the application
- Provides clear feedback at each step

### How to Use

1. Download the project and navigate to its directory in Terminal:
   ```bash
   cd path/to/LandAnalysisCrew
   ```

2. Make the script executable:
   ```bash
   chmod +x startup.sh
   ```

3. Run the script:
   ```bash
   ./startup.sh
   ```

4. That's it! The script will guide you through the entire process with clear feedback.

### What Happens Behind the Scenes

When you run `startup.sh`, it automatically:

1. Displays a welcome message showing all tasks to be performed
2. Checks for Python and installs it if missing (using Homebrew)
3. Sets up a Python virtual environment
4. Installs all required dependencies from requirements.txt
5. Installs Ollama (via Homebrew or direct installation)
6. Starts the Ollama service and ensures it's running
7. Downloads the Llama 3 8B model if not already present
8. Creates necessary directories (DATA, docs) if they don't exist
9. Checks for a data file and configuration files
10. Runs the main.py application
11. Performs cleanup after the application exits

## Troubleshooting

### Common Issues

#### "Permission Denied" Error When Running the Script

If you see "Permission denied" when trying to run the script, make sure it's executable:
```bash
chmod +x startup.sh
```

#### Homebrew Installation Issues

If Homebrew installation fails:
1. Visit https://brew.sh/ and follow their installation instructions
2. Run the script again after installing Homebrew

#### Ollama Installation Problems

If Ollama doesn't install correctly:
1. Visit https://ollama.com/ and download the Mac installer
2. Install Ollama manually
3. Run the script again

#### "Command not found: python3"

If you see this error:
1. Install Python 3 manually:
   ```bash
   brew install python
   ```
2. Run the script again

#### Ollama Service Not Starting

If the Ollama service doesn't start automatically:
1. Open a new Terminal window
2. Run: `ollama serve`
3. Keep this window open
4. In another Terminal window, run `./startup.sh` again

#### Llama 3 Model Download Issues

If the Llama 3 model download fails:
1. Ensure you have a stable internet connection
2. The model is about 4GB in size, so it may take time to download
3. If it still fails, the application will attempt to download it when needed

## Using Claude Instead of Llama 3

If you prefer to use Claude (requires API key) or can't run Llama 3:

1. Get an API key from [Anthropic](https://console.anthropic.com/)
2. Edit the `.env` file:
   ```bash
   nano .env
   ```
3. Add your Anthropic API key: `ANTHROPIC_API_KEY=your_key_here`
4. Set `USE_CLAUDE=True` in the file

This will make the application use Claude instead of Llama 3, even if Ollama is installed.

## Manual Setup Alternative

If you prefer to set up components manually instead of using the automated script:

1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python 3 if not already installed:
   ```bash
   brew install python
   ```

3. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   ```

4. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Install Ollama:
   ```bash
   brew install ollama
   ```

7. Start Ollama:
   ```bash
   ollama serve
   ```
   (Keep this terminal window open)

8. In a new terminal window, activate the virtual environment again and pull the Llama 3 model:
   ```bash
   source venv/bin/activate
   ollama pull llama3:8b
   ```

9. Create a configuration file:
   ```bash
   cp .env.example .env
   ```

10. Create the DATA directory:
    ```bash
    mkdir -p DATA
    ```

11. Run the application:
    ```bash
    python main.py
    ```

## Additional Resources

- [Ollama Documentation](https://ollama.com/docs)
- [Homebrew Documentation](https://docs.brew.sh)
- [Python Virtual Environments Guide](https://docs.python.org/3/library/venv.html) 