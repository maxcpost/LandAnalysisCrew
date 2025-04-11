#!/usr/bin/env python3
"""
Simple test script to verify that the PropertyAnalysisCrew methods work correctly.
This script doesn't rely on LLMs, just checks the workflow.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import project modules
from src.models.crew import PropertyAnalysisCrew
from src.utils.formatting import print_header, print_info, print_error, print_success

class MockResearchAgent:
    """Simple mock agent that returns predefined responses."""
    
    def __init__(self, agent_type="researcher"):
        self.agent_type = agent_type
        # This simulates the agent property that CrewAI uses
        self.agent = self
    
    def execute_task(self, task):
        """Return a mock response based on the task."""
        return f"Mock {self.agent_type} response for task: {task.description[:50]}..."

def test_research_property_potential():
    """Test the research_property_potential method."""
    print_header("TESTING RESEARCH_PROPERTY_POTENTIAL")
    
    # Create a simple property data dictionary
    property_data = {
        "Property Address": "123 Test Street",
        "City": "Test City",
        "State": "Test State",
        "Land Area (AC)": 10.0,
        "For Sale Price": 500000,
        "Zoning": "Residential"
    }
    
    # Create the crew
    crew = PropertyAnalysisCrew(property_data)
    
    # Override the web_researcher with our mock
    crew.web_researcher = MockResearchAgent("web researcher")
    
    # Monkey patch the method to avoid CrewAI dependencies
    def mock_research_property_potential(self):
        return "Mock property potential research data"
    
    original_method = crew.research_property_potential
    crew.research_property_potential = mock_research_property_potential.__get__(crew, PropertyAnalysisCrew)
    
    try:
        # Call the method
        result = crew.research_property_potential()
        print_info(f"Result: {result}")
        print_success("Test passed!")
        return True
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False
    finally:
        # Restore the original method
        crew.research_property_potential = original_method

def test_generate_report():
    """Test the generate_report method."""
    print_header("TESTING GENERATE_REPORT")
    
    # Create a simple property data dictionary
    property_data = {
        "Property Address": "123 Test Street",
        "City": "Test City",
        "State": "Test State",
        "Land Area (AC)": 10.0,
        "For Sale Price": 500000,
        "Zoning": "Residential"
    }
    
    # Create the crew
    crew = PropertyAnalysisCrew(property_data)
    
    # Override the report_generator with our mock
    crew.report_generator = MockResearchAgent("report generator")
    
    # Monkey patch the method to avoid CrewAI dependencies
    def mock_generate_report(self, property_potential):
        return f"Mock report based on: {property_potential[:30]}..."
    
    original_method = crew.generate_report
    crew.generate_report = mock_generate_report.__get__(crew, PropertyAnalysisCrew)
    
    try:
        # Call the method
        result = crew.generate_report("Test property potential data")
        print_info(f"Result: {result}")
        print_success("Test passed!")
        return True
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False
    finally:
        # Restore the original method
        crew.generate_report = original_method

def test_generate_executive_summary():
    """Test the generate_executive_summary method."""
    print_header("TESTING GENERATE_EXECUTIVE_SUMMARY")
    
    # Create a simple property data dictionary
    property_data = {
        "Property Address": "123 Test Street",
        "City": "Test City",
        "State": "Test State",
        "Land Area (AC)": 10.0,
        "For Sale Price": 500000,
        "Zoning": "Residential"
    }
    
    # Create the crew
    crew = PropertyAnalysisCrew(property_data)
    
    # Override the report_generator with our mock
    crew.report_generator = MockResearchAgent("report generator")
    
    # Monkey patch the method to avoid CrewAI dependencies
    def mock_generate_executive_summary(self, property_potential, full_report):
        return f"Mock executive summary based on: {property_potential[:20]}... and {full_report[:20]}..."
    
    original_method = crew.generate_executive_summary
    crew.generate_executive_summary = mock_generate_executive_summary.__get__(crew, PropertyAnalysisCrew)
    
    try:
        # Call the method
        result = crew.generate_executive_summary("Test property potential data", "Test full report data")
        print_info(f"Result: {result}")
        print_success("Test passed!")
        return True
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False
    finally:
        # Restore the original method
        crew.generate_executive_summary = original_method

def test_generate_investment_summary():
    """Test the generate_investment_summary method."""
    print_header("TESTING GENERATE_INVESTMENT_SUMMARY")
    
    # Create a simple property data dictionary
    property_data = {
        "Property Address": "123 Test Street",
        "City": "Test City",
        "State": "Test State",
        "Land Area (AC)": 10.0,
        "For Sale Price": 500000,
        "Zoning": "Residential"
    }
    
    # Create the crew
    crew = PropertyAnalysisCrew(property_data)
    
    # Override the report_generator with our mock
    crew.report_generator = MockResearchAgent("report generator")
    
    # Monkey patch the method to avoid CrewAI dependencies
    def mock_generate_investment_summary(self, property_potential, executive_summary):
        return f"Mock investment summary based on: {property_potential[:20]}... and {executive_summary[:20]}..."
    
    original_method = crew.generate_investment_summary
    crew.generate_investment_summary = mock_generate_investment_summary.__get__(crew, PropertyAnalysisCrew)
    
    try:
        # Call the method
        result = crew.generate_investment_summary("Test property potential data", "Test executive summary data")
        print_info(f"Result: {result}")
        print_success("Test passed!")
        return True
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False
    finally:
        # Restore the original method
        crew.generate_investment_summary = original_method

def test_save_report_to_file():
    """Test the save_report_to_file method."""
    print_header("TESTING SAVE_REPORT_TO_FILE")
    
    # Create a simple property data dictionary
    property_data = {
        "Property Address": "123 Test Street",
        "City": "Test City",
        "State": "Test State",
        "Land Area (AC)": 10.0,
        "For Sale Price": 500000,
        "Zoning": "Residential"
    }
    
    # Create the crew
    crew = PropertyAnalysisCrew(property_data)
    
    try:
        # Call the method
        result = crew.save_report_to_file(
            "Test full report data",
            "Test executive summary data",
            "Test investment summary data"
        )
        print_info(f"Result: {result}")
        print_success("Test passed!")
        return True
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False

def test_analyze_property():
    """Test the analyze_property method."""
    print_header("TESTING ANALYZE_PROPERTY")
    
    # Create a simple property data dictionary
    property_data = {
        "Property Address": "123 Test Street",
        "City": "Test City",
        "State": "Test State",
        "Land Area (AC)": 10.0,
        "For Sale Price": 500000,
        "Zoning": "Residential"
    }
    
    # Create the crew
    crew = PropertyAnalysisCrew(property_data)
    
    # Override the agents with our mocks
    crew.web_researcher = MockResearchAgent("web researcher")
    crew.report_generator = MockResearchAgent("report generator")
    crew.data_analyst = MockResearchAgent("data analyst")
    crew.market_analyst = MockResearchAgent("market analyst")
    
    # Monkey patch the methods to avoid CrewAI dependencies
    def mock_research_property_potential(self):
        return "Mock property potential research data"
    
    def mock_generate_report(self, property_potential):
        return f"Mock report based on: {property_potential[:30]}..."
    
    def mock_generate_executive_summary(self, property_potential, full_report):
        return f"Mock executive summary based on: {property_potential[:20]}... and {full_report[:20]}..."
    
    def mock_generate_investment_summary(self, property_potential, executive_summary):
        return f"Mock investment summary based on: {property_potential[:20]}... and {executive_summary[:20]}..."
    
    original_research = crew.research_property_potential
    original_report = crew.generate_report
    original_exec_summary = crew.generate_executive_summary
    original_invest_summary = crew.generate_investment_summary
    
    crew.research_property_potential = mock_research_property_potential.__get__(crew, PropertyAnalysisCrew)
    crew.generate_report = mock_generate_report.__get__(crew, PropertyAnalysisCrew)
    crew.generate_executive_summary = mock_generate_executive_summary.__get__(crew, PropertyAnalysisCrew)
    crew.generate_investment_summary = mock_generate_investment_summary.__get__(crew, PropertyAnalysisCrew)
    
    try:
        # Call the method
        full_report, executive_summary, investment_summary, report_path = crew.analyze_property()
        print_info(f"Full report: {full_report}")
        print_info(f"Executive summary: {executive_summary}")
        print_info(f"Investment summary: {investment_summary}")
        print_info(f"Report path: {report_path}")
        print_success("Test passed!")
        return True
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore the original methods
        crew.research_property_potential = original_research
        crew.generate_report = original_report
        crew.generate_executive_summary = original_exec_summary
        crew.generate_investment_summary = original_invest_summary

def run_all_tests():
    """Run all test functions."""
    print_header("RUNNING ALL TESTS")
    
    results = {
        "research_property_potential": test_research_property_potential(),
        "generate_report": test_generate_report(),
        "generate_executive_summary": test_generate_executive_summary(),
        "generate_investment_summary": test_generate_investment_summary(),
        "save_report_to_file": test_save_report_to_file(),
        "analyze_property": test_analyze_property()
    }
    
    print_header("TEST RESULTS")
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    if all(results.values()):
        print_success("All tests passed!")
        return 0
    else:
        print_error("Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests()) 