#!/usr/bin/env python3
"""
System utilities for infrastructure setup and verification.
Focuses on checking Ollama installation and setting up required models.
"""

import os
import sys
import subprocess
import platform
import time
import requests
from .formatting import print_info, print_error, print_success, print_warning

def check_ollama_installed():
    """Check if Ollama is installed on the system."""
    try:
        result = subprocess.run(
            ["which", "ollama"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if result.returncode != 0:
            print_error("Ollama is not installed on this system.")
            print_info("Please install Ollama from https://ollama.com")
            return False
            
        print_success("Ollama is installed")
        return True
    except Exception as e:
        print_error(f"Error checking Ollama installation: {e}")
        return False

def check_ollama_running():
    """Check if the Ollama service is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print_success("Ollama service is running")
            return True
        else:
            print_error(f"Ollama service returned unexpected status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Ollama service is not running")
        print_info("Please start Ollama with: ollama serve")
        return False
    except Exception as e:
        print_error(f"Error checking Ollama service: {e}")
        return False

def setup_ollama_model(model_name="llama3"):
    """
    Pull the specified model for Ollama if it's not already available.
    
    Args:
        model_name: The name of the model to pull (default: llama3)
    
    Returns:
        bool: True if the model is ready, False otherwise
    """
    if not check_ollama_running():
        return False
        
    try:
        # Check if the model is already pulled
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = response.json().get("models", [])
        
        # If model exists, we're good to go
        if any(model["name"] == model_name for model in models):
            print_success(f"Model '{model_name}' is available")
            return True
            
        # Pull the model
        print_info(f"Pulling model '{model_name}' (this may take a while)...")
        
        # Use subprocess to pull the model so we can stream the output
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Stream the output
        for line in process.stdout:
            line = line.strip()
            if line:
                print(line)
                
        # Wait for the process to complete
        process.wait()
        
        if process.returncode != 0:
            print_error(f"Failed to pull model '{model_name}'")
            return False
            
        print_success(f"Model '{model_name}' is ready")
        return True
        
    except Exception as e:
        print_error(f"Error setting up Ollama model: {e}")
        return False

def get_ollama_models():
    """Get a list of available Ollama models.
    
    Returns:
        list: List of model names, or empty list if failed
    """
    if not check_ollama_running():
        return []
        
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print_error(f"Failed to get model list: {response.status_code}")
            return []
            
        models = response.json().get("models", [])
        return [model["name"] for model in models]
    except Exception as e:
        print_error(f"Error getting Ollama models: {e}")
        return [] 