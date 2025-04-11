from crewai import Agent, Task, Crew, Process
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import subprocess
import sys
import time
import requests
import re
from datetime import datetime
import textwrap
import json
from typing import Any, Dict, List, Optional, Union

# Visualization libraries (for Report Generation Agent)
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Import enhanced web research tool
from enhanced_web_research import WebResearchTool, EnhancedWebResearchTool

# Load environment variables
load_dotenv()

# Constants
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:70b"  # Using Llama 3.3 70B model
CREW_TEMPERATURE = 0.1  # Lower temperature for more focused, deterministic responses

# This is the key issue - litellm needs the provider prefix
# Using two separate constants: one for CrewAI (prefixed) and one for Ollama API (just model name)
LITELLM_MODEL = f"ollama/{OLLAMA_MODEL}"  # With required provider prefix for LiteLLM

# Force disable any potential Anthropic or OpenAI API usage
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""

# Make sure we're using local models only
os.environ["CREWAI_LOCAL_MODEL"] = "true"
os.environ["CREWAI_FORCE_LOCAL"] = "true"
os.environ["CREWAI_LLM"] = "ollama"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""

# Terminal colors for better formatting
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'

# Since we can't use the callback system, we'll create simpler formatting functions
def print_header(text):
    """Print a formatted header."""
    if not supports_color():
        print(f"\n===== {text} =====")
        return
        
    width = min(os.get_terminal_size().columns, 80)
    print("\n" + "=" * width)
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(width)}{Colors.ENDC}")
    print("=" * width)

def print_subheader(text):
    """Print a formatted subheader."""
    if not supports_color():
        print(f"\n----- {text} -----")
        return
        
    width = min(os.get_terminal_size().columns, 80)
    print("\n" + "-" * width)
    print(f"{Colors.BOLD}{text.center(width)}{Colors.ENDC}")
    print("-" * width)

def print_agent(role, message, color=None):
    """Print an agent message with proper formatting."""
    if not supports_color():
        print(f"\n[{role}]: {message}")
        return
        
    if color is None:
        color = Colors.BOLD
        
    width = min(os.get_terminal_size().columns, 80)
    wrapped_text = textwrap.fill(
        message, 
        width=width - 4,
        initial_indent=f"{color}💬 {role}: {Colors.ENDC}",
        subsequent_indent="   "
    )
    print(wrapped_text)
    print("")  # Add a blank line for readability

def print_task(task_num, task_name):
    """Print a task header."""
    print_subheader(f"TASK {task_num}: {task_name}")

