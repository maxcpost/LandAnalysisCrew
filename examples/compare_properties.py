#!/usr/bin/env python3
"""
Example script that demonstrates comparing multiple properties.
This script loads several properties from the dataset and runs a comparison analysis.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import project modules
from src.data.loader import PropertyDataLoader
from src.models.crew import PropertyAnalysisCrew
from src.utils.system import check_ollama_installed, check_ollama_running, setup_ollama_model
from src.utils.formatting import print_header, print_error, print_info
from src.utils.llm import setup_llm as setup_llm_util

# Load environment variables
load_dotenv()

def setup_llm():
    """Set up the language model to be used."""
    # Use our centralized LLM utility module with CrewAI compatibility
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true" or "--use-mock" in sys.argv
    
    return setup_llm_util(
        use_mock=use_mock,
        for_crewai=True,  # Use the CrewAI-compatible adapter
        model_name=os.getenv("OLLAMA_MODEL", "llama3"),
        base_url=os.getenv("OLLAMA_API_BASE", "http://localhost:11434"),
        temperature=float(os.getenv("CREW_TEMPERATURE", "0.7")),
        verbose=True
    )

def main():
    """Main function to run the property comparison."""
    # Check command-line arguments
    if len(sys.argv) < 3:
        print("Usage: python compare_properties.py <stock_number1> <stock_number2> [stock_number3 ...]")
        return 1
        
    stock_numbers = sys.argv[1:]
    
    # Load the property data
    try:
        loader = PropertyDataLoader()
        properties_data = []
        
        for stock_number in stock_numbers:
            property_data = loader.get_property_data(stock_number)
            
            if property_data is None:
                print_error(f"Property with stock number {stock_number} not found.")
                return 1
                
            properties_data.append(property_data)
            
    except Exception as e:
        print_error(f"Error loading property data: {e}")
        return 1
    
    # Set up the language model
    llm = setup_llm()
    
    # Create the property analysis crew with the first property (needed for initialization)
    crew = PropertyAnalysisCrew(properties_data[0], llm=llm)
    
    try:
        # Run the comparison analysis
        comparison_report = crew.compare_properties(properties_data)
        
        # Print the comparison report
        print_header("PROPERTY COMPARISON REPORT")
        print(comparison_report)
        
        print_info("Full comparison report saved to: outputs/reports/property_comparison.md")
        return 0
        
    except Exception as e:
        print_error(f"Error comparing properties: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 