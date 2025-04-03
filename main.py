from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun
import pandas as pd
import os
from dotenv import load_dotenv
import subprocess
import sys
import time
import requests

# Load environment variables
load_dotenv()

# Configure LiteLLM for debugging
import litellm
litellm._turn_on_debug()

# Default to Llama 3 8B model via Ollama
LLAMA_MODEL = "meta-llama/Meta-Llama-3-8B"
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
CREW_TEMPERATURE = float(os.getenv("CREW_TEMPERATURE", 0.5))

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
    """Setup Llama 3 model in Ollama"""
    try:
        print("Checking if Llama 3 model is available in Ollama...")
        result = subprocess.run(["ollama", "list"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE, 
                              text=True)
        
        if "llama3" not in result.stdout:
            print("Downloading Llama 3 model (this may take a few minutes the first time)...")
            subprocess.run(["ollama", "pull", "llama3"], check=True)
            print("Llama 3 model downloaded successfully!")
        else:
            print("Llama 3 model is ready to use.")
        
        return True
    except subprocess.SubprocessError as e:
        print(f"Error setting up Ollama model: {e}")
        return False

def use_anthropic_if_available():
    """Check if Anthropic API key is available"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key != "your_anthropic_api_key_here":
        print("\nFound valid Anthropic API key, using Claude model instead of Llama 3.")
        return True
    return False

class PropertyAnalyzer:
    def __init__(self, csv_path="DATA/master.csv"):
        """Initialize the property analyzer with CSV data"""
        self.csv_path = csv_path
        self.data = pd.read_csv(csv_path)
        self.search_tool = DuckDuckGoSearchRun()
        self.column_descriptions = self._get_column_descriptions()
        
        # Choose model based on availability
        if check_ollama_installed() and check_ollama_running() and not use_anthropic_if_available():
            self.model = LLAMA_MODEL
            setup_ollama_model()
        else:
            self.model = ANTHROPIC_MODEL
        
    def _get_column_descriptions(self):
        """Return descriptions for important data columns"""
        return {
            # Basic Property Information
            "StockNumber": "Unique identifier for each property listing",
            "Property Address": "Street address of the property",
            "City": "City where the property is located",
            "State": "State where the property is located",
            "Zip": "ZIP/Postal code of the property location",
            "For Sale Price": "The listing price of the property in USD",
            "PropertyID": "Secondary identifier used in property management systems",
            "Land Area (AC)": "Property area in acres - critical for development density calculations",
            "Latitude": "Geographic coordinate (latitude) of the property",
            "Longitude": "Geographic coordinate (longitude) of the property",
            "Zoning": "Legal zoning classification that determines allowable development types",
            "County Name": "The county where the property is located",
            "Proposed Land Use": "Suggested or approved future use for the property",
            
            # Ownership and Sales Information
            "Owner Name": "Current owner of the property",
            "Sale Company Name": "Real estate company handling the property sale",
            "Sale Company Contact": "Contact person at the real estate company",
            "Sale Company Phone": "Phone number for the real estate company",
            "Sale Company Fax": "Fax number for the real estate company",
            "Last Sale Date": "Date when the property was last sold",
            "Last Sale Price": "Price at which the property was last sold in USD",
            
            # Flood Risk Information
            "In SFHA": "Whether property is in Special Flood Hazard Area (Yes/No) - indicates flood risk",
            "Fema Flood Zone": "FEMA-designated flood zone classification (e.g., A, AE, X) - details flood risk level",
            "FEMA Map Date": "Date of the FEMA flood map used for flood zone determination",
            "Floodplain Area": "Portion of the property within the designated floodplain (often in acres or %)",
            
            # Population Growth Metrics (Critical for Market Analysis)
            "% Pop Grwth 2020-2024(5m)": "Percentage population growth within 5 miles (2020-2024) - Key indicator of recent area growth",
            "% Pop Grwth 2024-2029(5m)": "Projected percentage population growth within 5 miles (2024-2029) - Forecasted future growth",
            "% Pop Grwth 2020-2024(10m)": "Percentage population growth within 10 miles (2020-2024) - Broader area growth trend",
            "% Pop Grwth 2024-2029(10m)": "Projected percentage population growth within 10 miles (2024-2029) - Broader future growth",
            
            # Population Data by Distance
            "2000 Population(3m)": "Total population within 3 miles in 2000 - Historical benchmark",
            "2020 Population(3m)": "Total population within 3 miles in 2020 - Recent census data",
            "2024 Population(3m)": "Total population within 3 miles in 2024 - Current estimate",
            "2029 Population(3m)": "Projected population within 3 miles in 2029 - Future forecast",
            "2000 Population(5m)": "Total population within 5 miles in 2000 - Historical benchmark",
            "2020 Population(5m)": "Total population within 5 miles in 2020 - Recent census data",
            "2024 Population(5m)": "Total population within 5 miles in 2024 - Current estimate",
            "2029 Population(5m)": "Projected population within 5 miles in 2029 - Future forecast",
            "2000 Population(10m)": "Total population within 10 miles in 2000 - Historical benchmark for wider region",
            "2020 Population(10m)": "Total population within 10 miles in 2020 - Recent census data for wider region",
            "2024 Population(10m)": "Total population within 10 miles in 2024 - Current estimate for wider region",
            "2029 Population(10m)": "Projected population within 10 miles in 2029 - Future forecast for wider region",
            
            # Income Data by Distance (Critical for Affordability Analysis)
            "2020 Med HH Inc(3m)": "Median household income within 3 miles in 2020 - Recent benchmark",
            "2024 Avg HH Inc(3m)": "Average household income within 3 miles in 2024 - Current mean income",
            "2024 Med HH Inc(3m)": "Median household income within 3 miles in 2024 - Current middle income point",
            "2029 Avg HH Inc(3m)": "Projected average household income within 3 miles in 2029 - Future forecast of mean income",
            "2029 Med HH Inc(3m)": "Projected median household income within 3 miles in 2029 - Future middle income point",
            "2020 Med HH Inc(5m)": "Median household income within 5 miles in 2020 - Recent benchmark",
            "2024 Avg HH Inc(5m)": "Average household income within 5 miles in 2024 - Current mean income",
            "2024 Med HH Inc(5m)": "Median household income within 5 miles in 2024 - Current middle income point, key for affordability analysis",
            "2029 Avg HH Inc(5m)": "Projected average household income within 5 miles in 2029 - Future income prediction",
            "2029 Med HH Inc(5m)": "Projected median household income within 5 miles in 2029 - Future middle income point",
            
            # Home Value Distribution Data (Price Brackets)
            "2024 Median Home Value(3m)": "Median home value within 3 miles in 2024 - Current market benchmark",
            "2029 Median HH Value(3m)": "Projected median home value within 3 miles in 2029 - Future market prediction",
            "2024 Median Home Value(5m)": "Median home value within 5 miles in 2024 - Current market benchmark, crucial for price positioning",
            "2029 Median HH Value(5m)": "Projected median home value within 5 miles in 2029 - Future market prediction",
            "2024 Median Home Value(10m)": "Median home value within 10 miles in 2024 - Wider market context",
            "2029 Median HH Value(10m)": "Projected median home value within 10 miles in 2029 - Future wider market",
            
            # Housing Unit Growth
            "% HU Grwth 2020-2024(3m)": "Percentage growth in housing units within 3 miles (2020-2024) - Recent construction activity",
            "% HU Grwth 2020-2024(5m)": "Percentage growth in housing units within 5 miles (2020-2024) - Area construction trends",
            "% HU Grwth 2020-2024(10m)": "Percentage growth in housing units within 10 miles (2020-2024) - Regional construction trends",
            
            # Detailed Demographic Data by Distance (5-mile radius)
            "TotPop_5": "Total population within 5 miles - Current population base",
            "TotHHs_5": "Total households within 5 miles - Number of household units, important for market sizing",
            "MedianHHInc_5": "Median household income within 5 miles - Middle income point, key for affordability",
            "AvgHHInc_5": "Average household income within 5 miles - Mean income level",
            "TotHUs_5": "Total housing units within 5 miles - Housing supply metric",
            "OccHUs_5": "Occupied housing units within 5 miles - Indicates demand level",
            "OwnerOcc_5": "Owner-occupied housing units within 5 miles - Ownership rate metric",
            "RenterOcc_5": "Renter-occupied housing units within 5 miles - Rental market size",
            "AvgOwnerHHSize_5": "Average owner household size within 5 miles - Typical family size of owners",
            "AvgRenterHHSize_5": "Average renter household size within 5 miles - Typical family size of renters",
            "VacHUs_5": "Vacant housing units within 5 miles - Key indicator of oversupply or seasonal area",
            "VacantForSale_5": "Vacant units for sale within 5 miles - Direct competition metric",
            "VacantForRent_5": "Vacant units for rent within 5 miles - Rental market vacancy",
            "OwnerVacRate_5": "Owner vacancy rate within 5 miles - Percentage of for-sale homes vacant",
            "RenterVacRate_5": "Renter vacancy rate within 5 miles - Percentage of rental units vacant, key market tightness indicator",
            "MedianHValue_5": "Median home value within 5 miles - Middle price point of homes",
            "MedianGrossRent_5": "Median gross rent within 5 miles - Middle price point for rentals",
            "AvgGrossRent_5": "Average gross rent within 5 miles - Mean rental cost, important for investment analysis",
            
            # Nearby Amenities and Services (Critical for Development Appeal)
            "Nearest_Walmart_Distance_Miles": "Distance to the nearest Walmart in miles - Retail convenience metric",
            "Nearest_Walmart_Travel_Time_Minutes": "Travel time to the nearest Walmart in minutes - Accessibility metric",
            "Nearest_Hospital_Distance_Miles": "Distance to the nearest hospital in miles - Healthcare access metric",
            "Nearest_Hospital_Travel_Time_Minutes": "Travel time to the nearest hospital in minutes - Emergency service access",
            "Nearest_Park_Distance_Miles": "Distance to the nearest park in miles - Recreation access metric",
            "Nearest_Park_Travel_Time_Minutes": "Travel time to the nearest park in minutes - Lifestyle amenity access",
            
            # Composite Scoring Metrics (Critical for Overall Evaluation)
            "Home_Affordability": "Score that measures property affordability relative to local incomes (higher is better) - Key for attainable housing viability",
            "Rent_Affordability": "Score that measures rent affordability in the area (higher is better) - Indicates rental burden levels",
            "Convenience_Index": "Score that measures proximity to amenities (higher is better) - Lifestyle and convenience factor",
            "Population_Access": "Score that measures access to population centers (higher is better) - Market size potential",
            "Market_Saturation": "Score that measures how saturated the market is (lower means less competition) - Competitive landscape metric",
            "Composite_Score": "Overall score combining all factors (higher is better) - Summary metric of development potential",
            
            # Percentile Rankings (Relative Position Metrics)
            "Home_Affordability Percentile": "Percentile ranking for home affordability (higher is better) - How this property compares to others",
            "Rent_Affordability Percentile": "Percentile ranking for rent affordability (higher is better) - Relative position for rental stress",
            "Convenience_Index Percentile": "Percentile ranking for convenience (higher is better) - Relative amenity access position",
            "Population_Access Percentile": "Percentile ranking for population access (higher is better) - Relative market access position",
            "Market_Saturation Percentile": "Percentile ranking for market saturation (higher is better) - Relative competition position",
            "Composite_Score Percentile": "Percentile ranking for overall composite score (higher is better) - Overall relative position",
            
            # Additional Important Metrics for Housing Development
            "InElementary_5": "Number of children enrolled in elementary school within 5 miles - Family demographic indicator",
            "InHighSchool_5": "Number of children enrolled in high school within 5 miles - Teen demographic indicator",
            "InCollege_5": "Number of people enrolled in college within 5 miles - Young adult demographic indicator",
            "VacantSeasonal_5": "Vacant units for seasonal use within 5 miles - Indicator of vacation/second home market",
            "MobileHomes_5": "Number of mobile homes within 5 miles - Alternative housing market indicator",
            "MobileHomesPerK_5": "Mobile homes per 1,000 housing units within 5 miles - Affordable housing prevalence",
            
            # Home Value Brackets (Price Distribution)
            "HvalUnder50_5": "Homes valued under $50,000 within 5 miles - Very low-cost housing count",
            "Hval50_5": "Homes valued $50,000-$99,999 within 5 miles - Low-cost housing count",
            "Hval100_5": "Homes valued $100,000-$149,999 within 5 miles - Moderate-low cost housing",
            "Hval150_5": "Homes valued $150,000-$199,999 within 5 miles - Moderate cost housing",
            "Hval200_5": "Homes valued $200,000-$299,999 within 5 miles - Moderate-high cost housing",
            "Hval300_5": "Homes valued $300,000-$499,999 within 5 miles - High cost housing",
            "Hval500_5": "Homes valued $500,000-$999,999 within 5 miles - Very high cost housing",
            "HvalOverMillion_5": "Homes valued over $1,000,000 within 5 miles - Luxury housing count",
        }
        
    def get_property_data(self, stock_number):
        """Get all data for a specific property by stock number"""
        property_data = self.data[self.data['StockNumber'] == stock_number]
        if property_data.empty:
            return None
        return property_data.iloc[0].to_dict()
        
    def get_property_list(self):
        """Returns a list of all stock numbers and their addresses"""
        return self.data[['StockNumber', 'Property Address', 'City', 'State']].to_dict('records')
        
    def create_agents(self):
        """Create specialized agents for property analysis"""
        
        # Data Analyst Agent analyzes the raw property data
        data_analyst = Agent(
            role="Property Data Analyst",
            goal="Analyze property data to identify locations ideal for attainable housing developments and economic growth potential",
            backstory="""You are an expert in real estate data analysis with years of experience 
            interpreting property metrics and housing affordability indicators. You specialize in 
            identifying areas experiencing both economic growth and housing affordability challenges. 
            Your analysis helps development companies identify locations where attainable housing 
            would meet critical market needs and support sustainable community growth. You have a 
            deep understanding of the housing crisis affecting many communities and can recognize 
            the data patterns that indicate where new attainable housing developments would be 
            most impactful and welcomed by the community.""",
            verbose=True,
            allow_delegation=True,
            tools=[self.search_tool],
            llm_model=self.model,
            temperature=CREW_TEMPERATURE
        )
        
        # Market Researcher Agent focuses on external market conditions
        market_researcher = Agent(
            role="Housing & Economic Research Specialist",
            goal="Research local housing crisis indicators, economic growth, and community sentiment toward new attainable housing developments",
            backstory="""You are a specialized researcher who excels at analyzing housing markets, 
            economic development patterns, and community housing needs. You have extensive experience 
            identifying areas experiencing housing affordability challenges alongside economic growth. 
            You can recognize the signals that indicate where a large-scale attainable housing development 
            would be welcomed and needed by the community. You know how to evaluate local government 
            attitudes toward housing development and identify locations where new development is being 
            actively encouraged to address housing shortages.""",
            verbose=True,
            allow_delegation=True,
            tools=[self.search_tool],
            llm_model=self.model,
            temperature=CREW_TEMPERATURE
        )
        
        # Financial Analyst Agent handles financial analysis and projections
        financial_analyst = Agent(
            role="Attainable Housing Financial Analyst",
            goal="Analyze financial feasibility of large-scale attainable housing developments and create compelling ROI projections",
            backstory="""You are a financial expert specializing in affordable and attainable housing 
            development economics. You understand the unique financial challenges and opportunities 
            in creating housing that is both profitable for developers and attainable for residents. 
            You have extensive experience with large-scale master-planned communities and can model 
            complex financial projections for developments with 500+ homes. You know how to identify 
            areas where the economics support attainable housing development and can calculate the 
            optimal price points that balance affordability with developer profitability.""",
            verbose=True,
            allow_delegation=True,
            tools=[self.search_tool],
            llm_model=self.model,
            temperature=CREW_TEMPERATURE
        )
        
        # Development Strategist Agent focuses on development recommendations
        development_strategist = Agent(
            role="Attainable Housing Development Strategist",
            goal="Create strategic plans for attainable housing communities that address housing crises while ensuring developer success",
            backstory="""You are a seasoned development strategist who specializes in attainable housing 
            and master-planned communities. You have designed numerous successful developments that 
            have addressed housing affordability challenges while creating vibrant, sustainable communities. 
            You understand how to navigate local regulations, build community support, and design 
            developments that meet both market needs and financial goals. You're skilled at identifying 
            locations where economic growth and housing shortages intersect, creating optimal conditions 
            for attainable housing development. You can recommend the right mix of housing types, 
            amenities, and pricing strategies to ensure community success.""",
            verbose=True,
            allow_delegation=True,
            tools=[self.search_tool],
            llm_model=self.model,
            temperature=CREW_TEMPERATURE
        )
        
        return {
            "data_analyst": data_analyst,
            "market_researcher": market_researcher,
            "financial_analyst": financial_analyst,
            "development_strategist": development_strategist
        }
    
    def create_tasks(self, agents, property_data, property_location):
        """Create tasks for the property analysis crew"""
        
        # Task for initial data analysis
        data_analysis_task = Task(
            description=f"""Analyze the key metrics for the property at {property_location} with special focus on 
            housing affordability, economic growth, and potential for a large-scale attainable housing development.
            
            The property has the following key data:
            - Price: ${property_data.get('For Sale Price', 'N/A')}
            - Land Area: {property_data.get('Land Area (AC)', 'N/A')} acres
            - Zoning: {property_data.get('Zoning', 'N/A')}
            - County: {property_data.get('County Name', 'N/A')}
            - Proposed Use: {property_data.get('Proposed Land Use', 'N/A')}
            
            CRITICAL ANALYSIS POINTS FOR ATTAINABLE HOUSING DEVELOPMENT:
            
            1. Housing Affordability Analysis:
               - Home Affordability Score: {property_data.get('Home_Affordability', 'N/A')}
               - Rent Affordability Score: {property_data.get('Rent_Affordability', 'N/A')}
               - 2024 Median Home Value (5mi): ${property_data.get('2024 Median Home Value(5m)', 'N/A')}
               - 2024 Median HH Income (5mi): ${property_data.get('2024 Med HH Inc(5m)', 'N/A')}
               - Calculate the income-to-home price ratio to identify affordability gaps
               - Analyze if the location shows signs of a housing crisis (supply/demand imbalance)
            
            2. Economic Growth Indicators:
               - Population Growth (5mi): {property_data.get('% Pop Grwth 2020-2024(5m)', 'N/A')}% (2020-2024)
               - Projected Growth (5mi): {property_data.get('% Pop Grwth 2024-2029(5m)', 'N/A')}% (2024-2029)
               - 2024 Population (5mi): {property_data.get('2024 Population(5m)', 'N/A')}
               - Job growth trends and employment opportunities
               - Analyze if the area is experiencing economic expansion or new business activity
            
            3. Master-Planned Community Feasibility:
               - Assess if the {property_data.get('Land Area (AC)', 'N/A')} acres is sufficient for 500+ homes
               - Convenience Index: {property_data.get('Convenience_Index', 'N/A')}
               - Population Access: {property_data.get('Population_Access', 'N/A')}
               - Evaluate infrastructure readiness for large-scale development
               - Analyze if local amenities support a master-planned community
            
            4. Community Need Assessment:
               - Assess the housing supply gap in the area
               - Evaluate if there are signs of local support for new housing developments
               - Analyze whether attainable housing aligns with local community needs
               - Look for evidence of housing shortages or affordability crises
            
            Identify at least 8 key insights from this data and explain their significance for an attainable 
            housing development of 500+ homes. Focus particularly on metrics that indicate both economic 
            growth AND housing affordability challenges.
            
            Column Descriptions:
            {self.column_descriptions}
            """,
            agent=agents["data_analyst"],
            expected_output="A detailed analysis of the property's potential for attainable housing development with at least 8 key insights"
        )
        
        # Task for market research
        market_research_task = Task(
            description=f"""Research the local housing market conditions, economic growth patterns, 
            development activities, and COMMUNITY SENTIMENT toward attainable housing for 
            {property_location} ({property_data.get('County Name', 'N/A')} County).
            
            CRITICAL RESEARCH AREAS:
            
            1. Housing Crisis Assessment:
               - Evidence of housing shortages in the area
               - News articles about housing affordability challenges
               - Local reporting on homelessness or housing insecurity
               - Rental vacancy rates and housing supply metrics
               - Government declarations regarding housing emergencies
            
            2. Economic Development:
               - Recent or planned major developments in the area
               - Economic growth initiatives or business expansion
               - Job creation announcements and employment trends
               - Infrastructure improvements (roads, utilities, public transport)
               - Major employers moving to or from the area
            
            3. Community & Government Sentiment:
               - Local government statements on housing needs
               - Community support or opposition to new housing developments
               - Recent zoning changes or housing policies
               - Incentives for affordable/attainable housing development
               - Public commentary on housing needs from local officials
            
            4. Rental Market Data:
               - Average gross rent in a 10-mile radius (critical for our ROI calculations)
               - Rental price trends over the past 5 years
               - Rental demand indicators
               - Affordability metrics (% of income spent on housing)
            
            5. Competitive Analysis:
               - Other housing developments planned or in progress
               - Success or failure of similar developments in the region
               - Market niches that are underserved
            
            RESEARCH OBJECTIVE: Determine if this location shows both:
            1. Strong economic growth indicators (suggesting long-term development viability)
            2. Housing affordability challenges (indicating community need for attainable housing)
            3. Positive government/community sentiment toward new housing development
            
            Particularly focus on finding evidence that local governments and communities are actively 
            seeking developers to build attainable housing to address local housing shortages.
            
            Use the internet to find current information. Focus on reliable sources like local government sites,
            economic development agencies, news outlets, real estate market reports, and rental listing aggregators.
            Provide specific citations and quotes from relevant officials or reports when possible.
            """,
            agent=agents["market_researcher"],
            expected_output="A comprehensive report on housing market conditions, economic growth, and community sentiment toward attainable housing development, with specific citations",
            context=[data_analysis_task]
        )
        
        # Task for financial analysis
        financial_analysis_task = Task(
            description=f"""Analyze the financial feasibility of developing a 500+ home attainable housing 
            master-planned community at {property_location}.
            
            The property is priced at ${property_data.get('For Sale Price', 'N/A')} with {property_data.get('Land Area (AC)', 'N/A')} acres.
            
            FINANCIAL ANALYSIS FRAMEWORK:
            
            1. Attainable Housing Development Model:
               - Target 500+ homes at attainable price points (below market rate)
               - Analyze if the lot size ({property_data.get('Land Area (AC)', 'N/A')} acres) is sufficient for this scale
               - Calculate optimal density to achieve affordability while maintaining quality
               - Determine price points that would be considered "attainable" in this market
                 (typically 80-120% of area median income affordability)
            
            2. Development Economics:
               - Per-home construction cost estimates for attainable housing
               - Infrastructure and common area development costs
               - Local impact fees and development charges
               - Phasing strategy to optimize cash flow during multi-year development
            
            3. Market-Specific Financial Metrics:
               - Home Affordability Score: {property_data.get('Home_Affordability', 'N/A')}
               - Rent Affordability Score: {property_data.get('Rent_Affordability', 'N/A')}
               - 2024 Median Home Value (5mi): ${property_data.get('2024 Median Home Value(5m)', 'N/A')}
               - 2029 Median Home Value (5mi): ${property_data.get('2029 Median HH Value(5m)', 'N/A')}
               - 2024 Median HH Income (5mi): ${property_data.get('2024 Med HH Inc(5m)', 'N/A')}
               - Calculate the "affordability gap" in this market and how attainable housing addresses it
            
            4. Lot Development Economics (for reference):
               - Lot Density: 3.5 lots per acre of land
               - Total Potential Lots: {3.5 * float(property_data.get('Land Area (AC)', 0))} lots
               - Initial Development Cost: $55,000 per lot
               - Total Development Cost: ${55000 * 3.5 * float(property_data.get('Land Area (AC)', 0))}
               - Total Lot Investment: ${float(property_data.get('For Sale Price', 0)) + (55000 * 3.5 * float(property_data.get('Land Area (AC)', 0)))}
            
            5. Attainable Housing ROI Analysis:
               - Calculate realistic sale prices for attainable housing in this market
               - Project development timeline and cash flow (5-year development horizon)
               - Analyze profit margins at different price points
               - Identify potential subsidies, tax incentives, or grants available for attainable housing
               - Calculate internal rate of return (IRR) and return on investment (ROI)
            
            6. Sensitivity Analysis:
               - Risk assessment if construction costs increase by 10-20%
               - Impact of economic downturn on sales velocity
               - Effects of potential interest rate changes
               - Comparison of different attainable housing models (rent vs. own)
            
            7. Community Economic Impact:
               - Projected economic impact of 500+ homes on the local economy
               - Potential job creation during and after development
               - Tax base expansion benefits for local government
            
            Based on this analysis, determine:
            1. If the financial numbers support attainable housing development
            2. The optimal price points and development approach
            3. The expected ROI and timeline for the development
            4. Key financial risks and mitigations
            5. Whether this location represents a strong financial opportunity for attainable housing
            """,
            agent=agents["financial_analyst"],
            expected_output="A comprehensive financial analysis for a 500+ home attainable housing development with ROI projections and optimal price points",
            context=[data_analysis_task, market_research_task]
        )
        
        # Task for development recommendations
        development_recommendations_task = Task(
            description=f"""Create a comprehensive attainable housing development strategy for a 500+ home 
            master-planned community at {property_location}.
            
            Property details:
            - Land Area: {property_data.get('Land Area (AC)', 'N/A')} acres
            - Zoning: {property_data.get('Zoning', 'N/A')}
            - Proposed Land Use: {property_data.get('Proposed Land Use', 'N/A')}
            - Composite Score: {property_data.get('Composite_Score', 'N/A')}
            
            ATTAINABLE HOUSING DEVELOPMENT STRATEGY:
            
            1. Community Vision & Positioning:
               - Define the vision for an attainable housing community in this location
               - Positioning relative to market needs and housing affordability challenges
               - Community identity and branding approach
               - How this development addresses the local housing crisis
            
            2. Development Program:
               - Optimal mix of housing types and price points
               - Density recommendations to achieve affordability while maintaining quality
               - Amenities and community features that support attainable housing
               - Phasing strategy for a 500+ home community
               - Infrastructure and public space planning
            
            3. Regulatory Strategy:
               - Zoning and entitlement approach
               - Potential incentives and programs to support attainable housing
               - Community engagement and approval strategy
               - Environmental and sustainability considerations
            
            4. Marketing & Sales Strategy:
               - Target resident profiles
               - Messaging that emphasizes attainability and community benefits
               - Outreach channels and partnership opportunities
               - Pricing strategy that balances affordability with development economics
            
            5. Implementation Roadmap:
               - Key project milestones
               - Development timeline (with phases if appropriate)
               - Critical path considerations
               - Partnership and stakeholder engagement plan
            
            6. Risk Mitigation:
               - Key development risks and mitigation strategies
               - Market fluctuation contingency plans
               - Regulatory challenge strategies
            
            7. Community Impact:
               - How this development will address local housing affordability challenges
               - Economic benefits to the community
               - How to position the development as a solution to the housing crisis
            
            Based on all previous analyses (data, market, and financial), provide a comprehensive 
            strategy for developing a successful attainable housing community that addresses 
            local housing needs while ensuring a financially viable project.
            
            Focus particularly on how this development can help address the housing crisis in 
            this area and why the local community and government would welcome this development.
            """,
            agent=agents["development_strategist"],
            expected_output="A comprehensive attainable housing development strategy for a 500+ home community with specific recommendations",
            context=[data_analysis_task, market_research_task, financial_analysis_task]
        )
        
        # Task for final executive summary
        executive_summary_task = Task(
            description=f"""Create a concise executive summary for the attainable housing development opportunity 
            at {property_location}, focused on how this project can address local housing affordability challenges 
            while taking advantage of economic growth trends.
            
            Synthesize all findings and recommendations into a clear, actionable report that includes:
            
            1. Property & Market Overview:
               - Location: {property_location}
               - Price: ${property_data.get('For Sale Price', 'N/A')}
               - Size: {property_data.get('Land Area (AC)', 'N/A')} acres
               - Zoning: {property_data.get('Zoning', 'N/A')}
               - Key market indicators of housing need and economic growth
            
            2. Attainable Housing Opportunity Assessment:
               - Housing affordability gap analysis
               - Evidence of housing crisis or shortage
               - Community/government sentiment toward new housing
               - Economic growth indicators supporting development
            
            3. Development Concept:
               - Vision for a 500+ home attainable housing community
               - Housing mix and price point strategy
               - Key amenities and community features
               - Phasing approach
            
            4. Financial Summary:
               - Total development costs
               - Projected returns and profitability
               - Affordability metrics and target price points
               - Potential incentives or subsidies
            
            5. Competitive Advantage:
               - Why this location is ideal for attainable housing
               - How this development addresses specific local needs
               - Unique positioning opportunities
            
            6. Risks and Mitigations:
               - Key development risks
               - Market risks
               - Regulatory risks
               - Mitigation strategies
            
            7. SWOT Analysis:
               - Strengths (location, market, timing, etc.)
               - Weaknesses (challenges to overcome)
               - Opportunities (housing crisis solutions, economic growth, etc.)
               - Threats (competition, market shifts, etc.)
            
            8. Final Go/No-Go Recommendation:
               - Clear recommendation on whether to proceed
               - Key factors supporting this decision
               - Critical success factors if proceeding
               - Next steps and immediate priorities
            
            This summary must address the central question: "Is this location experiencing BOTH 
            economic growth AND housing affordability challenges that would make it ideal for 
            a large-scale attainable housing development?"
            
            Focus on creating a compelling case for why this development would be welcomed by 
            the community and local government as a solution to housing challenges.
            """,
            agent=agents["development_strategist"],
            expected_output="A complete executive summary with go/no-go recommendation for an attainable housing development",
            context=[data_analysis_task, market_research_task, financial_analysis_task, development_recommendations_task]
        )
        
        return [
            data_analysis_task,
            market_research_task,
            financial_analysis_task,
            development_recommendations_task,
            executive_summary_task
        ]
    
    def analyze_property(self, stock_number):
        """Run a complete analysis on the property with the given stock number"""
        # Get property data
        property_data = self.get_property_data(stock_number)
        if not property_data:
            return f"Property with stock number {stock_number} not found."
        
        # Create property location string
        property_location = f"{property_data.get('Property Address', '')}, {property_data.get('City', '')}, {property_data.get('State', '')} {property_data.get('Zip', '')}"
        
        # Create agents and tasks
        agents = self.create_agents()
        tasks = self.create_tasks(agents, property_data, property_location)
        
        # Create and run the crew
        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            verbose=2
        )
        
        result = crew.kickoff()
        return result

def main():
    """Main function to run the property analysis"""
    print("\n===== PROPERTY ANALYSIS CREW =====")
    print("This tool analyzes properties for attainable housing development potential")
    
    # Check for Ollama installation and setup model
    if not check_ollama_installed():
        print("\nOllama is not installed. Looking for Anthropic API key...")
        if use_anthropic_if_available():
            print("Using Claude model for analysis.")
        else:
            print("\nNo Ollama installation or Anthropic API key found.")
            print("Please either:")
            print("1. Install Ollama from https://ollama.com/")
            print("2. Or add your Anthropic API key to .env file")
            sys.exit(1)
    elif not check_ollama_running():
        print("\nOllama is installed but not running.")
        if use_anthropic_if_available():
            print("Using Claude model for analysis instead.")
        else:
            print("Please start Ollama before running this program.")
            print("On macOS/Linux: Run 'ollama serve' in a terminal")
            print("On Windows: Start Ollama from the start menu or run 'ollama serve' in a command prompt")
            sys.exit(1)
    else:
        if use_anthropic_if_available():
            print("Anthropic API key found. Using Claude model for analysis.")
        else:
            print("\nUsing Llama 3 8B model via Ollama")
            setup_ollama_model()
    
    try:
        # Initialize analyzer
        analyzer = PropertyAnalyzer()
        
        # Check if we can read the CSV file
        properties = analyzer.get_property_list()
        
        # Show available properties
        print("\nAvailable Properties:")
        for i, prop in enumerate(properties[:10]):  # Show first 10 for brevity
            print(f"{i+1}. Stock# {prop['StockNumber']} - {prop['Property Address']}, {prop['City']}, {prop['State']}")
        
        if len(properties) > 10:
            print(f"...and {len(properties) - 10} more properties")
        
        # Get stock number from user
        stock_number = input("\nEnter the Stock Number to analyze: ")
        
        try:
            stock_number = int(stock_number)
        except ValueError:
            print("Invalid input. Please enter a numeric Stock Number.")
            return
        
        # Run the analysis
        print(f"\nAnalyzing property with Stock Number {stock_number}...\n")
        if analyzer.model == LLAMA_MODEL:
            print("This analysis may take several minutes with the Llama 3 model.")
            print("The system is working even if it appears to be inactive.")
        else:
            print("Using Claude model for analysis. This may take a few minutes.")
        
        result = analyzer.analyze_property(stock_number)
        
        print("\n==== PROPERTY ANALYSIS RESULT ====\n")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your CSV file exists at DATA/master.csv")
        if not use_anthropic_if_available():
            print("2. Check that Ollama is running (run 'ollama serve' in a terminal)")
            print("3. Make sure the Llama 3 model is available (run 'ollama pull llama3')")
        else:
            print("2. Verify your Anthropic API key is valid in the .env file")
        print("3. Check your internet connection for web search functionality")

if __name__ == "__main__":
    main()




