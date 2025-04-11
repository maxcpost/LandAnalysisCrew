#!/usr/bin/env python3
"""
Main entry point for the Land Analysis Crew application.
This module provides the command-line interface for property analysis.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Import components from the project
from src.data.loader import PropertyDataLoader
from src.utils.system import check_ollama_installed, check_ollama_running, setup_ollama_model
from src.utils.formatting import print_header, print_subheader, print_agent

# Load environment variables
load_dotenv()

def show_help():
    """Display help information about the application."""
    print_header("PROPERTY ANALYSIS SYSTEM HELP")
    print("\nThis tool analyzes properties for high-density, master-planned community development")
    print("\nUSAGE:")
    print("  python -m src.main [options]")
    print("\nOPTIONS:")
    print("  --help, -h     Show this help message")
    print("  --list         List available properties")
    print("  --search TEXT  Search for properties by address or city")
    print("  --stock NUM    Analyze the property with the given stock number")
    print("\nEXAMPLES:")
    print("  python -m src.main --list")
    print("  python -m src.main --search \"Austin\"")
    print("  python -m src.main --stock 12345")
    print("\nFor more information, see the documentation.")
    
def list_properties(loader):
    """List available properties."""
    print_header("AVAILABLE PROPERTIES")
    
    properties = loader.get_property_list()
    total_count = len(properties)
    
    if total_count == 0:
        print("No properties found in the dataset.")
        return
    
    # Show first 20 properties for brevity
    display_count = min(20, total_count)
    for i, prop in enumerate(properties[:display_count], 1):
        try:
            print(f"{i}. Stock# {prop['StockNumber']} - {prop.get('Property Address', 'N/A')}, {prop.get('City', 'N/A')}, {prop.get('State', 'N/A')}")
        except KeyError:
            print(f"{i}. Stock# {prop.get('StockNumber', 'Unknown')} - (Missing address information)")
    
    if total_count > display_count:
        print(f"\n...and {total_count - display_count} more properties")
    
    print(f"\nTotal properties: {total_count}")

def search_properties(loader, query):
    """Search for properties matching the query."""
    print_header(f"PROPERTY SEARCH: {query}")
    
    results = loader.search_properties(query)
    if not results:
        print(f"No properties found matching '{query}'.")
        return
    
    print(f"Found {len(results)} matching properties:")
    
    for i, prop in enumerate(results, 1):
        print(f"{i}. Stock# {prop['StockNumber']} - {prop.get('Property Address', 'N/A')}, {prop.get('City', 'N/A')}, {prop.get('State', 'N/A')}")

def analyze_property(loader, stock_number):
    """Analyze a property by stock number."""
    print_header(f"ANALYZING PROPERTY: Stock# {stock_number}")
    
    # Get property data
    property_data = loader.get_property_data(stock_number)
    if not property_data:
        print(f"Property with stock number {stock_number} not found.")
        return
    
    # Show basic information
    print(f"Property: {property_data.get('Property Address', 'N/A')}")
    print(f"Location: {property_data.get('City', 'N/A')}, {property_data.get('State', 'N/A')} {property_data.get('Zip', 'N/A')}")
    print(f"Land Area: {property_data.get('Land Area (AC)', 'N/A')} acres")
    print(f"For Sale Price: ${property_data.get('For Sale Price', 'N/A')}")
    print("")
    
    # This is a stub - in the full implementation, we would:
    # 1. Set up the agent crew
    # 2. Run the analysis tasks
    # 3. Generate the report
    # For now, we'll just indicate that this is a placeholder
    print("Full property analysis would be performed here in the complete implementation.")
    print("This would include running the agent crew with all specialized agents.")

def main():
    """Main function to run the property analysis system."""
    # Check for command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h', 'help', '?']:
            show_help()
            return 0
            
        # Initialize the data loader
        try:
            loader = PropertyDataLoader()
        except Exception as e:
            print(f"Error: {e}")
            print("\nPlease ensure:")
            print("1. You have run the startup.sh script first")
            print("2. You have placed your property data CSV in the DATA directory as 'master.csv'")
            return 1
            
        # Handle list command
        if arg == '--list':
            list_properties(loader)
            return 0
            
        # Handle search command
        if arg == '--search' and len(sys.argv) > 2:
            query = sys.argv[2]
            search_properties(loader, query)
            return 0
            
        # Handle stock number command
        if arg == '--stock' and len(sys.argv) > 2:
            stock_number = sys.argv[2]
            analyze_property(loader, stock_number)
            return 0
            
        # Unknown command
        print(f"Unknown command: {arg}")
        print("Use --help to see available commands.")
        return 1
        
    # No arguments, show help
    show_help()
    return 0

if __name__ == "__main__":
    sys.exit(main()) 