# Function to check if a terminal supports colors
def supports_color():
    """Check if the terminal supports colors."""
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except Exception:
        # If there's any error, assume no color support
        return False

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        subprocess.run(["ollama", "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def check_ollama_running():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except:
        return False

def setup_ollama_model():
    """Ensure Ollama model is available"""
    try:
        # Force LangChain and CrewAI to use local models only
        os.environ["CREWAI_LOCAL_MODEL"] = "true" 
        os.environ["CREWAI_FORCE_LOCAL"] = "true"
        
        # Set model name and temperature
        os.environ["OLLAMA_MODEL"] = OLLAMA_MODEL
        
        # Check if model is available
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name") for model in models]
            
            if OLLAMA_MODEL not in model_names:
                print(f"\nDownloading {OLLAMA_MODEL} model, this may take several minutes (or even hours)...")
                print(f"The model is approximately 45GB. Please be patient.")
                pull_response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/pull",
                    json={"name": OLLAMA_MODEL}
                )
                if pull_response.status_code != 200:
                    print(f"Warning: Could not download {OLLAMA_MODEL} model.")
                    print(f"Please run 'ollama pull {OLLAMA_MODEL}' manually.")
            else:
                print(f"\nModel {OLLAMA_MODEL} is already available.")
        else:
            print("\nWarning: Could not check available models.")
            print(f"Make sure Ollama is running on {OLLAMA_BASE_URL}")
    except Exception as e:
        print(f"\nError setting up Ollama model: {e}")
        print("Continuing with Ollama anyway, but you may need to pull the model manually.")

class PropertyAnalyzer:
    def __init__(self, csv_path="DATA/master.csv"):
        """Initialize the property analyzer with CSV data"""
        self.csv_path = csv_path
        
        # Check if CSV file exists
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Try to load the CSV file
        try:
            self.data = pd.read_csv(csv_path)
            
            # Check for required columns
            required_columns = ["StockNumber", "Property Address", "City", "State"]
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            
            if missing_columns:
                raise ValueError(f"CSV file missing required columns: {', '.join(missing_columns)}")
                
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing CSV file: {e}")
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {e}")
        
        # Set up Ollama directly
        try:
            from langchain.llms import Ollama
            self.ollama_llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
            print(f"\nInitialized Ollama with model {OLLAMA_MODEL}")
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
            print("Continuing without Ollama model setup. This may cause issues later.")
        
        # Check if Ollama is running
        if not check_ollama_running():
            print("\nOllama is not running. Please make sure Ollama is installed and running.")
            print("You can install Ollama from https://ollama.com/")
            print("Then start it with 'ollama serve' command in a separate terminal.")
            sys.exit(1)
            
    def get_property_data(self, stock_number):
        """Get all data for a specific property by stock number"""
        property_data = self.data[self.data['StockNumber'] == stock_number]
        if property_data.empty:
            return None
        
        # Convert the data to a dictionary and handle missing values
        property_dict = property_data.iloc[0].to_dict()
        
        # Convert numeric fields that might be missing or 'N/A' to appropriate values
        for key, value in property_dict.items():
            if pd.isna(value):
                property_dict[key] = 'N/A'
            elif isinstance(value, (int, float)) and 'Price' in key:
                # Format prices with commas for readability
                try:
                    property_dict[key] = f"{value:,.2f}".rstrip('0').rstrip('.') if '.' in f"{value:,.2f}" else f"{value:,.0f}"
                except:
                    # Keep original value if formatting fails
                    pass
        
        return property_dict
        
    def get_property_list(self):
        """Returns a list of all stock numbers and their addresses"""
        return self.data[['StockNumber', 'Property Address', 'City', 'State']].to_dict('records')
    
    def analyze_property(self, stock_number):
        """
        Run a full property analysis using the CrewAI framework with specialized agents
        for data analysis, web research, market analysis, and report generation.
        """
        # Get property data
        property_data = self.get_property_data(stock_number)
        if not property_data:
            return f"Property with stock number {stock_number} not found."
        
        # Create property location string
        property_location = f"{property_data.get('Property Address', '')}, {property_data.get('City', '')}, {property_data.get('State', '')} {property_data.get('Zip', '')}"
        
        # Show analysis header
        use_colors = supports_color()
        if use_colors:
            print_header("PROPERTY ANALYSIS")
            print(f"\n{Colors.GRAY}Analyzing property at {property_location}...{Colors.ENDC}\n")
        else:
            print("\n===== PROPERTY ANALYSIS =====")
            print(f"\nAnalyzing property at {property_location}...\n")
        
        # Import directly here to ensure we get the right version
        from langchain.llms import Ollama
        
        # Create Ollama LLM instances directly for each agent - with full config
        llm = Ollama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=CREW_TEMPERATURE
        )
        
        try:
            # Create the specialized agents according to the project plan
            
            # 1. Data Analysis Agent
            data_analysis_agent = Agent(
            role="Property Data Analyst",
                goal="Analyze raw property metrics to identify key insights for development potential",
                backstory="You are a specialist in demographic, economic, and environmental property data analysis. You extract meaningful patterns from complex datasets to support real estate development decisions.",
                verbose=True,
                llm=llm,
                allow_delegation=False
            )
            
            # 2. Web Research Agent
            web_research_agent = Agent(
                role="Housing & Economic Research Specialist",
                goal="Gather relevant external information about the property's location and market",
                backstory="You are an expert at researching local economic trends, housing markets, and development regulations. You find key insights from the web to supplement property data analysis.",
                verbose=True,
                llm=llm,
                tools=[WebResearchTool()],
                allow_delegation=True
            )
            
            # 3. Market Analysis Agent
            market_analysis_agent = Agent(
                role="Attainable Housing Market Analyst",
                goal="Evaluate market suitability for the planned housing community",
                backstory="You specialize in analyzing housing market data to determine optimal development strategies. You have expertise in evaluating demand patterns, competition, and pricing strategies.",
            verbose=True,
                llm=llm,
                allow_delegation=False
            )
            
            # 4. Report Generation Agent
            report_generation_agent = Agent(
                role="Attainable Housing Development Strategist",
                goal="Compile all findings into a comprehensive strategic analysis report",
                backstory="You have extensive experience in evaluating property development opportunities and creating strategic recommendations. You excel at integrating diverse insights into actionable guidance.",
            verbose=True,
                llm=llm,
                allow_delegation=False
        )
        
            # Create tasks for the agents
            
            # Task 1: Data Analysis
        data_analysis_task = Task(
            description=f"""Analyze the key metrics for the property at {property_location}.
            
                Property Details:
                - Stock Number: {property_data.get('StockNumber', 'N/A')}
            - Land Area: {property_data.get('Land Area (AC)', 'N/A')} acres
            - County: {property_data.get('County Name', 'N/A')}
            - Zoning: {property_data.get('Zoning', 'N/A')}
                - For Sale Price: ${property_data.get('For Sale Price', 'N/A')}
                - Flood Risk: {property_data.get('In SFHA', 'N/A')} (Special Flood Hazard Area)
                - FEMA Flood Zone: {property_data.get('Fema Flood Zone', 'N/A')}
                
                Demographic Analysis:
                - Population (5mi): {property_data.get('2024 Population(5m)', 'N/A')}
                - Population Growth (2020-2024, 5mi): {property_data.get('% Pop Grwth 2020-2024(5m)', 'N/A')}%
                - Projected Growth (2024-2029, 5mi): {property_data.get('% Pop Grwth 2024-2029(5m)', 'N/A')}%
                - Age Distribution (various age brackets available in data)
                
                Income Analysis:
                - 2024 Median Household Income (5mi): ${property_data.get('2024 Med HH Inc(5m)', 'N/A')}
                - 2024 Average Household Income (5mi): ${property_data.get('2024 Avg HH Inc(5m)', 'N/A')}
                - Income trends and projections (2024-2029)
            
            Housing Market Metrics:
            - 2024 Median Home Value (5mi): ${property_data.get('2024 Median Home Value(5m)', 'N/A')}
                - Housing Value Distribution (across price ranges)
                - Rental Market Data (median/average rents)
                - Housing Occupancy Data (owner vs. renter)
                
                Proximity Services:
                - Nearest Walmart: {property_data.get('Nearest_Walmart_Distance_Miles', 'N/A')} miles
                - Nearest Hospital: {property_data.get('Nearest_Hospital_Distance_Miles', 'N/A')} miles
                - Nearest Park: {property_data.get('Nearest_Park_Distance_Miles', 'N/A')} miles
                
                Market Analysis Scores:
                - Home Affordability: {property_data.get('Home_Affordability', 'N/A')} (Percentile: {property_data.get('Home_Affordability Percentile', 'N/A')})
                - Rent Affordability: {property_data.get('Rent_Affordability', 'N/A')} (Percentile: {property_data.get('Rent_Affordability Percentile', 'N/A')})
                - Convenience Index: {property_data.get('Convenience_Index', 'N/A')} (Percentile: {property_data.get('Convenience_Index Percentile', 'N/A')})
                - Population Access: {property_data.get('Population_Access', 'N/A')} (Percentile: {property_data.get('Population_Access Percentile', 'N/A')})
                - Market Saturation: {property_data.get('Market_Saturation', 'N/A')} (Percentile: {property_data.get('Market_Saturation Percentile', 'N/A')})
                - Composite Score: {property_data.get('Composite_Score', 'N/A')} (Percentile: {property_data.get('Composite_Score Percentile', 'N/A')})
                
                Using all the data available, perform a comprehensive analysis of this property's development potential for an attainable housing community with:
                - 80% high-quality manufactured homes
                - 15% apartment/condo homes
                - 5% traditional/"stick" built homes
                
                Identify key strengths, concerns, and notable patterns in the data. Calculate how this property compares to typical development targets.
                
                Provide a detailed analysis with a clear assessment of the property's demographic, economic, and housing market potential.
                """,
                agent=data_analysis_agent,
                expected_output="A comprehensive analysis of the property's raw data metrics with key insights for development potential."
            )
            
            # Task 2: Web Research
            web_research_task = Task(
                description=f"""Research key information about the area around {property_location} that would impact housing development.
                
                Search for recent (within the last 2 years) information about:
                
                1. Local Economic Development:
                   - Business expansions or relocations in {property_data.get('City', 'the area')} and {property_data.get('County Name', 'the county')}
                   - Major employers and job growth trends
                   - Economic development initiatives or challenges
                   - Infrastructure projects (roads, utilities, public transit)
                
                2. Housing Market Conditions:
                   - Evidence of housing shortage or crisis in the area
                   - Recent housing developments and their reception
                   - Affordable housing initiatives or programs
                   - Public funding or grants available for housing development
                   - Manufactured housing acceptance and regulations
                
                3. Government and Regulatory Environment:
                   - Local government attitude toward development
                   - Recent zoning changes or updates affecting residential development
                   - Permitting process efficiency and challenges
                   - Development incentives or tax benefits available
                
                4. Community Factors:
                   - School quality and educational opportunities
                   - Crime statistics and safety perception
                   - Community amenities and quality of life indicators
                   - Local sentiment toward growth and development
                
                5. Potential Partnership Opportunities:
                   - Local employers seeking workforce housing
                   - Educational institutions with housing needs
                   - Healthcare providers seeking proximity housing
                
                For each finding, provide:
                - Source URL or citation
                - Date of information
                - A brief summary of the key points
                - Relevance to the proposed housing development
                
                Focus on information that would directly impact the viability of developing a mixed attainable housing community with manufactured homes, apartments, and traditional homes.
                """,
                agent=web_research_agent,
                context=[data_analysis_task],
                expected_output="A detailed research report on local economic, housing, and regulatory conditions with properly cited sources."
            )
            
            # Task 3: Market Analysis
            market_analysis_task = Task(
                description=f"""Evaluate the market suitability of {property_location} for the planned housing community based on the data analysis and web research findings.
                
                Property Specifics:
            - Land Area: {property_data.get('Land Area (AC)', 'N/A')} acres
                - For Sale Price: ${property_data.get('For Sale Price', 'N/A')}
                - Current Zoning: {property_data.get('Zoning', 'N/A')}
                
                Using the data analysis and web research findings, assess:
                
                1. Demand Analysis:
                   - Evaluate demand for different housing types (manufactured homes, apartments, traditional homes)
                   - Assess if the planned 80/15/5 housing mix is optimal for this market
                   - Identify target demographic segments most likely to be residents
                
                2. Competition Assessment:
                   - Analyze current and planned housing developments in the area
                   - Evaluate market saturation and vacancy rates
                   - Identify competitive advantages for this property
                
                3. Pricing Strategy:
                   - Recommend optimal price points for each housing type
                   - Evaluate affordability relative to local incomes
                   - Analyze rental vs. ownership demand patterns
                
                4. Amenities Assessment:
                   - Determine which amenities would be most valuable for the target market
                   - Evaluate demand for subscription services (housekeeping, landscaping, daycare)
                   - Assess technology integration opportunities
                
                5. Development Phasing:
                   - Recommend optimal phasing strategy based on market demand
                   - Identify which housing types to prioritize in early phases
                   - Suggest timeline considerations based on market conditions
                
                Provide a detailed market analysis with clear recommendations for adapting the development plan to match local market conditions and maximize ROI.
                """,
                agent=market_analysis_agent,
                context=[data_analysis_task, web_research_task],
                expected_output="A comprehensive market analysis with specific recommendations for housing mix, pricing, amenities, and development strategy."
            )
            
            # Task 4: Report Generation
            report_generation_task = Task(
                description=f"""Create a comprehensive property analysis report for {property_location} by integrating all findings from the data analysis, web research, and market analysis.
                
                The report should include:
                
                1. Executive Summary (200-300 words):
                   - Overall property suitability score (1-10)
                   - Top 3 strengths of the property for development
                   - Top 3 concerns or challenges
                   - Clear acquisition recommendation (Highly Recommended, Recommended, Consider with Conditions, Not Recommended)
                
                2. Property Profile:
                   - Basic property details (location, size, price, zoning)
                   - Environmental assessment (flood risk analysis)
                   - Proximity services evaluation
                
                3. Demographic Analysis:
                   - Population trends and projections
                   - Age distribution analysis with implications for community amenities
                   - Income distribution analysis with affordability assessment
                
                4. Housing Market Analysis:
                   - Current and projected housing value distribution
                   - Rental market assessment
                   - Market scores interpretation
                
                5. Economic Outlook:
                   - Income trend projections
                   - Local economic development assessment
                   - Employment opportunities
                
                6. Development Opportunity Assessment:
                   - Optimal housing mix recommendation (adjusting the 80/15/5 model if needed)
                   - Target resident profiles
                   - Amenity and service recommendations
                   - Competitive advantage assessment
                
                7. Risk Assessment:
                   - Market risks
                   - Regulatory/zoning challenges
                   - Environmental considerations
                
                8. Financial Projection:
                   - Estimated development costs based on company's housing mix
                   - Revenue potential based on local market data
                   - ROI scenarios (conservative, moderate, optimistic)
                
                9. Strategic Recommendations:
                   - Clear guidance on property acquisition
                   - Development phasing strategy
                   - Risk mitigation approaches
                
                Format the report in a clear, professional manner with distinct sections. Use bullet points for key findings and recommendations. Emphasize actionable insights throughout.
                """,
                agent=report_generation_agent,
                context=[data_analysis_task, web_research_task, market_analysis_task],
                expected_output="A complete property analysis report with executive summary, detailed findings, and strategic recommendations."
            )
            
            # Create and run the crew
            crew = Crew(
                agents=[data_analysis_agent, web_research_agent, market_analysis_agent, report_generation_agent],
                tasks=[data_analysis_task, web_research_task, market_analysis_task, report_generation_task],
                        verbose=True,
                process=Process.sequential
            )
            
            print("\nStarting comprehensive property analysis (this may take several minutes)...")
            print(f"Using {OLLAMA_MODEL} model for all agents...")
            
            # Execute the analysis
            result = crew.kickoff()
            
            # Format and return the result
            print_header("PROPERTY ANALYSIS COMPLETE")
            print("\nResults:")
            print(result)
            
            return result
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
            # Provide a basic fallback result
            basic_result = f"""
PROPERTY ANALYSIS ERROR

We encountered an error while analyzing {property_location}:
{str(e)}

Basic Property Information:
- Land Area: {property_data.get('Land Area (AC)', 'N/A')} acres
- County: {property_data.get('County Name', 'N/A')}
- Median Home Value (5mi): ${property_data.get('2024 Median Home Value(5m)', 'N/A')}
- Median Income (5mi): ${property_data.get('2024 Med HH Inc(5m)', 'N/A')}
- Population Growth: {property_data.get('% Pop Grwth 2020-2024(5m)', 'N/A')}%

Please try again or check the system configuration.
"""
            print(basic_result)
            return basic_result

