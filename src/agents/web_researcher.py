#!/usr/bin/env python3
"""
Web Research Agent for Land Analysis Crew.
Gathers property data, demographic information, and market trends from online sources.
"""

from crewai import Agent, Task
from textwrap import dedent

class WebResearchAgent:
    """
    Agent that researches property information and market data from online sources.
    """
    
    def __init__(self, llm=None):
        """
        Initialize the web research agent.
        
        Args:
            llm: Language model to use for the agent (optional)
        """
        from crewai import Agent
        
        # Set up agent
        self.agent = Agent(
            role="Web Researcher",
            goal="Research property details, market data, and development potential",
            backstory="""You are an expert in property research with 8 years of experience 
            investigating real estate opportunities. Your specialty is gathering comprehensive 
            information about properties and their surroundings to evaluate development 
            potential. You have access to various data sources and can analyze zoning 
            regulations, market trends, demographic information, and environmental factors.
            
            You're known for your thorough, data-driven approach and ability to uncover 
            critical insights that others might miss. Your research forms the foundation 
            for development decisions and investment strategies.""",
            verbose=True,
            llm=llm
        )
        
    def get(self, key, default=None):
        """
        Implementation of the get method to support dict-like access for CrewAI compatibility.
        
        Args:
            key: The key to look up
            default: Default value if key not found
            
        Returns:
            The value for the key or the default
        """
        if key == "config":
            return {}
        if key == "agent":
            return self.agent
        if hasattr(self, key):
            return getattr(self, key)
        return default

    def __getitem__(self, key):
        """
        Support dictionary-like access for CrewAI compatibility.
        
        Args:
            key: The key to look up
            
        Returns:
            The value for the key
        """
        return self.get(key)

    def create_property_details_task(self, property_data):
        """
        Create a task to research additional details about a property.
        
        Args:
            property_data: Basic property information including address
            
        Returns:
            Task: Task to execute in a crew
        """
        return Task(
            description=dedent(f"""
                Research additional details about the property located at 
                {property_data.get('Property Address', 'N/A')}, {property_data.get('City', 'N/A')}, 
                {property_data.get('State', 'N/A')}.
                
                Focus your research on finding:
                
                1. Property History
                   - Previous sales and price history
                   - Any previous development proposals
                   - Historical uses of the land
                
                2. Zoning and Land Use
                   - Current zoning designation
                   - Allowed uses and density
                   - Any recent or proposed zoning changes
                   - Setback requirements, height restrictions, etc.
                
                3. Utilities and Infrastructure
                   - Available utilities (water, sewer, electric, gas)
                   - Capacity issues or connection challenges
                   - Road access and quality
                   - Broadband/telecommunications availability
                
                4. Environmental Factors
                   - Flood zone status
                   - Soil conditions (if available)
                   - Any known environmental issues
                   - Topography and drainage
                
                5. Nearby Amenities
                   - Schools and their ratings
                   - Shopping and services
                   - Parks and recreation
                   - Healthcare facilities
                
                6. Transportation
                   - Proximity to major roads and highways
                   - Public transportation options
                   - Traffic patterns and congestion issues
                   - Walk/bike scores
                
                Be specific and provide sources for your information where possible.
                Focus on information that would impact the property's development potential
                for high-density residential use.
            """),
            expected_output=dedent("""
                A detailed property research report covering all the requested aspects, with
                specific information about this property and its surroundings. The report should
                be well-organized, fact-based, and include citations or sources where possible.
                It should focus on information relevant to development potential.
            """),
            agent=self.agent
        )
        
    def create_demographic_data_task(self, property_data):
        """
        Create a task to research demographic information for the area around a property.
        
        Args:
            property_data: Basic property information including location
            
        Returns:
            Task: Task to execute in a crew
        """
        return Task(
            description=dedent(f"""
                Research and compile demographic data for the area surrounding the property at
                {property_data.get('Property Address', 'N/A')}, {property_data.get('City', 'N/A')}, 
                {property_data.get('State', 'N/A')}.
                
                Your research should include:
                
                1. Population Characteristics
                   - Current population and density
                   - Population growth trends (5-10 year history)
                   - Population projections (5-10 year forecast)
                   - Age distribution
                   - Household sizes and composition
                
                2. Income and Employment
                   - Median household income
                   - Income distribution
                   - Major employers in the area
                   - Employment sectors and growth
                   - Unemployment rates compared to regional/national averages
                
                3. Housing Trends
                   - Homeownership vs. rental rates
                   - Housing costs (both ownership and rental)
                   - Housing affordability metrics
                   - Housing types (single-family, multi-family, etc.)
                   - Age of housing stock
                
                4. Education
                   - Educational attainment levels
                   - School district quality
                   - Proximity to higher education
                
                5. Migration Patterns
                   - In-migration vs. out-migration
                   - Where new residents are coming from
                   - Why people are moving to or from the area
                
                Look at data for multiple geographic levels where appropriate:
                - Immediate neighborhood (1-mile radius if possible)
                - City/town level
                - County level
                - Metropolitan area (if applicable)
                
                Focus on data points that would be most relevant for determining the market
                for high-density residential development.
            """),
            expected_output=dedent("""
                A comprehensive demographic analysis with specific data points for the area
                surrounding the property. The report should be well-structured, include actual
                numbers and statistics, and clearly indicate the geographic area each data point
                refers to. Where possible, include trends over time and comparative context
                (how the area compares to regional or national averages).
            """),
            agent=self.agent
        )
        
    def create_local_development_task(self, property_data):
        """
        Create a task to research local development activity and regulations.
        
        Args:
            property_data: Basic property information including location
            
        Returns:
            Task: Task to execute in a crew
        """
        return Task(
            description=dedent(f"""
                Research local development activity and regulations affecting the property at
                {property_data.get('Property Address', 'N/A')}, {property_data.get('City', 'N/A')}, 
                {property_data.get('State', 'N/A')}.
                
                Your research should cover:
                
                1. Development Regulations
                   - Comprehensive plan designation
                   - Zoning code details relevant to multi-family/mixed-use
                   - Development review process
                   - Impact fees and other development costs
                   - Affordable housing requirements or incentives
                
                2. Recent Development Activity
                   - Major developments completed in the last 3 years
                   - Projects currently under construction
                   - Planned/proposed developments
                   - Focus on multi-family and mixed-use projects
                
                3. Government Attitude Toward Growth
                   - Is the local government pro-growth or restrictive?
                   - Recent policy changes affecting development
                   - Political climate regarding new housing
                
                4. Infrastructure Plans
                   - Planned road improvements
                   - Transit expansions or improvements
                   - Utility upgrades
                   - Public facility investments (parks, schools, etc.)
                
                5. Incentive Programs
                   - Tax increment financing districts
                   - Opportunity zones
                   - Density bonuses
                   - Other development incentives
                
                Be specific about the local jurisdiction's approach to development and
                any unique challenges or opportunities in this particular area. Include
                information about typical timelines for approvals and any known development
                controversies in the area.
            """),
            expected_output=dedent("""
                A detailed report on the local development environment, with specific information
                about regulations, recent activity, and government stance toward development in
                this particular location. The report should be factual and objective, but should
                highlight any red flags or special opportunities that would affect development
                potential. Where possible, include specific examples of recent developments and
                their experiences with the approval process.
            """),
            agent=self.agent
        )

    def research_property_details(self, property_data):
        """
        Research additional details about a property beyond the basic data.
        
        Args:
            property_data: Basic property information including address
            
        Returns:
            str: Detailed property information report
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_property_details_task method with a crew."
        
    def research_demographic_data(self, property_data):
        """
        Research demographic information for the area around a property.
        
        Args:
            property_data: Basic property information including location
            
        Returns:
            str: Demographic analysis report
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_demographic_data_task method with a crew."
        
    def research_local_development(self, property_data):
        """
        Research local development activity and regulations.
        
        Args:
            property_data: Basic property information including location
            
        Returns:
            str: Local development research report
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_local_development_task method with a crew."

    def create_property_research_task(self, property_data):
        """
        Create a task for researching property details.
        
        Args:
            property_data: Dictionary of property data
            
        Returns:
            Task: Task to execute in a crew
        """
        # Extract address components for better prompting
        address = property_data.get('Property Address', 'Unknown')
        city = property_data.get('City', 'Unknown')
        state = property_data.get('State', 'Unknown')
        
        # Create a task configuration object for the latest crewai version
        task_description = f"""
        Conduct comprehensive research on the property located at {address}, {city}, {state}.
        
        Your research should include:
        
        1. **Property Details & Zoning**
           - Current zoning and applicable regulations
           - Historical information and prior use
           - Environmental considerations (flood zones, soil conditions, etc.)
           - Utilities availability (water, sewer, electricity, internet)
           - Access and transportation infrastructure
        
        2. **Local Demographics & Economics**
           - Population trends and projections
           - Economic indicators (income levels, employment rates)
           - Housing market analysis (demand, pricing, trends)
           - Commercial activity and development in the area
           - Local amenities and services
        
        3. **Regulatory Environment**
           - Local government attitude toward development
           - Recent similar projects and their reception
           - Incentives or restrictions for development
           - Building codes and construction requirements
           - Timeline for typical approval processes
        
        4. **Competitive Analysis**
           - Similar properties in the market
           - Recent land sales and valuations
           - Existing and planned competing developments
           - Market gaps and opportunities
        
        5. **Future Outlook**
           - Planned infrastructure improvements
           - Long-term development plans for the area
           - Anticipated regulatory changes
           - Factors that could affect property value over time
        """
        
        task_expected_output = "A comprehensive research report covering all the requested aspects of the property and its surrounding area."
        
        from crewai import Task
        
        # Create and return the task with the new configuration
        try:
            # First try with self as agent (newer crewai versions)
            return Task(
                description=task_description,
                expected_output=task_expected_output,
                agent=self
            )
        except Exception as e:
            # Fallback to self.agent (older crewai versions)
            return Task(
                description=task_description,
                expected_output=task_expected_output,
                agent=self.agent
            )

    def _get_property_context(self, property_data):
        """
        Create a context list from property data for use in tasks.
        
        Args:
            property_data: Dictionary containing property information
            
        Returns:
            list: Context strings with property information
        """
        context = []
        
        # Basic property information
        if 'Property Address' in property_data:
            context.append(f"Property Address: {property_data['Property Address']}")
            
        if 'City' in property_data and 'State' in property_data:
            context.append(f"Location: {property_data['City']}, {property_data['State']}")
            
        if 'Land Area (AC)' in property_data:
            context.append(f"Size: {property_data['Land Area (AC)']} acres")
            
        if 'Zoning' in property_data:
            context.append(f"Current Zoning: {property_data['Zoning']}")
            
        if 'Latitude' in property_data and 'Longitude' in property_data:
            context.append(f"Coordinates: {property_data['Latitude']}, {property_data['Longitude']}")
            
        # Additional property details if available
        if 'County Name' in property_data:
            context.append(f"County: {property_data['County Name']}")
            
        if 'Proposed Land Use' in property_data:
            context.append(f"Proposed Land Use: {property_data['Proposed Land Use']}")
            
        if 'In SFHA' in property_data:
            context.append(f"In Special Flood Hazard Area: {property_data['In SFHA']}")
            
        if 'Fema Flood Zone' in property_data:
            context.append(f"FEMA Flood Zone: {property_data['Fema Flood Zone']}")
            
        # Add demographic information if available
        population_keys = [k for k in property_data.keys() if 'Population' in k]
        if population_keys:
            context.append("Population data available in property data")
            
        income_keys = [k for k in property_data.keys() if 'Income' in k or 'Inc' in k]
        if income_keys:
            context.append("Income data available in property data")
            
        housing_keys = [k for k in property_data.keys() if 'Home Value' in k or 'Housing' in k]
        if housing_keys:
            context.append("Housing value data available in property data")
        
        return context 

    def create_research_task(self, query):
        """
        Create a task for general property research.
        
        Args:
            query (str): The research query to execute
            
        Returns:
            Task: A task to perform property research
        """
        from crewai import Task
        
        return Task(
            description=query,
            expected_output="A comprehensive research report that addresses all the requested information in a structured format.",
            agent=self.agent
        ) 