#!/usr/bin/env python3
"""
Web Research Demo
This script demonstrates the enhanced web research capabilities of the system.
"""

import os
import json
import sys

# Add parent directory to path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the enhanced web research tool
from enhanced_web_research import EnhancedWebResearchTool

def main():
    """Run a demonstration of the enhanced web research capabilities."""
    print("Enhanced Web Research Demo")
    print("=========================\n")
    
    # Create the research tool
    print("Initializing web research tool...")
    tool = EnhancedWebResearchTool()
    
    if not tool.search_available:
        print("Error: DuckDuckGo search library not available.")
        print("Please install it with: pip install -U duckduckgo-search")
        return 1
    
    # Example property data
    property_data = {
        "City": "Austin",
        "County Name": "Travis",
        "State": "Texas",
        "Zip": "78701"
    }
    
    print(f"\nResearching property location: {property_data['City']}, {property_data['State']}")
    print("This will execute searches across multiple categories...\n")
    
    # Example 1: Category-specific search
    print("Example 1: Economic Development Search")
    print("--------------------------------------")
    economic_results = tool.execute_search_strategy(
        property_data, 
        category="economic_development",
        max_results_per_query=2,
        max_queries=1
    )
    
    print(f"Executed {len(tool.executed_searches)} queries")
    
    for result_set in economic_results.get("search_results", []):
        print(f"\nQuery: {result_set.get('query')}")
        if "aggregate_insights" in result_set:
            print("Insights:")
            for insight in result_set.get("aggregate_insights", []):
                print(f"  - {insight}")
        
        print("\nResults:")
        for i, result in enumerate(result_set.get("results", [])[:2], 1):
            print(f"  {i}. {result.get('title', 'No title')}")
            print(f"     Source: {result.get('source', 'Unknown')}")
            print(f"     Relevance: {result.get('relevance_score', 0.0):.2f}")
            print(f"     Summary: {result.get('summary', 'No summary')[:100]}...")
    
    # Example 2: Multi-category search
    print("\n\nExample 2: Multi-Category Search")
    print("-------------------------------")
    # Reset results for clean demo
    tool.search_results = {
        "search_results": [],
        "meta_analysis": {
            "economic_climate": {"growth_indicators": {}, "detected_trends": []},
            "housing_market": {"detected_trends": []},
            "government_policy": {"detected_trends": []},
            "infrastructure": {"detected_projects": []},
            "community_factors": {"notable_features": []}
        },
        "location_context": tool.search_results["location_context"]
    }
    
    # Execute a comprehensive search
    results = tool.execute_search_strategy(
        property_data,
        max_results_per_query=1,
        max_queries=1
    )
    
    # Show meta-analysis
    meta = tool.get_meta_analysis()
    print("Meta-Analysis:")
    print(json.dumps(meta, indent=2))
    
    # Show search counts by category
    categories = {}
    for result_set in results.get("search_results", []):
        category = result_set.get("category", "unknown")
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print("\nResults by category:")
    for category, count in categories.items():
        print(f"  {category}: {count} result sets")
    
    print("\nEnhanced Web Research Demo completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 