def test_web_search():
    """Test the web search functionality to ensure it's working properly."""
    try:
        print("Testing enhanced web search functionality...")
        web_tool = EnhancedWebResearchTool()
        
        if not web_tool.search_available:
            print("Web search is not available. DuckDuckGo search library is not installed.")
            print("Install it with: pip install -U duckduckgo-search")
            return False
            
        # Try a simple search
        test_query = "real estate market trends"
        results = web_tool.search(test_query, max_results=2)
        
        if not results or len(results) == 0:
            print("Web search test failed. No results returned.")
            return False
            
        # Print a sample result to confirm it's working
        print("Web search test successful. Sample result:")
        print(f"Title: {results[0].get('title', 'No title')}")
        print(f"Snippet: {results[0].get('body', 'No content')[:100]}...")
        return True
        
    except Exception as e:
        print(f"Web search test failed with error: {e}")
        return False

def main():
    """Main function to run the property analysis"""
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help', '?']:
        show_help()
        return
        
    print_header("PROPERTY ANALYSIS SYSTEM")
    print("This tool analyzes properties for high-density, master-planned community development")
    print("(Use --help for detailed information about the system)")
    
    # Ensure we're using local Llama model
    os.environ["CREWAI_LOCAL_MODEL"] = "true"
    os.environ["CREWAI_FORCE_LOCAL"] = "true"
    os.environ["ANTHROPIC_API_KEY"] = "" 
    os.environ["OPENAI_API_KEY"] = ""
    
    # Explicitly tell CrewAI to use Ollama
    import crewai
    if hasattr(crewai, 'set_default_llm'):
        try:
            from langchain.llms import Ollama
            llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=CREW_TEMPERATURE)
            crewai.set_default_llm(llm)
            print("Successfully set CrewAI's default LLM to Ollama")
        except Exception as e:
            print(f"Warning: Couldn't set CrewAI's default LLM: {e}")
    
    # Check for Ollama installation and setup model
    if not check_ollama_installed():
        print("\nOllama is not installed.")
        print("Please install Ollama from https://ollama.com/")
        print("Then run the startup.sh script again.")
        sys.exit(1)
    elif not check_ollama_running():
        print("\nOllama is installed but not running.")
        print("Please start Ollama before running this program.")
        print("On macOS/Linux: Run 'ollama serve' in a terminal")
        print("On Windows: Start Ollama from the start menu or run 'ollama serve' in a command prompt")
        sys.exit(1)
    else:
        print("\nUsing Llama 3 model via Ollama")
        try:
            # Make a direct request to Ollama API as a test
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": "Hello, are you working?", "stream": False}
            )
            if response.status_code == 200:
                print("Successfully connected to Ollama API")
            else:
                print(f"Warning: Ollama API responded with status code {response.status_code}")
        except Exception as e:
            print(f"Warning: Error testing Ollama API: {e}")
    
    try:
        # Initialize analyzer
        print("\nInitializing property analyzer...")
        try:
            analyzer = PropertyAnalyzer()
            print("Property data loaded successfully.")
        except FileNotFoundError as e:
            print(f"\nError: {e}")
            print("\nPlease ensure:")
            print("1. You have run the startup.sh script first")
            print("2. You have placed your property data CSV in the DATA directory as 'master.csv'")
            sys.exit(1)
        except ValueError as e:
            print(f"\nError with CSV file: {e}")
            print("\nPlease check your CSV file format. It should include columns for:")
            print("StockNumber, Property Address, City, State")
            sys.exit(1)
        
        # Setup Ollama model
        setup_ollama_model()
        
        # Test web search functionality
        print("\nVerifying web search capability...")
        search_available = test_web_search()
        if not search_available:
            print("\nWarning: Web search functionality is limited or unavailable.")
            print("The Web Research Agent may not be able to gather external information.")
            print("Analysis will proceed using only the data in your CSV file.")
            proceed = input("Do you want to continue without web search? [Y/n]: ").strip().lower()
            if proceed == 'n':
                print("Exiting. Please install duckduckgo-search package and try again.")
                sys.exit(0)
        
        # Check if we can read the CSV file
        try:
            properties = analyzer.get_property_list()
            if not properties:
                print("Warning: No properties found in the CSV file.")
                print("The file may be empty or have an unexpected format.")
                response = input("Do you want to continue anyway? [y/N]: ")
                if response.lower() != "y":
                    print("Exiting program.")
                    sys.exit(0)
        except Exception as e:
            print(f"Error retrieving property list: {e}")
            print("The CSV file may have an invalid format.")
            sys.exit(1)
        
        # Show available properties
        print("\nAvailable Properties:")
        for i, prop in enumerate(properties[:10]):  # Show first 10 for brevity
            try:
                print(f"{i+1}. Stock# {prop['StockNumber']} - {prop.get('Property Address', 'N/A')}, {prop.get('City', 'N/A')}, {prop.get('State', 'N/A')}")
            except KeyError:
                print(f"{i+1}. Stock# {prop.get('StockNumber', 'Unknown')} - (Missing address information)")
        
        if len(properties) > 10:
            print(f"...and {len(properties) - 10} more properties")
        
        # Get stock number from user
        stock_number = input("\nEnter the Stock Number to analyze: ").strip()
        
        if not stock_number:
            print("Error: No stock number entered. Please try again.")
            return
        
        # Get property details for display
        property_data = analyzer.get_property_data(stock_number)
        if not property_data:
            print(f"Error: Property with Stock Number '{stock_number}' was not found in the dataset.")
            print("Available stock numbers include:")
            for i, prop in enumerate(properties[:5]):  # Show first 5 for brevity
                print(f"  - {prop['StockNumber']}")
            if len(properties) > 5:
                print(f"  - ... and {len(properties) - 5} more")
            return
            
        # Display property summary before analysis
        property_location = f"{property_data.get('Property Address', '')}, {property_data.get('City', '')}, {property_data.get('State', '')} {property_data.get('Zip', '')}"
        
        print(f"\nProperty Selected:")
        print(f"Location: {property_location}")
        print(f"Land Area: {property_data.get('Land Area (AC)', 'N/A')} acres")
        print(f"County: {property_data.get('County Name', 'N/A')}")
        print(f"For Sale Price: ${property_data.get('For Sale Price', 'N/A')}")
        
        # Run the analysis
        print(f"\nAnalyzing property with Stock Number {stock_number}...\n")
        print("This comprehensive analysis may take 10-15 minutes with the Llama 3 model.")
        print("The system is working even if it appears to be inactive.")
        
        try:
            analyzer.analyze_property(stock_number)
        except Exception as e:
            print(f"\nError during analysis: {e}")
            print("Please try again with a different property.")
            
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Print error trace for detailed debugging if it's a serious error
        import traceback
        print("\nDetailed error information:")
        traceback.print_exc()
        
        print("\nTroubleshooting tips:")
        print("1. Make sure your CSV file exists at DATA/master.csv and has the correct format")
        print("2. Check that Ollama is running (run 'ollama serve' in a terminal)")
        print("3. Make sure the Llama 3 model is available (run 'ollama pull llama3')")

