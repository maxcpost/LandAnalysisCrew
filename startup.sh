#!/bin/bash
# Land Analysis Crew - Environment Setup Script for Mac

# Global variables for cleanup
OLLAMA_PID=""

# Utility Functions
print_header() {
  echo ""
  echo "======================================================================"
  echo "  🏠 Land Analysis Crew - Setup"
  echo "======================================================================"
  echo ""
}

print_success() {
  echo "✅ $1"
}

print_error() {
  echo "❌ $1"
}

print_info() {
  echo "ℹ️  $1"
}

print_warning() {
  echo "⚠️  $1"
}

# Cleanup function
cleanup() {
  print_info "Performing cleanup..."
  
  # Deactivate virtual environment if active
  if [ -n "$VIRTUAL_ENV" ]; then
    deactivate 2>/dev/null
    print_info "Virtual environment deactivated"
  fi
  
  # Don't kill Ollama if it was started successfully - we need it for the application
  echo ""
  print_info "Setup script completed."
  if [ $1 -ne 0 ]; then
    print_warning "Setup encountered some issues. See the messages above for details."
  fi
  
  exit $1
}

# Register cleanup handler for script exit
trap 'cleanup $?' EXIT
trap 'cleanup 1' INT TERM

# Check if a command exists
command_exists() {
  command -v "$1" &> /dev/null
}

# Check if Ollama is running
ollama_running() {
  curl -s http://localhost:11434/api/version &> /dev/null
}

# Check if a model exists in Ollama
model_exists() {
  ollama list 2>/dev/null | grep -q "$1"
}

# Kill existing Ollama process
kill_ollama() {
  if pgrep -x "ollama" > /dev/null; then
    print_info "Found an existing Ollama process."
    print_info "To ensure a clean start, the script needs to restart the Ollama service."
    
    # Ask user for confirmation before killing
    read -p "Is it okay to restart the Ollama service? [Y/n]: " response
    response=${response:-Y}  # Default to Y if empty
    
    if [[ $response =~ ^[Yy]$ ]]; then
      print_info "Stopping existing Ollama process..."
      
      # Try gentle termination first
      pkill ollama
      sleep 3
      
      # Check if process is still running
      if pgrep -x "ollama" > /dev/null; then
        print_warning "Ollama process is still running. Attempting to force stop..."
        pkill -9 ollama
        sleep 2
        
        # If still running, give user options
        if pgrep -x "ollama" > /dev/null; then
          print_error "Could not stop the existing Ollama process."
          print_info "This could be because:"
          print_info "1. The process is being used by another application"
          print_info "2. You don't have permission to stop this process"
          print_info "3. The process is in an inconsistent state"
          
          echo ""
          print_info "You have the following options:"
          echo "1) Continue with the existing Ollama process"
          echo "2) Try to manually stop Ollama and then continue"
          echo "3) Exit the script"
          
          read -p "Choose an option (1-3): " option
          case $option in
            1)
              print_info "Continuing with the existing Ollama process."
              print_warning "This might cause issues if the process is not functioning correctly."
              return 0
              ;;
            2)
              print_info "Please open a new terminal and run: 'sudo pkill -9 ollama'"
              print_info "After stopping the process, press Enter to continue..."
              read
              
              # Check again if process was stopped
              if pgrep -x "ollama" > /dev/null; then
                print_error "Ollama process is still running. Cannot continue safely."
                return 1
              else
                print_success "Ollama process successfully stopped."
                return 0
              fi
              ;;
            *)
              print_info "Exiting the script. Please restart after manually stopping Ollama."
              print_info "You can stop Ollama with: 'sudo pkill -9 ollama'"
              exit 1
              ;;
          esac
        fi
      fi
      
      print_success "Ollama process stopped"
    else
      print_info "Continuing with the existing Ollama process."
      print_warning "This might cause issues if the process is in an inconsistent state."
    fi
  fi
  
  return 0
}

# Display welcome message
welcome() {
  print_header
  print_info "Welcome to Land Analysis Crew - Environment Setup"
  print_info "This script will set up your environment for analyzing properties."
  echo ""
}

