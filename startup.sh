#!/bin/bash
# Land Analysis Crew - Automated Setup and Execution
# For macOS systems - Sets up the environment and runs the application

# ===== Utility Functions =====

# Print styled message with emoji
print_step() {
  echo ""
  echo "🔄 $1"
  echo "---------------------------------------------"
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

# Check if a command exists
has_command() {
  command -v "$1" &> /dev/null
}

# Check if Ollama server is responding
ollama_running() {
  curl -s "http://localhost:11434/api/version" &> /dev/null
}

# Check if a model exists in Ollama
model_exists() {
  ollama list 2>/dev/null | grep -q "$1"
}

# Check and kill existing Ollama processes if needed
kill_existing_ollama() {
  local pid=$(pgrep ollama)
  if [ -n "$pid" ]; then
    print_info "Found existing Ollama process. Closing it to start fresh..."
    kill $pid 2>/dev/null
    sleep 2
  fi
}

# ===== Main Setup Steps =====

# Display welcome banner
show_welcome() {
  clear
  echo ""
  echo "=================================================="
  echo "🏡 Land Analysis Crew - Automated Startup"
  echo "=================================================="
  echo ""
  echo "This script will set up your environment and run"
  echo "the Land Analysis application on your Mac."
  echo ""
  echo "Tasks to be performed:"
  echo "  • Check and install Python if needed"
  echo "  • Set up virtual environment"
  echo "  • Install required dependencies"
  echo "  • Install and configure Ollama"
  echo "  • Download Llama 3 AI model"
  echo "  • Prepare data directories"
  echo "  • Run the application"
  echo ""
  echo "Press Enter to continue or Ctrl+C to exit..."
  read
}

# Step 1: Check Python installation
check_python() {
  print_step "CHECKING PYTHON INSTALLATION"
  
  if has_command python3; then
    python_version=$(python3 --version)
    print_success "Python is installed: $python_version"
    return 0
  else
    print_warning "Python 3 not found"
    
    # Try to install Python with Homebrew
    if has_command brew; then
      print_info "Installing Python via Homebrew..."
      brew install python
      
      if has_command python3; then
        python_version=$(python3 --version)
        print_success "Python installed successfully: $python_version"
        return 0
      else
        print_error "Failed to install Python automatically"
      fi
    else
      print_error "Homebrew not found - required to install Python"
      print_info "Installing Homebrew first..."
      
      /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      
      # Add Homebrew to the current session PATH
      if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
      elif [ -f "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
      fi
      
      if has_command brew; then
        print_success "Homebrew installed successfully"
        print_info "Now installing Python..."
        brew install python
        
        if has_command python3; then
          python_version=$(python3 --version)
          print_success "Python installed successfully: $python_version"
          return 0
        else
          print_error "Failed to install Python"
          print_info "Please install Python 3 manually and run this script again"
          exit 1
        fi
      else
        print_error "Failed to install Homebrew"
        print_info "Please install Python 3 manually and run this script again"
        exit 1
      fi
    fi
  fi
}

# Step 2: Setup virtual environment
setup_venv() {
  print_step "SETTING UP PYTHON VIRTUAL ENVIRONMENT"
  
  if [ -d "venv" ]; then
    print_info "Found existing virtual environment"
  else
    print_info "Creating new virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
      print_error "Failed to create virtual environment"
      print_info "Try running: pip3 install virtualenv"
      exit 1
    fi
    
    print_success "Virtual environment created"
  fi
  
  print_info "Activating virtual environment..."
  source venv/bin/activate
  
  if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
  fi
  
  print_success "Virtual environment activated"
}

# Step 3: Install dependencies
install_dependencies() {
  print_step "INSTALLING PYTHON DEPENDENCIES"
  
  print_info "Upgrading pip..."
  pip install --upgrade pip > /dev/null
  
  print_info "Installing required packages from requirements.txt..."
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
      print_error "Failed to install dependencies"
      exit 1
    fi
    
    print_success "All dependencies installed successfully"
  else
    print_error "requirements.txt not found"
    exit 1
  fi
}

# Step 4: Setup Ollama
setup_ollama() {
  print_step "SETTING UP OLLAMA AI ENGINE"
  
  if has_command ollama; then
    print_success "Ollama is already installed"
  else
    print_info "Installing Ollama..."
    
    if has_command brew; then
      print_info "Installing via Homebrew..."
      brew install ollama
      
      if [ $? -ne 0 ]; then
        print_warning "Homebrew installation failed, trying direct method..."
        curl -fsSL https://ollama.com/install.sh | sh
      fi
    else
      print_info "Installing directly..."
      curl -fsSL https://ollama.com/install.sh | sh
    fi
    
    if has_command ollama; then
      print_success "Ollama installed successfully"
    else
      print_error "Failed to install Ollama"
      print_warning "Will try to use Claude AI instead (requires API key)"
      
      # Check/create .env file for Claude fallback
      if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
          cp .env.example .env
          sed -i '' 's/your_anthropic_api_key_here//' .env
          print_info "Created .env file - you'll need to add an Anthropic API key"
        else
          print_error ".env.example file not found - can't set up Claude fallback"
        fi
      fi
      
      return 1
    fi
  fi
  
  # Ensure Ollama is running
  print_info "Checking if Ollama service is running..."
  
  # Kill any existing Ollama process to start fresh
  kill_existing_ollama
  
  if ! ollama_running; then
    print_info "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    
    # Wait for service to start
    for i in {1..10}; do
      if ollama_running; then
        break
      fi
      print_info "Waiting for Ollama to start... ($i/10)"
      sleep 2
    done
  fi
  
  if ollama_running; then
    print_success "Ollama service is running"
    return 0
  else
    print_error "Failed to start Ollama service"
    print_warning "Will try to use Claude AI instead (requires API key)"
    
    # Check/create .env file for Claude fallback
    if [ ! -f ".env" ]; then
      if [ -f ".env.example" ]; then
        cp .env.example .env
        sed -i '' 's/your_anthropic_api_key_here//' .env
        print_info "Created .env file - you'll need to add an Anthropic API key"
      fi
    fi
    
    return 1
  fi
}

# Step 5: Download Llama model
setup_model() {
  print_step "SETTING UP LLAMA 3 AI MODEL"
  
  if ollama_running; then
    if model_exists "llama3:8b"; then
      print_success "Llama 3 model is already available"
    else
      print_info "Downloading Llama 3 8B model (this may take several minutes)..."
      ollama pull llama3:8b
      
      if model_exists "llama3:8b"; then
        print_success "Llama 3 model downloaded successfully"
      else
        print_error "Failed to download Llama 3 model"
        print_info "The model will be downloaded when you run the application"
      fi
    fi
  else
    print_warning "Skipping model setup - Ollama is not running"
  fi
}

# Step 6: Prepare data directories
prepare_directories() {
  print_step "PREPARING DATA DIRECTORIES"
  
  # Create DATA directory if it doesn't exist
  if [ ! -d "DATA" ]; then
    print_info "Creating DATA directory..."
    mkdir -p DATA
    print_success "DATA directory created"
  else
    print_success "DATA directory already exists"
  fi
  
  # Check for data file
  if [ -f "DATA/master.csv" ]; then
    print_success "Property data file found: DATA/master.csv"
  else
    print_warning "No data file found in DATA directory"
    print_info "You'll need to add your property data as DATA/master.csv before analyzing properties"
  fi
  
  # Create docs directory if it doesn't exist
  if [ ! -d "docs" ]; then
    print_info "Creating docs directory..."
    mkdir -p docs
    print_success "docs directory created"
  else
    print_success "docs directory already exists"
  fi
  
  # Ensure .env file exists
  if [ ! -f ".env" ]; then
    print_info "Creating configuration file from template..."
    if [ -f ".env.example" ]; then
      cp .env.example .env
      print_success "Configuration file created: .env"
    else
      print_warning ".env.example not found - creating minimal .env file"
      echo "ANTHROPIC_API_KEY=" > .env
      echo "ANTHROPIC_MODEL=claude-3-opus-20240229" >> .env
      echo "CREW_TEMPERATURE=0.5" >> .env
    fi
  else
    print_success "Configuration file already exists: .env"
  fi
}

# Step 7: Run the application
run_application() {
  print_step "LAUNCHING LAND ANALYSIS CREW APPLICATION"
  
  print_info "Starting main.py..."
  echo ""
  echo "=================================================="
  python main.py
  app_exit_code=$?
  echo "=================================================="
  echo ""
  
  if [ $app_exit_code -eq 0 ]; then
    print_success "Application completed successfully"
  else
    print_warning "Application exited with code: $app_exit_code"
  fi
}

# Step 8: Cleanup
cleanup() {
  print_step "CLEANING UP"
  
  # Deactivate virtual environment if active
  if [ -n "$VIRTUAL_ENV" ]; then
    print_info "Deactivating virtual environment..."
    deactivate
    print_success "Virtual environment deactivated"
  fi
  
  print_success "Startup process completed"
  echo ""
  echo "To run the application again, just execute:"
  echo "./startup.sh"
  echo ""
}

# ===== Main Execution =====

# Execute all steps in sequence
main() {
  show_welcome
  check_python
  setup_venv
  install_dependencies
  setup_ollama
  setup_model
  prepare_directories
  run_application
  cleanup
}

# Run the script
main 