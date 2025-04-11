#!/usr/bin/env python3
"""
Report Generator Agent for Land Analysis Crew.
Produces comprehensive property analysis reports based on data from other agents.
"""

from crewai import Agent, Task
from textwrap import dedent

class ReportGenerator:
    """Agent for generating comprehensive property analysis reports."""

    def __init__(self, llm=None):
        """
        Initialize the report generator agent.
        
        Args:
            llm: Language model to use for the agent (optional)
        """
        from crewai import Agent
        
        # Set up agent
        self.agent = Agent(
            role="Property Development Report Generator",
            goal="Create comprehensive, data-driven property development reports with clear recommendations",
            backstory="""You are an expert report writer specializing in real estate development with 
            10 years of experience creating professional investment analysis documents. You excel at 
            synthesizing complex property data, market research, and financial analysis into clear, 
            structured reports that guide investment decisions.
            
            You've written over 300 property analysis reports for developers, investors, and real 
            estate funds. Your reports are known for their thoroughness, clarity, and actionable 
            recommendations. You have a talent for distilling technical details into accessible 
            insights while maintaining the depth required for sophisticated real estate professionals.""",
            verbose=True,
            llm=llm
        )
        
    def create_report_task(self, property_data, research_data, market_analysis, data_analysis):
        """
        Create a task for generating a comprehensive report.
        
        Args:
            property_data: Dictionary of property data
            research_data: Property research data
            market_analysis: Market analysis data
            data_analysis: Financial analysis data
            
        Returns:
            Task: Task to execute in a crew
        """
        # Extract address components for better prompting
        address = property_data.get('Property Address', 'Unknown')
        city = property_data.get('City', 'Unknown')
        state = property_data.get('State', 'Unknown')
        
        # Create task description
        task_description = f"""
        Generate a comprehensive investment property analysis report for {address}, {city}, {state}.
        
        Use the following data compiled from previous analyses to create your report:
        
        1. Property Research Data:
        {research_data}
        
        2. Market Analysis:
        {market_analysis}
        
        3. Data Analysis:
        {data_analysis}
        
        Your report should include:
        
        1. Executive Summary: A concise overview of key findings and recommendations.
        
        2. Property Overview:
           - Location analysis and neighborhood characteristics
           - Current property status and features
           - Zoning and legal considerations
        
        3. Market Analysis:
           - Local real estate market trends
           - Demographic analysis and projections
           - Economic indicators affecting the property
        
        4. Development Potential:
           - Highest and best use analysis
           - Development scenarios with pros/cons
           - Regulatory considerations and timeline
        
        5. Financial Analysis:
           - Current valuation assessment
           - Development cost projections
           - Revenue potential analysis
           - ROI calculations for various scenarios
           - Risk assessment and sensitivity analysis
        
        6. Investment Recommendations:
           - Optimal development strategy
           - Investment timeline and milestones
           - Exit strategy options
           - Key success factors and contingency plans
        
        7. Appendices:
           - Detailed data tables
           - Comparable property analysis
           - Sources and methodology
        
        The report should be comprehensive yet accessible, with a professional tone suitable for sophisticated real estate investors.
        """
        
        task_expected_output = "A complete investment property analysis report in markdown format with all sections described above."
        
        from crewai import Task
        
        # Create and return the task with the new configuration
        return Task(
            description=task_description,
            expected_output=task_expected_output,
            agent=self.agent
        )
        
    def create_executive_summary_task(self, property_data, property_potential, full_report):
        """
        Create a task to generate a concise executive summary from a full report.
        
        Args:
            property_data (dict): The property data
            property_potential (str): The property potential analysis
            full_report (str): Complete property analysis report
            
        Returns:
            Task: Task to execute in a crew
        """
        # Extract address components for better prompting
        address = property_data.get('Property Address', 'Unknown')
        city = property_data.get('City', 'Unknown')
        state = property_data.get('State', 'Unknown')
        
        return Task(
            description=dedent(f"""
                Create a concise executive summary for the property at {address}, {city}, {state}.
                
                Use the following information to create your summary:
                
                Property Potential Analysis:
                {property_potential}
                
                Full Property Report:
                {full_report}
                
                The executive summary should include:
                1. Property Overview - Brief description, key features, current status
                2. Key Findings - Most important insights from all analyses
                3. Development Recommendations - Top 2-3 development strategies
                4. Critical Considerations - Major challenges or special opportunities
                5. Next Steps - Recommended actions for moving forward
                
                The executive summary should be 1-2 pages (about 500-800 words) in Markdown format.
                Focus on being brief but comprehensive. Use bullet points where appropriate.
                The tone should be professional and objective.
            """),
            expected_output="Executive summary in Markdown format with all sections specified above.",
            agent=self.agent
        )
    
    def create_investment_summary_task(self, property_data, property_potential, executive_summary):
        """
        Create a task for the report generator agent to produce an investment summary for the property.
        
        Args:
            property_data (dict): The property data
            property_potential (str): The property potential analysis
            executive_summary (str): The executive summary
            
        Returns:
            Task: The task for creating an investment summary
        """
        # Extract address components for better prompting
        address = property_data.get('Property Address', 'Unknown')
        city = property_data.get('City', 'Unknown')
        state = property_data.get('State', 'Unknown')
        
        return Task(
            description=f"""
            Create a focused investment summary for the property at {address}, {city}, {state}.
            Use information from both the property analysis and the executive summary.
            
            Property Analysis:
            {property_potential}
            
            Executive Summary:
            {executive_summary}
            
            The investment summary should include:
            1. Key Financial Metrics - ROI, IRR, NPV, Payback Period
            2. Investment Scenario Analysis - Best/Likely/Worst cases
            3. Comparative Market Analysis - How this property compares to similar properties
            4. Investment Strategy Recommendations - Development type, phasing, timelines
            5. Risk Factors and Mitigation Strategies
            
            The investment summary should be formatted in Markdown and be suitable for presentation to potential investors.
            """,
            expected_output="Investment summary in Markdown format with all sections specified above.",
            agent=self.agent
        )
        
    def generate_report(self, 
                        property_data, 
                        demographic_analysis, 
                        market_analysis, 
                        environmental_data):
        """
        Generate a comprehensive property analysis report.
        
        Args:
            property_data: Basic property information
            demographic_analysis: Demographic data analysis
            market_analysis: Market trend analysis
            environmental_data: Environmental analysis
            
        Returns:
            str: Formatted report text
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_report_task method with a crew."
        
    def generate_executive_summary(self, full_report):
        """
        Generate a concise executive summary from a full report.
        
        Args:
            full_report: Complete property analysis report
            
        Returns:
            str: Executive summary text
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_executive_summary_task method with a crew."
    
    def create_investment_one_pager(self, property_data, demographic_data, market_data):
        """
        Create a one-page investment summary for potential investors.
        
        Args:
            property_data: Basic property information
            demographic_data: Key demographic highlights
            market_data: Key market trends
            
        Returns:
            str: One-page investment summary
        """
        # For backward compatibility - create a task but note it needs a crew to execute
        return "To execute this task, please use the create_investment_summary_task method with a crew."

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