# Check for Python installation
check_python() {
  print_info "Checking Python installation..."
  if command_exists python3; then
    python_version=$(python3 --version)
    print_success "Python is installed: $python_version"
    return 0
  else
    print_error "Python 3 is not installed!"
    print_info "Installing Python using Homebrew..."
    
    # Check/install Homebrew first
    if ! command_exists brew; then
      print_info "Installing Homebrew first..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      if [ $? -ne 0 ]; then
        print_error "Failed to install Homebrew"
        print_info "Please install Homebrew manually from https://brew.sh/"
        print_info "Then run this script again"
        return 1
      fi
      print_success "Homebrew installed"
      
      # Add Homebrew to PATH for this session if installed to default location
      if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
      elif [ -f "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
      fi
    fi
    
    # Now install Python
    brew install python
    if [ $? -ne 0 ]; then
      print_error "Failed to install Python"
      print_info "Please install Python 3 manually and run this script again"
      return 1
    fi
    print_success "Python installed"
    return 0
  fi
}

# Set up Python virtual environment
setup_venv() {
  print_info "Setting up Python virtual environment..."
  if [ -d "venv" ]; then
    print_info "Virtual environment already exists"
  else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
      print_error "Failed to create virtual environment"
      return 1
    fi
    print_success "Virtual environment created"
  fi
  
  # Activate virtual environment and install dependencies
  print_info "Installing dependencies..."
  source venv/bin/activate
  pip install --upgrade pip > /dev/null
  pip install -r requirements.txt
  # Ensure DuckDuckGo Search is installed
  if ! pip install -U duckduckgo-search; then
    print_warning "Failed to install duckduckgo-search package."
    print_info "The application will run with limited web search functionality."
    print_info "You can manually install it later with: pip install -U duckduckgo-search"
  else
    print_success "DuckDuckGo search package installed successfully"
  fi
  
  # Check if any critical dependencies failed
  if [ $? -ne 0 ]; then
    print_error "Failed to install core dependencies"
    return 1
  fi
  print_success "Dependencies installed"
  return 0
}

# Setup Ollama
setup_ollama() {
  print_info "Setting up Ollama..."
  if command_exists ollama; then
    print_success "Ollama is already installed"
  else
    # Check for Homebrew
    if ! command_exists brew; then
      print_info "Installing Homebrew..."
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      
      # Add Homebrew to PATH for this session if installed to default location
      if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
      elif [ -f "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
      fi
    fi
    
    # Install Ollama
    print_info "Installing Ollama..."
    brew install ollama
    if [ $? -ne 0 ]; then
      print_warning "Failed to install via Homebrew, trying alternative method..."
      curl -fsSL https://ollama.com/install.sh | sh
      if [ $? -ne 0 ]; then
        print_error "Failed to install Ollama"
        print_info "The application requires Ollama to run. Please install it manually from https://ollama.com/"
        exit 1
      else
        print_success "Ollama installed"
      fi
    else
      print_success "Ollama installed via Homebrew"
    fi
  fi
  
  # Stop any existing Ollama process
  kill_ollama
  
  # Check if Ollama is already running
  print_info "Setting up Ollama service..."
  if ollama_running; then
    print_success "Ollama service is already running"
    # Get the PID for reference
    OLLAMA_PID=$(pgrep -x "ollama")
    print_info "Using existing Ollama process (PID: $OLLAMA_PID)"
  else
    # Start a new Ollama process
    print_info "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    
    # Wait for Ollama to start with improved feedback
    print_info "Waiting for Ollama service to start..."
    max_wait=30  # Maximum wait time in seconds
    wait_count=0
    
    while [ $wait_count -lt $max_wait ]; do
      if ollama_running; then
        print_success "Ollama service is running (PID: $OLLAMA_PID)"
        break
      fi
      
      # Show progress
      if [ $(($wait_count % 5)) -eq 0 ]; then
        echo -n -e "\n   Still waiting... ($wait_count/$max_wait seconds)"
      else
        echo -n "."
      fi
      
      sleep 1
      wait_count=$((wait_count + 1))
    done
  fi
  
  # If Ollama is still not running after the wait period
  if ! ollama_running; then
    print_error "Failed to start Ollama service"
    print_info "Attempting to diagnose the issue..."
    
    # Check if process is still running
    if ps -p $OLLAMA_PID > /dev/null 2>&1; then
      print_info "The Ollama process (PID: $OLLAMA_PID) is running but not responding to API requests."
      print_info "This could be because:"
      print_info "1. Another application is using port 11434"
      print_info "2. The Ollama service is in a bad state"
    else
      print_info "The Ollama process is not running. It may have crashed on startup."
    fi
    
    # Check for common issues
    if command_exists lsof; then
      print_info "Checking if another process is using Ollama's port (11434)..."
      PORT_PROCESS=$(lsof -i :11434 | grep LISTEN)
      if [ -n "$PORT_PROCESS" ]; then
        print_info "Found process using port 11434:"
        echo "$PORT_PROCESS"
      fi
    fi
    
    # Offer potential solutions
    print_info "Please try the following:"
    echo "1) Manually start Ollama in another terminal: 'ollama serve'"
    echo "2) Check if another Ollama instance is already running: 'ps aux | grep ollama'"
    echo "3) Restart your computer and try again"
    
    # Ask if they want to try running without restarting
    read -p "Do you want to try continuing anyway? (not recommended) [y/N]: " continue_anyway
    
    if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
      print_info "Exiting setup. Please fix the Ollama issues and try again."
      exit 1
    else
      print_warning "Continuing without a confirmed working Ollama service."
      print_info "The application may not function correctly!"
    fi
  fi
  
  # Check and download Llama 3.3 model
  print_info "Checking Llama 3.3 70B model..."
  
  # First verify that Ollama service is responding
  if ! ollama_running; then
    print_warning "Ollama service is not responding. Cannot verify model availability."
    print_warning "The application might not work correctly if the model is not available."
    print_info "You can manually check with 'ollama list' in another terminal."
    
    # Ask if they want to continue anyway
    read -p "Do you want to continue without checking the model? [y/N]: " skip_model_check
    if [[ ! $skip_model_check =~ ^[Yy]$ ]]; then
      print_info "Exiting setup. Please ensure Ollama is running and try again."
      exit 1
    else
      print_warning "Continuing without model verification. The application may fail later."
      return 0
    fi
  fi
  
  # Check if model exists
  MODEL_CHECK_RESULT=0
  if ! ollama list 2>/dev/null | grep -q "llama3:70b"; then
    print_info "Llama 3.3 70B model is not found. Need to download it."
    MODEL_CHECK_RESULT=1
  else
    print_success "Llama 3.3 70B model is already available"
    return 0
  fi
  
  # Only proceed with download if model check indicates it's needed
  if [ $MODEL_CHECK_RESULT -eq 1 ]; then
    # Check disk space before downloading - Llama 3.3 70B requires about 45GB
    free_space=$(df -h . | awk 'NR==2 {print $4}')
    print_info "Disk space available: $free_space"
    
    # Check if we have less than 50GB available (rough estimate)
    if df -k . | awk 'NR==2 {exit ($4 < 50000000)}'; then
      print_warning "Low disk space might cause problems during model download."
      print_info "Llama 3.3 70B requires approximately 45GB of disk space."
      read -p "Continue with download anyway? [Y/n]: " response
      response=${response:-Y}  # Default to Y if empty
      
      if [[ ! $response =~ ^[Yy]$ ]]; then
        print_info "Download cancelled. Please free up disk space and try again."
        exit 1
      fi
    fi
    
    print_info "Downloading Llama 3.3 70B model (this will take a significant amount of time)..."
    print_info "Download size: ~45GB. Please be patient and ensure a stable internet connection."
    
    # Try the download with timeout and retry logic
    MAX_RETRIES=2
    RETRY_COUNT=0
    DOWNLOAD_SUCCESS=false
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$DOWNLOAD_SUCCESS" = "false" ]; do
      # Show a progress spinner during download
      (ollama pull llama3:70b > /dev/null 2>&1) & 
      download_pid=$!
      
      spin='-\|/'
      i=0
      elapsed=0
      timeout=3600  # 60 minutes timeout for large model
      
      while kill -0 $download_pid 2>/dev/null; do
        i=$(( (i+1) % 4 ))
        printf "\r  Downloading... %s (elapsed: %d seconds)" "${spin:$i:1}" $elapsed
        sleep 1
        elapsed=$((elapsed + 1))
        
        # Check for timeout
        if [ $elapsed -gt $timeout ]; then
          print_warning "Download is taking too long. Killing process..."
          kill -9 $download_pid 2>/dev/null
          break
        fi
      done
      printf "\r                                                 \n"
      
      # Check if download completed successfully by waiting for process completion
      wait $download_pid
      download_status=$?
      
      if [ $download_status -eq 0 ] && ollama list 2>/dev/null | grep -q "llama3:70b"; then
        print_success "Llama 3.3 70B model downloaded successfully!"
        DOWNLOAD_SUCCESS=true
      else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
          print_warning "Download attempt $RETRY_COUNT failed. Retrying..."
          sleep 3
        fi
      fi
    done
    
    if [ "$DOWNLOAD_SUCCESS" = "false" ]; then
      print_error "Failed to download Llama 3.3 70B model after $MAX_RETRIES attempts"
      print_info "Common causes include:"
      print_info "1. Network connectivity issues"
      print_info "2. Insufficient disk space"
      print_info "3. Ollama service interrupted"
      print_info ""
      print_info "Options:"
      echo "1) Continue without the model (application will likely fail)"
      echo "2) Exit and try again later"
      
      read -p "Choose an option (1-2): " option
      if [ "$option" = "1" ]; then
        print_warning "Continuing without the required model. The application will likely fail."
        return 0
      else
        print_info "Exiting setup. Try again later with:"
        print_info "  1. Better internet connection"
        print_info "  2. More disk space"
        print_info "  3. Or run 'ollama pull llama3:70b' manually before running this script"
        exit 1
      fi
    fi
  fi
  
  return 0
}

# Validate CSV file structure
validate_csv() {
  csv_file="$1"
  if [ ! -f "$csv_file" ]; then
    return 1
  fi
  
  print_info "Validating CSV file structure..."
  # Read the header row and check for essential columns
  header=$(head -n 1 "$csv_file")
  
  # Check for critical columns - adjust as needed
  essential_columns=("StockNumber" "Property Address" "City" "State" "For Sale Price" "Land Area (AC)")
  missing_columns=()
  
  for col in "${essential_columns[@]}"; do
    if ! echo "$header" | grep -q "$col"; then
      missing_columns+=("$col")
    fi
  done
  
  if [ ${#missing_columns[@]} -gt 0 ]; then
    print_warning "The CSV file is missing the following essential columns:"
    for col in "${missing_columns[@]}"; do
      print_info "  - $col"
    done
    return 1
  fi
  
  # Check number of columns as a sanity check (the file should have many columns)
  column_count=$(echo "$header" | tr ',' '\n' | wc -l)
  if [ "$column_count" -lt 20 ]; then
    print_warning "The CSV file appears to have only $column_count columns."
    print_warning "The application expects a detailed property dataset with many columns."
    return 1
  fi
  
  print_success "CSV file structure appears valid"
  return 0
}

# Prepare data directories
setup_data() {
  print_info "Setting up data directories..."
  mkdir -p DATA docs
  
  # Create a clean .env file that forces Ollama usage
  print_info "Creating configuration file..."
  echo "# Property Analysis Crew Configuration" > .env
  echo "CREW_TEMPERATURE=0.5" >> .env
  print_success "Configuration file created"
  print_info "Configuration set to use Llama 3 (local model) via Ollama"
  
  # Check for data file
  if [ -f "DATA/master.csv" ]; then
    print_success "Property data file found: DATA/master.csv"
    
    # Validate the CSV structure
    if ! validate_csv "DATA/master.csv"; then
      print_warning "The CSV file found doesn't match the expected format."
      print_info "You might encounter errors when running the application."
      print_info "Consider checking the file structure and column names."
    fi
  else
    print_warning "No property data file found in DATA directory."
    print_info "The application requires a 'master.csv' file to analyze properties."
    
    # Check if we have a sample data file
    if [ -f "sample_data/master.csv" ]; then
      print_info "Found sample data file. Would you like to use it for testing?"
      read -p "Copy sample data to DATA directory? [Y/n]: " response
      response=${response:-Y}  # Default to Y if empty
      
      if [[ $response =~ ^[Yy]$ ]]; then
        cp sample_data/master.csv DATA/
        print_success "Sample data copied to DATA/master.csv"
        
        # Validate the sample data
        validate_csv "DATA/master.csv"
      else
        print_info "You'll need to add your property data as 'master.csv' in the DATA directory before analyzing properties."
      fi
    else
      print_info "You'll need to add your property data as 'master.csv' in the DATA directory before analyzing properties."
      print_info "The file should contain property listings with columns for location, price, and other attributes."
    fi
  fi
  
  print_success "Data directories prepared"
}

# Main function
main() {
  # Display welcome message
  welcome
  
  # Check for Python
  check_python
  if [ $? -ne 0 ]; then
    print_error "Python setup failed. Please install Python 3 manually and run this script again."
    exit 1
  fi
  
  # Set up virtual environment
  setup_venv
  if [ $? -ne 0 ]; then
    print_error "Virtual environment setup failed."
    exit 1
  fi
  
  # Set up Ollama
  setup_ollama
  
  # Prepare data directories
  setup_data
  
  # Setup complete
  print_header
  print_success "Environment setup complete!"
  print_info "Your environment is now ready to run the Land Analysis Crew application."
  print_info "To run the application, use the following command:"
  echo ""
  echo "    python main.py"
  echo ""
  print_info "When you're done, you can exit the virtual environment with:"
  echo ""
  echo "    deactivate"
  echo ""
  print_info "Activating virtual environment now..."
  source venv/bin/activate
}

# Run the main function
main 