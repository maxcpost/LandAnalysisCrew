#!/usr/bin/env python3
"""
Example script that demonstrates analyzing a property.
This script loads a property from the dataset and runs a complete analysis.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import time
import json
from typing import List, Dict, Any, Optional
import traceback

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import project modules
from src.data.loader import PropertyDataLoader
from src.models.crew import PropertyAnalysisCrew
from src.utils.system import check_ollama_installed, check_ollama_running, setup_ollama_model
from src.utils.formatting import print_header, print_error, print_info, print_warning
from src.utils.llm import setup_llm as setup_llm_util

# Load environment variables
load_dotenv()

class MockLLM:
    """
    Mock implementation of an LLM for testing.
    This implements the interface required by crewai.
    """
    
    def __init__(self, model_name="llama3", temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature
        print(f"[MockLLM] Initialized with model={model_name}, temperature={temperature}")
    
    def completion(self, model=None, messages=None, **kwargs):
        """
        Mock implementation of the completion API.
        Returns a response in the expected format.
        """
        print(f"\n[MockLLM] Generating completion for messages: {len(messages)}")
        time.sleep(0.5)  # Simulate processing time
        
        # Extract the last message content to generate a relevant response
        last_message = messages[-1]['content'] if messages else ""
        topic = "property analysis"
        if "zoning" in last_message.lower():
            topic = "zoning"
        elif "utility" in last_message.lower() or "infrastructure" in last_message.lower():
            topic = "utilities"
        elif "environmental" in last_message.lower():
            topic = "environmental factors"
        
        # Create a mock response based on the identified topic
        content = self._generate_mock_response(topic)
        
        # Return a response in the expected completion format
        return {
            "id": "mock-completion-id",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model or self.model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 150,
                "total_tokens": 250
            }
        }
    
    def _generate_mock_response(self, topic):
        """Generate a mock response based on the topic."""
        responses = {
            "property analysis": """
Based on my research, here's what I found about 8053 Oak Orchard Rd in Batavia, NY:

## Property History
- The property has been used for agricultural purposes for many years
- There are no records of previous development proposals
- Last sold in 2010 for approximately $450,000

## Zoning and Land Use
- Currently zoned as Agricultural/Residential (AR)
- Allows for residential development with proper permits
- Density allowed: approximately 4-6 units per acre
- Height restrictions: 35 feet maximum

## Utilities and Infrastructure
- Public water available at the road
- No public sewer (septic systems required)
- Electricity available 
- Natural gas lines nearby but may require extension
- Broadband available through Spectrum

## Environmental Factors
- Not in a flood zone (Zone X)
- Gently sloping terrain, generally good for development
- Soil is primarily well-draining loam
- No known environmental contamination issues

## Nearby Amenities
- Schools: Batavia School District (4 miles)
- Shopping: Batavia town center (5 miles)
- Healthcare: United Memorial Medical Center (6 miles)
- Parks: Genesee County Park (3 miles)

## Transportation
- Direct access to Oak Orchard Road (moderate traffic)
- 3 miles from NY-98
- 7 miles from I-90 (NYS Thruway)
- No public transportation directly serving the property
- Walk score: 25/100 (car-dependent)

The property shows good potential for residential development due to its size, access to utilities, and proximity to Batavia. The main challenges would be establishing sewer infrastructure and addressing any zoning changes required for high-density development.
""",
            "zoning": """
The zoning information for 8053 Oak Orchard Rd in Batavia, NY is as follows:

## Current Zoning Designation
- Currently zoned as Agricultural/Residential (AR) in Genesee County
- The property falls under the Town of Batavia's jurisdiction for zoning purposes

## Allowed Uses and Density
- Primary allowed uses: Single-family homes, agricultural activities, and limited commercial farm operations
- Conditional uses: Multi-family housing (requires special permit)
- Base density: 1 unit per acre for single-family homes
- With proper planning approvals: 4-6 units per acre possible through Planned Unit Development (PUD) process

## Recent/Proposed Zoning Changes
- The Town of Batavia updated its comprehensive plan in 2021, which indicates openness to higher-density residential development in this area
- No specific zoning changes are currently proposed for this parcel
- The area is identified as a "growth corridor" in the county's long-term development plan

## Development Requirements
- Setbacks: 50 feet front yard, 25 feet side yards, 50 feet rear yard
- Height restrictions: 35 feet (approximately 2-3 stories) for residential structures
- Lot coverage: Maximum 30% for residential development
- Parking requirements: 2 spaces per dwelling unit
- Open space requirement: 40% for developments larger than 5 acres