def show_help():
    """Display help information about the system and how to interpret results."""
    print_header("PROPERTY ANALYSIS SYSTEM HELP")
    
    print("\nOVERVIEW:")
    print("This system analyzes property data for high-density, master-planned community development.")
    print("It uses a team of specialized AI agents powered by Llama 3.3 70B to provide comprehensive")
    print("analysis and recommendations for properties in your dataset.")
    
    print("\nSYSTEM REQUIREMENTS:")
    print("- Python 3.9+ with required packages installed")
    print("- Ollama installed and running (https://ollama.com)")
    print("- Llama 3.3 70B model downloaded (approximately 45GB)")
    print("- 16GB+ RAM recommended (32GB preferred for optimal performance)")
    print("- Internet connection for web research component")
    
    print("\nDATA FORMAT:")
    print("The system expects a CSV file named 'master.csv' in the DATA directory with these columns:")
    print("- StockNumber: Unique identifier for each property")
    print("- Property Address, City, State, Zip: Location information")
    print("- Land Area (AC): Size in acres")
    print("- For Sale Price: Property's asking price")
    print("- And numerous demographic, economic, and market data columns")
    
    print("\nANALYSIS PROCESS:")
    print("1. Data Analysis Agent: Evaluates raw property metrics, demographics, and environmental factors")
    print("2. Web Research Agent: Researches local economic trends, regulations, and market conditions")
    print("3. Market Analysis Agent: Assesses market fit for the company's development model")
    print("4. Report Generation Agent: Creates comprehensive analysis and recommendations")
    
    print("\nINTERPRETING RESULTS:")
    print("The final report is organized into sections:")
    print("- Executive Summary: Overall rating (1-10) and key findings")
    print("- Property Profile: Basic details and environmental assessment")
    print("- Demographic Analysis: Population and income trends")
    print("- Housing Market Analysis: Current and projected housing values")
    print("- Development Opportunity Assessment: Housing mix and target residents")
    print("- Financial Projection: Development costs, revenue potential, and ROI")
    print("- Strategic Recommendations: Clear guidance on property acquisition")
    
    print("\nTROUBLESHOOTING:")
    print("- If analysis is slow: This is normal, as the AI processes complex data")
    print("- If analysis fails: Check Ollama is running and the model is downloaded")
    print("- If data errors occur: Ensure your CSV has all required columns")
    
    print("\nFor more help, refer to the project documentation or contact support.")
    print("")

if __name__ == "__main__":
    main()




