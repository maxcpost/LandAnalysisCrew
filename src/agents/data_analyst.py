#!/usr/bin/env python3
"""
Data Analysis Agent for Land Analysis Crew.
Analyzes property data, demographics, and market metrics to identify development opportunities.
"""

from crewai import Agent, Task
from textwrap import dedent

class DataAnalyst:
    """Agent for analyzing property financial data and development potential."""

    def __init__(self, llm=None):
        """
        Initialize the data analysis agent.
        
        Args:
            llm: Language model to use for the agent (optional)
        """
        from crewai import Agent
        
        # Set up agent
        self.agent = Agent(
            role="Property Data Analyst",
            goal="Analyze property data to determine investment potential and highest best use",
            backstory="""You are a senior data analyst specializing in real estate with 15 years of 
            experience evaluating properties for development potential. Your expertise includes 
            financial modeling, ROI analysis, and market valuation. You have a background in both 
            residential and commercial property analysis and are skilled at identifying the most 
            profitable development strategies based on property characteristics and market data.
            
            You've successfully analyzed over 500 properties, helping developers make informed decisions 
            that have led to profitable investments. Your analysis needs to be data-driven, 
            comprehensive, and contain actionable insights.""",
            verbose=True,
            llm=llm
        )
        
    def create_property_potential_task(self, property_data, demographic_data, market_data):
        """
        Create a task to analyze a property's development potential.
        
        Args:
            property_data: Basic property information
            demographic_data: Demographic analysis for the area
            market_data: Market analysis for the area
            
        Returns:
            Task: Task to execute in a crew
        """
        return Task(
            description=dedent(f"""
                Analyze the development potential of the property located at 
                {property_data.get('Property Address', 'N/A')}, {property_data.get('City', 'N/A')}, 
                {property_data.get('State', 'N/A')} for high-density residential development.
                
                Use the following data in your analysis:
                
                Property Information:
                - Size: {property_data.get('Land Area (AC)', 'N/A')} acres
                - Listed Price: ${property_data.get('For Sale Price', 'N/A')}
                - Zoning: {property_data.get('Zoning', 'N/A')}
                
                Demographic Data:
                {demographic_data}
                
                Market Data:
                {market_data}
                
                Your analysis should include:
                
                1. Development Capacity
                   - Estimate the potential number of units based on size and zoning
                   - Analyze potential for different housing types (apartments, townhomes, etc.)
                   - Consider mixed-use potential if appropriate
                
                2. Financial Feasibility
                   - Calculate land cost per potential unit
                   - Estimate development costs based on local market
                   - Project potential revenue based on local rental/sales rates
                   - Calculate rough ROI and compare to industry standards
                
                3. Demographic Alignment
                   - Analyze how well the site matches demographic trends
                   - Identify target resident profiles for the development
                   - Determine if there's sufficient demand for the proposed units
                
                4. Market Position
                   - Evaluate competition in the immediate market
                   - Identify unique selling points for this location
                   - Assess absorption rate potential
                
                5. Risk Assessment
                   - Identify key risks specific to this property
                   - Suggest risk mitigation strategies
                   - Rate the overall risk level (low, medium, high)
                
                6. Opportunity Score
                   - On a scale of 1-10, rate this property's overall potential
                   - Justify your rating with specific factors
                
                Use specific numbers and data points throughout your analysis. 
                Be objective but provide a clear recommendation about whether this property
                represents a good opportunity for high-density residential development.
            """),
            expected_output=dedent("""
                A detailed analysis of the property's development potential that includes all 
                requested sections. The analysis should use specific numbers and calculations
                where possible, and should provide clear, data-backed conclusions about the
                property's potential. The report should be well-structured with clear section
                headings and a final recommendation.
            """),
            agent=self.agent
        )
        
    def create_property_comparison_task(self, properties_data, criteria=None):
        """
        Create a task to compare multiple properties based on development potential.
        
        Args:
            properties_data: List of property data dictionaries
            criteria: Optional dictionary of weighting criteria
            
        Returns:
            Task: Task to execute in a crew
        """
        # Default criteria if none provided
        if criteria is None:
            criteria = {
                "land_cost_per_acre": 0.25,
                "location_quality": 0.20,
                "development_capacity": 0.20,
                "regulatory_environment": 0.15,
                "market_strength": 0.20
            }
        
        # Extract properties for display in the task description
        properties_summary = "\n\n".join([
            f"Property {i+1}: {prop.get('Property Address', 'N/A')}, {prop.get('City', 'N/A')}, {prop.get('State', 'N/A')}"
            f"\n- Size: {prop.get('Land Area (AC)', 'N/A')} acres"
            f"\n- Price: ${prop.get('For Sale Price', 'N/A')}"
            for i, prop in enumerate(properties_data)
        ])
        
        # Create criteria description
        criteria_desc = "\n".join([f"- {key} ({value * 100}%)" for key, value in criteria.items()])
        
        return Task(
            description=dedent(f"""
                Compare the following properties for their potential for high-density 
                residential development:
                
                {properties_summary}
                
                Create a structured comparison using the following criteria and weights:
                {criteria_desc}
                
                For each property, you should:
                
                1. Calculate a score for each criterion on a scale of 1-10
                2. Apply the appropriate weighting to each score
                3. Calculate a total weighted score
                4. Rank the properties from best to worst opportunity
                
                Additionally, provide:
                
                - A brief explanation of each score
                - Pros and cons for each property
                - A clear recommendation on which property represents the best development opportunity
                
                Your analysis should be data-driven and objective, using specific metrics
                where possible. Consider factors like cost per potential unit, location advantages,
                market strength, regulatory hurdles, and development capacity.
            """),
            expected_output=dedent("""
                A comprehensive comparison of the properties with clear scoring for each criterion,
                weighted totals, and rankings. The analysis should include explanations for each
                score, pros and cons for each property, and a final recommendation with 
                supporting rationale. The format should be clear and easy to understand, with
                tables or structured data presentation where appropriate.
            """),
            agent=self.agent
        )
        
    def create_demographic_trends_task(self, demographic_data, property_location):
        """
        Create a task to analyze demographic trends for a specific location.
        
        Args:
            demographic_data: Demographic data for analysis
            property_location: City, state or specific location
            
        Returns:
            Task: Task to execute in a crew
        """
        return Task(
            description=dedent(f"""
                Analyze the demographic trends for {property_location} and their implications
                for high-density residential development. 
                
                Use the following demographic data in your analysis:
                {demographic_data}
                
                Your analysis should include:
                
                1. Population Growth Analysis
                   - Current population and growth trends
                   - Projections for future growth
                   - Age distribution shifts
                   - Migration patterns
                
                2. Household Formation Trends
                   - Household size changes
                   - Single vs. family households
                   - Rental vs. ownership preferences
                   - Impact on housing demand
                
                3. Income and Affordability
                   - Income distribution and trends
                   - Housing affordability metrics
                   - Rent/price-to-income ratios
                   - Optimal price points for new development
                
                4. Target Market Segments
                   - Identify key demographic groups driving housing demand
                   - Analyze their housing preferences and needs
                   - Estimate the size of each target segment
                   - Recommend unit mix and amenities based on demographics
                
                5. Employment Trends
                   - Major employment sectors and growth
                   - Commuting patterns
                   - Impact on housing demand
                   - Future employment projections
                
                6. Development Implications
                   - How the demographic trends support or challenge high-density development
                   - Specific recommendations for unit types, sizes, and amenities
                   - Pricing strategy recommendations
                   - Marketing approach for identified demographic segments
                
                Be specific and use actual figures from the data where possible. Focus on
                actionable insights that would inform development decisions.
            """),
            expected_output=dedent("""
                A detailed analysis of demographic trends with specific implications for
                development. The analysis should reference actual data points and provide
                clear, specific recommendations for unit mix, pricing, and amenities based
                on the demographic analysis. The report should identify specific target
                markets with their size, preferences, and optimal product design.
            """),
            agent=self.agent
        )

    def analyze_property_potential(self, property_data, demographic_data, market_data):
        """
        Analyze a property's development potential based on various data points.
        
        Args:
            property_data: Basic property information
            demographic_data: Demographic analysis for the area
            market_data: Market analysis for the area
            
        Returns:
            str: Property potential analysis
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_property_potential_task method with a crew."
        
    def compare_properties(self, properties_data, criteria=None):
        """
        Compare multiple properties based on development potential.
        
        Args:
            properties_data: List of property data dictionaries
            criteria: Optional dictionary of weighting criteria
            
        Returns:
            str: Property comparison analysis
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_property_comparison_task method with a crew."
        
    def analyze_demographic_trends(self, demographic_data, property_location):
        """
        Analyze demographic trends for a specific location.
        
        Args:
            demographic_data: Demographic data for analysis
            property_location: City, state or specific location
            
        Returns:
            str: Demographic trend analysis
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_demographic_trends_task method with a crew."

    def analyze_property_valuation(self, address, city, state, current_valuation, development_potential, investment_analysis, market_position):
        """
        Analyze a property's valuation based on various data points.
        
        Args:
            address: Property address
            city: City of the property
            state: State of the property
            current_valuation: Current market value of the property
            development_potential: Potential for different development types
            investment_analysis: Investment analysis for different scenarios
            market_position: Property's competitive position in the local real estate market
            
        Returns:
            str: Property valuation analysis
        """
        # Create a task for the data analyst
        task = Task(
            description=f"""
            Analyze the provided property data for {address}, {city}, {state}.
            
            Your analysis should include:
            
            1. **Current Valuation**:
               - Analyze current market value based on comparable sales
               - Calculate price per square foot/acre compared to local market
               - Identify key factors affecting current value
            
            2. **Development Potential**:
               - Evaluate potential for different development types (residential, commercial, mixed-use)
               - Estimate development costs including land prep, utilities, construction
               - Calculate potential ROI for different development scenarios
            
            3. **Investment Analysis**:
               - Conduct 5-year and 10-year ROI projections for different scenarios
               - Compare investment potential to other opportunities in the region
               - Identify key risk factors and mitigations
               - Calculate potential cash flow for income-producing developments
            
            4. **Market Position**:
               - Analyze property's competitive position in the local real estate market
               - Identify target demographic and demand assessment
               - Evaluate market absorption rate for developed units
            
            Document all assumptions made in your calculations and cite market data sources.
            """,
            expected_output="A comprehensive financial analysis including current valuation, development potential, ROI projections, and market position assessment.",
            agent=self
        )
        
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the analyze_property_valuation method with a crew."

    def create_financial_analysis_task(self, property_data):
        """
        Create a task for financial analysis of a property.
        
        Args:
            property_data: Dictionary of property data
            
        Returns:
            Task: Task to execute in a crew
        """
        # Extract address components for better prompting
        address = property_data.get('Property Address', 'Unknown')
        city = property_data.get('City', 'Unknown')
        state = property_data.get('State', 'Unknown')
        
        # Create task description
        task_description = f"""
        Analyze the provided property data for {address}, {city}, {state}.
        
        Your analysis should include:
        
        1. **Current Valuation**:
           - Analyze current market value based on comparable sales
           - Calculate price per square foot/acre compared to local market
           - Identify key factors affecting current value
        
        2. **Development Potential**:
           - Evaluate potential for different development types (residential, commercial, mixed-use)
           - Estimate development costs including land prep, utilities, construction
           - Calculate potential ROI for different development scenarios
        
        3. **Investment Analysis**:
           - Conduct 5-year and 10-year ROI projections for different scenarios
           - Compare investment potential to other opportunities in the region
           - Identify key risk factors and mitigations
           - Calculate potential cash flow for income-producing developments
        
        4. **Market Position**:
           - Analyze property's competitive position in the local real estate market
           - Identify target demographic and demand assessment
           - Evaluate market absorption rate for developed units
        
        Document all assumptions made in your calculations and cite market data sources.
        """
        
        task_expected_output = "A comprehensive financial analysis including current valuation, development potential, ROI projections, and market position assessment."
        
        from crewai import Task
        
        # Create and return the task with the new configuration
        return Task(
            description=task_description,
            expected_output=task_expected_output,
            agent=self
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