## Rezoning Potential
- Potential to request rezoning to Residential (R-2 or R-3) which would allow higher density
- PUD overlay zone is another option that would allow for mixed-use development
- The approval process typically takes 4-6 months and requires public hearings

For high-density residential development, a zoning variance or rezoning application would likely be required. The town has shown willingness to accommodate such developments when infrastructure concerns are adequately addressed.
""",
            "utilities": """
Here's the detailed utility and infrastructure information for 8053 Oak Orchard Rd in Batavia, NY:

## Water
- Public water supply is available at Oak Orchard Road
- Water pressure: Approximately 60-65 PSI (adequate for residential development)
- Water capacity: The municipal system has capacity for additional connections
- Connection fees: Approximately $3,500-$4,500 per connection
- On-site infrastructure needed: Water distribution system throughout development

## Sewer
- No public sewer system directly available at the property
- Nearest sewer connection point is approximately 1.2 miles south
- Options:
  1. Extend public sewer (estimated cost: $250-350 per linear foot)
  2. Develop on-site wastewater treatment system (for larger developments)
  3. Individual septic systems (would reduce density potential)
- Genesee County Sewer District would need to approve any sewer extension plans

## Electricity
- Service provided by National Grid
- 3-phase power available along Oak Orchard Road
- Capacity: Sufficient for residential development
- Connection costs: Standard residential connections approximately $1,500-2,500 per unit
- Distribution infrastructure needed on-site

## Natural Gas
- National Grid provides natural gas service
- Gas main located along Oak Orchard Road
- Capacity is sufficient for residential development
- Connection costs are standard for the area

## Telecommunications
- Spectrum provides broadband internet (up to 400 Mbps)
- Verizon provides DSL and phone service
- Fiber optic potential within 2-3 years according to county development plans
- Cell coverage is good from major carriers (Verizon, AT&T, T-Mobile)

## Road Access
- Direct access to Oak Orchard Road (county-maintained, good condition)
- Road width: 22 feet with shoulders
- Traffic volume: Moderate (approximately 4,500 vehicles per day)
- Access point will require county highway department approval
- Turn lanes likely required for larger developments

## Drainage
- The property has several natural drainage swales
- Stormwater management will require detention facilities
- Existing culverts at road frontage appear adequately sized
- Site has generally good drainage characteristics

The primary infrastructure challenge is sewer service. Developing with individual septic systems would limit density, while extending public sewer would add significant cost but allow for higher-density development. All other utilities are readily available for connection, making the property viable for development from an infrastructure perspective.
""",
            "environmental factors": """
# Environmental Assessment for 8053 Oak Orchard Rd, Batavia, NY

## Flood Zone Status
- Property is primarily located in Zone X (minimal flood hazard)
- According to FEMA maps, the property is outside the 500-year floodplain
- A small section along the western boundary (approximately 3 acres) has some potential for occasional ponding after major storm events
- No historical flooding issues reported

## Soil Conditions
- Predominant soil types: Appleton silt loam (40%), Kendaia silt loam (35%), and Lyons silty clay loam (25%)
- Drainage characteristics: Moderately well-drained to somewhat poorly drained
- Percolation rates: 20-30 minutes per inch (moderate)
- Bearing capacity: Estimated 2,000-3,000 psf (suitable for residential construction)
- Soil pH ranges from 6.2-7.1 (slightly acidic to neutral)
- Low to moderate shrink-swell potential

## Topography and Drainage
- Elevation range: 628-645 feet above sea level
- Generally gentle slopes (2-6% grade) across most of the property
- A modest ridge runs north-south through the eastern portion
- Natural drainage patterns flow generally southwest
- Several small seasonal streams cross the western portion of the property
- No significant steep slopes that would impede development

## Wetlands and Water Features
- USGS National Wetlands Inventory indicates approximately 4-5 acres of potential wetlands in the southwest corner
- A small pond (approximately 0.3 acres) is located in the southern portion
- Some hydric soils present in low-lying areas
- A Phase I wetland delineation would be recommended prior to development planning

## Environmental Hazards
- No known contamination or environmental cleanup sites on the property
- Historical aerial photos show continuous agricultural use since at least 1950
- No evidence of underground storage tanks
- No known history of industrial or commercial use that would suggest contamination
- Radon levels in this area are generally low to moderate (2-4 pCi/L)

