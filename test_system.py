#!/usr/bin/env python3
"""
System test for Property Analysis AI Agent
This script tests if all necessary components are properly installed and configured.
"""

import os
import sys
import time
import subprocess
import requests
import importlib.util
import platform
from typing import Dict, List, Tuple

def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_result(test_name: str, success: bool, message: str = "") -> None:
    """Print a test result with consistent formatting."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}{': ' + message if message else ''}")

def check_python_version() -> Tuple[bool, str]:
    """Check if Python version is compatible."""
    current_version = sys.version_info
    required_version = (3, 9)
    
    if current_version >= required_version:
        return True, f"Python {current_version.major}.{current_version.minor}.{current_version.micro}"
    else:
        return False, f"Found Python {current_version.major}.{current_version.minor}.{current_version.micro}, but {required_version[0]}.{required_version[1]}+ is required"

def check_required_packages() -> List[Tuple[str, bool, str]]:
    """Check if all required packages are installed."""
    required_packages = [
        "crewai",
        "pandas",
        "numpy",
        "langchain",
        "langchain_community",
        "dotenv",
        "requests",
        "matplotlib",
        "seaborn",
        "plotly",
        "duckduckgo_search",
        "ollama"
    ]
    
    results = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is not None:
            # Package is installed, try to get its version
            try:
                module = importlib.import_module(package)
                version = getattr(module, "__version__", "unknown version")
                results.append((package, True, version))
            except (ImportError, AttributeError):
                results.append((package, True, "installed"))
        else:
            results.append((package, False, "not installed"))
    
    return results

def check_ollama_installed() -> Tuple[bool, str]:
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
        return True, result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, "Ollama command not found"

def check_ollama_running() -> Tuple[bool, str]:
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return True, "Ollama server is running"
        else:
            return False, f"Ollama server responded with status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Ollama server is not responding: {str(e)}"

def check_ollama_models() -> Tuple[bool, Dict, str]:
    """Check available Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            llama_model_found = any("llama3:70b" in model.get("name", "") for model in models)
            return llama_model_found, models, f"Found {len(models)} models"
        else:
            return False, {}, f"Failed to list models: status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, {}, f"Failed to list models: {str(e)}"

def check_data_file() -> Tuple[bool, str]:
    """Check if the data file exists."""
    data_path = "DATA/master.csv"
    if os.path.exists(data_path):
        size_mb = os.path.getsize(data_path) / (1024 * 1024)
        return True, f"Found ({size_mb:.2f} MB)"
    else:
        return False, "DATA/master.csv not found"

def check_system_resources() -> Dict[str, Tuple[bool, str]]:
    """Check system resources."""
    results = {}
    
    # Check RAM
    try:
        if platform.system() == "Linux":
            with open('/proc/meminfo') as f:
                mem_info = dict(map(str.strip, line.split(':')) for line in f.readlines())
                total_ram_kb = int(mem_info['MemTotal'].split()[0])
                total_ram_gb = total_ram_kb / (1024 * 1024)
                results["RAM"] = (total_ram_gb >= 16, f"{total_ram_gb:.1f} GB")
        elif platform.system() == "Darwin":  # macOS
            mem_str = subprocess.check_output(['sysctl', '-n', 'hw.memsize']).decode('utf-8').strip()
            total_ram_bytes = int(mem_str)
            total_ram_gb = total_ram_bytes / (1024 * 1024 * 1024)
            results["RAM"] = (total_ram_gb >= 16, f"{total_ram_gb:.1f} GB")
        elif platform.system() == "Windows":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            c_ulong = ctypes.c_ulong
            class MEMORYSTATUS(ctypes.Structure):
                _fields_ = [
                    ('dwLength', c_ulong),
                    ('dwMemoryLoad', c_ulong),
                    ('dwTotalPhys', c_ulong),
                    ('dwAvailPhys', c_ulong),
                    ('dwTotalPageFile', c_ulong),
                    ('dwAvailPageFile', c_ulong),
                    ('dwTotalVirtual', c_ulong),
                    ('dwAvailVirtual', c_ulong)
                ]
            memory_status = MEMORYSTATUS()
            memory_status.dwLength = ctypes.sizeof(MEMORYSTATUS)
            kernel32.GlobalMemoryStatus(ctypes.byref(memory_status))
            total_ram_gb = memory_status.dwTotalPhys / (1024 * 1024 * 1024)
            results["RAM"] = (total_ram_gb >= 16, f"{total_ram_gb:.1f} GB")
        else:
            results["RAM"] = (None, "Unknown operating system")
    except Exception as e:
        results["RAM"] = (None, f"Error checking RAM: {str(e)}")
    
    # Check disk space
    try:
        if platform.system() in ["Linux", "Darwin", "Windows"]:
            cwd = os.getcwd()
            total, used, free = shutil.disk_usage(cwd)
            free_gb = free / (1024 * 1024 * 1024)
            results["Disk Space"] = (free_gb >= 50, f"{free_gb:.1f} GB free")
        else:
            results["Disk Space"] = (None, "Unknown operating system")
    except Exception as e:
        results["Disk Space"] = (None, f"Error checking disk space: {str(e)}")
    
    return results

def main():
    """Run all system tests."""
    print_header("Property Analysis System Test")
    print(f"Running tests on {platform.system()} {platform.release()}")
    
    # Check Python version
    python_ok, python_message = check_python_version()
    print_result("Python Version", python_ok, python_message)
    
    # Check packages
    print("\nChecking required packages:")
    package_results = check_required_packages()
    all_packages_ok = True
    for package, success, message in package_results:
        print_result(f"Package: {package}", success, message)
        if not success:
            all_packages_ok = False
    
    # Check Ollama
    print("\nChecking Ollama:")
    ollama_installed, ollama_installed_msg = check_ollama_installed()
    print_result("Ollama Installed", ollama_installed, ollama_installed_msg)
    
    ollama_running, ollama_running_msg = check_ollama_running()
    print_result("Ollama Server", ollama_running, ollama_running_msg)
    
    models_available = False
    if ollama_running:
        models_ok, models, models_msg = check_ollama_models()
        print_result("Llama 3.3 70B Available", models_ok, models_msg)
        
        if not models_ok:
            print("\nAvailable models:")
            if models:
                for model in models:
                    print(f"  - {model.get('name', 'unknown')}")
            else:
                print("  No models found")
        
        models_available = models_ok
    
    # Check data file
    data_ok, data_msg = check_data_file()
    print_result("\nData File", data_ok, data_msg)
    
    # Summarize results
    print_header("Test Summary")
    
    all_ok = python_ok and all_packages_ok and ollama_installed and ollama_running and models_available and data_ok
    
    if all_ok:
        print("✅ All system checks passed! The system is ready to run.")
    else:
        print("❌ Some checks failed. Please address the issues before running the system.")
        
        if not python_ok:
            print("→ Update Python to version 3.9 or higher")
        
        if not all_packages_ok:
            print("→ Install missing packages with: pip install -r requirements.txt")
        
        if not ollama_installed:
            print("→ Install Ollama from: https://ollama.com")
        
        if not ollama_running:
            print("→ Start Ollama with: ollama serve")
        
        if ollama_running and not models_available:
            print("→ Download the required model with: ollama pull llama3:70b")
        
        if not data_ok:
            print("→ Place your property data CSV in the DATA directory as 'master.csv'")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    try:
        import shutil  # For disk space check
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}")
        sys.exit(1) 