## Wildlife and Vegetation
- No known endangered or threatened species on the property
- Property is primarily agricultural fields with some woodlots on the western edge
- Potential habitat for common species but no critical habitat designations
- Tree cover is approximately 15% of the total acreage

## Climate Considerations
- USDA Hardiness Zone: 6a
- Annual precipitation: 36-40 inches
- Average snowfall: 85-95 inches
- Prevailing winds from the southwest

Overall, the environmental conditions are generally favorable for residential development. The main considerations would be addressing the potential wetlands in the southwest corner and implementing appropriate stormwater management practices. A formal Phase I Environmental Site Assessment would be recommended before proceeding with development.
"""
        }
        
        return responses.get(topic, responses["property analysis"])
        
    def call(self, **kwargs):
        """
        Direct function call version for use with CrewAI.
        
        Args:
            model: The model name (ignored in mock)
            messages: List of message dictionaries
            **kwargs: Additional arguments (ignored in mock)
            
        Returns:
            str: The mock completion content
        """
        # Extract messages if present
        messages = kwargs.get("messages", [])
        
        # Get mock response
        response = self.completion(messages=messages)
        
        # Extract and return just the content for compatibility
        return response["choices"][0]["message"]["content"]
        
    def __call__(self, **kwargs):
        """Legacy support for direct function call."""
        return self.call(**kwargs)

def setup_llm():
    """Set up the language model based on environment variables."""
    # Use our centralized LLM utility module with CrewAI compatibility
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true" or "--use-mock" in sys.argv
    
    # Set to use the CrewAI adapter
    return setup_llm_util(
        use_mock=use_mock,
        for_crewai=True,  # Use the CrewAI-compatible adapter
        model_name=os.getenv("OLLAMA_MODEL", "llama3"),
        base_url=os.getenv("OLLAMA_API_BASE", "http://localhost:11434"),
        temperature=float(os.getenv("CREW_TEMPERATURE", "0.7")),
        verbose=True
    )

def display_usage():
    """Display usage information."""
    print("Usage: python analyze_property.py <stock_number>")
    print("")
    print("Analyzes a property from the database for high-density residential development.")
    print("")
    print("Example:")
    print("  python analyze_property.py NY-00004")
    print("")
    print("To see available properties:")
    print("  ../scripts/run.sh --list")
    print("")

def main():
    """Run a property analysis."""
    try:
        # Check command-line arguments
        if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
            display_usage()
            sys.exit(0 if sys.argv[1] in ["-h", "--help"] else 1)
            
        stock_number = sys.argv[1]
        
        # Load property data
        loader = PropertyDataLoader()
        property_data = loader.get_property_data(stock_number)
        
        if property_data is None:
            print_error(f"Property with stock number '{stock_number}' not found.")
            print_info("Run './scripts/run.sh --list' to see available properties.")
            sys.exit(1)
        
        # Set up the language model
        llm = setup_llm()
        
        # Create the crew for property analysis
        crew = PropertyAnalysisCrew(property_data, llm)
        
        try:
            # Run the analysis
            results = crew.analyze_property()
            print_info(f"Return values from analyze_property: {len(results)} items")
            
            # Unpack the return values based on length
            if len(results) == 3:
                # Backward compatibility with older API
                full_report, executive_summary, report_path = results
                investment_summary = None
            elif len(results) == 4:
                # New API with investment summary
                full_report, executive_summary, investment_summary, report_path = results
            else:
                raise ValueError(f"Unexpected number of return values: {len(results)}")
            
            # Print executive summary
            print_header("EXECUTIVE SUMMARY")
            print(executive_summary)
            print(f"\nFull report saved to: {report_path}")
            
            # Exit with success code
            sys.exit(0)
        except ValueError as e:
            # Handle unpacking error
            print_error(f"Error unpacking results: {str(e)}")
            print_info("analyze_property() returned unexpected number of values.")
            sys.exit(1)
        except KeyError as e:
            # Handle CrewOutput format errors
            print_error(f"Error processing crew results: {str(e)}")
            print_info("The analysis produced partial results but could not be completed.")
            sys.exit(1)
        except Exception as e:
            # Handle other exceptions
            print_error(f"Error analyzing property: {str(e)}")
            print_error(traceback.format_exc())
            sys.exit(1)
    except Exception as e:
        # Handle top-level exceptions
        print_error(f"Error: {str(e)}")
        print_error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main()) 