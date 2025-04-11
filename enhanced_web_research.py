#!/usr/bin/env python3
"""
Enhanced Web Research Tool
Provides advanced search capabilities with specialized search templates, 
location-specific query modifiers, and structured result storage.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

class EnhancedWebResearchTool:
    """Tool for conducting web research with enhanced search strategies."""
    
    # Specialized search templates organized by category
    SEARCH_TEMPLATES = {
        "economic_development": [
            "{location} economic development news past year",
            "{location} new business opening 2023 2024",
            "{location} major employer hiring expanding",
            "{location} economic growth statistics recent",
            "{location} upcoming development projects",
            "{location} job market trends"
        ],
        "housing_market": [
            "{location} housing market analysis 2024",
            "{location} affordable housing initiative",
            "{location} housing shortage statistics",
            "{location} new housing development project",
            "{location} manufactured home community zoning",
            "{location} rental market trends 2024"
        ],
        "infrastructure": [
            "{location} infrastructure improvement plan",
            "{location} road expansion project",
            "{location} utilities upgrade plan",
            "{location} transportation development",
            "{location} broadband expansion rural",
            "{location} water sewer capacity development"
        ],
        "government_policy": [
            "{location} zoning changes residential development",
            "{location} new property development regulations",
            "{location} tax incentives housing development",
            "{location} permitting process development",
            "{location} planning commission decisions recent",
            "{location} development impact fees"
        ],
        "community_factors": [
            "{location} school district performance ranking",
            "{location} crime statistics trends",
            "{location} quality of life ranking",
            "{location} recreational facilities development",
            "{location} community sentiment growth survey",
            "{location} healthcare facilities access"
        ]
    }
    
    def __init__(self):
        # Try to import the DuckDuckGo search library
        try:
            from duckduckgo_search import DDGS
            self.search_engine = DDGS()
            self.search_available = True
        except ImportError:
            print("DuckDuckGo search library not available. Web research will be limited.")
            self.search_available = False
        
        # Initialize storage for search results
        self.search_results = {
            "search_results": [],
            "meta_analysis": {
                "economic_climate": {"growth_indicators": {}, "detected_trends": []},
                "housing_market": {"detected_trends": []},
                "government_policy": {"detected_trends": []},
                "infrastructure": {"detected_projects": []},
                "community_factors": {"notable_features": []}
            },
            "location_context": {}
        }
        
        # Track searches to avoid duplicates
        self.executed_searches = set()
    
    def create_location_context(self, property_data):
        """Create a hierarchical location context from property data."""
        city = property_data.get('City', '')
        county = property_data.get('County Name', '')
        state = property_data.get('State', '')
        zip_code = property_data.get('Zip', '')
        
        # Store in the search results
        self.search_results["location_context"] = {
            "city": city,
            "county": county,
            "state": state,
            "zip_codes": [zip_code] if zip_code else [],
            "full_location": f"{city}, {county}, {state}".replace(", ,", ",").strip(", ")
        }
        
        return self.search_results["location_context"]
    
    def build_location_query(self, location_context, specificity_level='medium'):
        """
        Build location query string with appropriate specificity.
        
        specificity_level: 'high', 'medium', or 'low'
        """
        city = location_context.get('city', '')
        county = location_context.get('county', '')
        state = location_context.get('state', '')
        
        if specificity_level == 'high' and city and county and state:
            return f"{city} {county} County {state}"
        elif specificity_level == 'medium' and city and state:
            return f"{city} {state}"
        elif specificity_level == 'low' and (city or county) and state:
            return f"{city or county} area {state}"
        else:
            # Fallback to whatever location data we have
            return location_context.get('full_location', '')
    
    def execute_search_strategy(self, property_data, category=None, max_results_per_query=3, max_queries=3):
        """
        Execute a comprehensive search strategy using templated queries.
        
        Args:
            property_data: Dictionary containing property information
            category: Optional category to focus search on (or None for all categories)
            max_results_per_query: Maximum results to return per query
            max_queries: Maximum number of queries to execute per category
            
        Returns:
            Dictionary of structured search results
        """
        if not self.search_available:
            return {
                "error": "Search unavailable",
                "message": "DuckDuckGo search library not installed."
            }
        
        # Create location context if not already done
        if not self.search_results["location_context"]:
            self.create_location_context(property_data)
        
        location_context = self.search_results["location_context"]
        
        # Determine which categories to search
        categories = [category] if category else self.SEARCH_TEMPLATES.keys()
        
        for search_category in categories:
            # Get templates for this category
            templates = self.SEARCH_TEMPLATES.get(search_category, [])
            
            # Limit the number of templates we'll use
            templates = templates[:max_queries]
            
            # Try different specificity levels if needed
            for specificity_level in ['medium', 'high', 'low']:
                location_query = self.build_location_query(location_context, specificity_level)
                
                # Skip empty location queries
                if not location_query:
                    continue
                
                for template in templates:
                    # Format the template with the location
                    query = template.format(location=location_query)
                    
                    # Skip if we've already run this query
                    if query in self.executed_searches:
                        continue
                    
                    # Execute the search
                    try:
                        results = self.search_engine.text(query, max_results=max_results_per_query)
                        self.executed_searches.add(query)
                        
                        # If we got results, store them and go to next template
                        if results and len(results) > 0:
                            timestamp = datetime.now().isoformat()
                            
                            # Process and store the results
                            structured_results = {
                                "category": search_category,
                                "query": query,
                                "timestamp": timestamp,
                                "results": []
                            }
                            
                            # Add each result with metadata
                            for result in results:
                                structured_result = {
                                    "title": result.get("title", ""),
                                    "url": result.get("href", ""),
                                    "source": self._extract_source_from_url(result.get("href", "")),
                                    "summary": result.get("body", "")[:500],  # First 500 chars
                                    "key_points": self._extract_key_points(result.get("body", "")),
                                    "entities": self._extract_entities(result.get("body", "")),
                                    "relevance_score": self._calculate_relevance(result, search_category),
                                    "confidence_rating": "medium"  # Default
                                }
                                
                                structured_results["results"].append(structured_result)
                            
                            # Add aggregate insights
                            structured_results["aggregate_insights"] = self._generate_insights(
                                structured_results["results"], 
                                search_category
                            )
                            
                            # Add to overall results
                            self.search_results["search_results"].append(structured_results)
                            
                            # Add to meta-analysis
                            self._update_meta_analysis(structured_results)
                            
                            # If we got reasonable results, no need to try other specificity levels
                            break
                            
                    except Exception as e:
                        print(f"Error during {search_category} search: {e}")
                        continue
                
                # If we got results for this category, don't try other specificity levels
                if any(r["category"] == search_category for r in self.search_results["search_results"]):
                    break
        
        return self.search_results
    
    def search(self, query, max_results=5, category=None):
        """
        Legacy search method for compatibility.
        For simple, direct searches without the enhanced strategy.
        """
        if not self.search_available:
            return [{"title": "Search unavailable", "body": "DuckDuckGo search library not installed.", "href": ""}]
        
        try:
            # Check if query contains location information
            if query and ":" in query and query.count(":") == 1:
                parts = query.split(":", 1)
                # Check if this is a category specification
                if parts[0].strip().lower() in self.SEARCH_TEMPLATES:
                    category = parts[0].strip().lower()
                    property_data = {"Property Address": parts[1].strip()}
                    results = self.execute_search_strategy(property_data, category)
                    # Convert to old format for backward compatibility
                    return [{"title": r.get("title", ""), 
                             "body": r.get("summary", ""), 
                             "href": r.get("url", "")} 
                            for cat in results.get("search_results", [])
                            for r in cat.get("results", [])]
            
            # Default behavior: direct search
            results = self.search_engine.text(query, max_results=max_results)
            return results
        except Exception as e:
            print(f"Error during web search: {e}")
            return [{"title": "Search error", "body": f"Error performing search: {str(e)}", "href": ""}]
    
    def _extract_source_from_url(self, url):
        """Extract the source name from a URL."""
        if not url:
            return "Unknown source"
        
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Remove www. if present
            if domain.startswith("www."):
                domain = domain[4:]
                
            # Remove .com, .org, etc.
            parts = domain.split(".")
            if len(parts) >= 2:
                return parts[-2].capitalize()
            
            return domain.capitalize()
        except Exception:
            return "Unknown source"
    
    def _extract_key_points(self, text):
        """Extract key points from text. Simplified implementation."""
        if not text:
            return []
        
        # Simple implementation: split by sentences and take first few
        sentences = text.split(". ")
        key_points = sentences[:min(3, len(sentences))]
        return [p.strip() + "." if not p.endswith(".") else p.strip() for p in key_points if p.strip()]
    
    def _extract_entities(self, text):
        """Extract entities from text. Simplified implementation."""
        entities = {
            "organizations": [],
            "locations": [],
            "amounts": []
        }
        
        # This is a simplified implementation
        # In a production system, you might use NLP libraries like spaCy
        
        # Extract dollar amounts with simple regex
        dollar_pattern = r'\$\s*\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:million|billion|m|b))?'
        amounts = re.findall(dollar_pattern, text, re.IGNORECASE)
        if amounts:
            entities["amounts"] = amounts[:5]  # Limit to first 5
            
        return entities
    
    def _calculate_relevance(self, result, category):
        """Calculate relevance score based on category and content."""
        # Simple implementation - a more robust system would use NLP
        if not result or "body" not in result:
            return 0.5  # Default score
            
        score = 0.5  # Start with neutral score
        
        # Check if category keywords appear in the content
        category_keywords = {
            "economic_development": ["business", "economy", "job", "employment", "growth", "industry"],
            "housing_market": ["housing", "home", "apartment", "rent", "mortgage", "residential"],
            "infrastructure": ["road", "transit", "utility", "infrastructure", "transportation", "development"],
            "government_policy": ["zoning", "regulation", "permit", "tax", "incentive", "government"],
            "community_factors": ["school", "education", "crime", "recreation", "healthcare", "park"]
        }
        
        # Check title and content for keywords
        keywords = category_keywords.get(category, [])
        content = (result.get("title", "") + " " + result.get("body", "")).lower()
        
        # Count matching keywords
        matches = sum(1 for keyword in keywords if keyword in content)
        
        # Adjust score based on matches (0.1 per match, max +0.4)
        score += min(0.4, matches * 0.1)
        
        # Check recency indicators
        recency_indicators = ["2024", "2023", "recent", "new", "latest", "update", "month", "week"]
        recency_matches = sum(1 for indicator in recency_indicators if indicator in content)
        
        # Adjust score for recency (0.05 per match, max +0.2)
        score += min(0.2, recency_matches * 0.05)
        
        # Cap at 0.95 (never perfect)
        return min(0.95, score)
    
    def _generate_insights(self, results, category):
        """Generate insights from a set of search results."""
        if not results:
            return []
            
        # Count common themes and keywords
        insights = []
        
        # Simple insight generation - in production, this would use more advanced NLP
        if category == "economic_development":
            # Check for growth indicators
            growth_terms = ["expansion", "growth", "new jobs", "hiring", "investment"]
            if any(any(term in r.get("summary", "").lower() for term in growth_terms) for r in results):
                insights.append("Evidence of economic growth in the area")
                
            # Check for decline indicators
            decline_terms = ["layoff", "closing", "downturn", "recession", "struggling"]
            if any(any(term in r.get("summary", "").lower() for term in decline_terms) for r in results):
                insights.append("Potential economic challenges in the area")
                
        elif category == "housing_market":
            # Check for housing shortage
            shortage_terms = ["shortage", "crisis", "lack of housing", "insufficient", "limited supply"]
            if any(any(term in r.get("summary", "").lower() for term in shortage_terms) for r in results):
                insights.append("Indicators of housing shortage in the market")
                
            # Check for development activity
            development_terms = ["development", "construction", "new homes", "building", "project"]
            if any(any(term in r.get("summary", "").lower() for term in development_terms) for r in results):
                insights.append("Active housing development in the area")
                
        # Add at least one generic insight if none found
        if not insights:
            insights.append(f"Information found related to {category.replace('_', ' ')}")
            
        return insights
    
    def _update_meta_analysis(self, search_results):
        """Update the meta-analysis based on search results."""
        category = search_results.get("category")
        results = search_results.get("results", [])
        
        if not category or not results:
            return
            
        # Update the meta-analysis based on category
        if category == "economic_development":
            # Count potential projects mentioned
            project_count = sum(1 for r in results if any(term in r.get("summary", "").lower() 
                                                       for term in ["project", "development", "investment"]))
            
            # Extract any dollar amounts
            all_amounts = []
            for r in results:
                all_amounts.extend(r.get("entities", {}).get("amounts", []))
                
            self.search_results["meta_analysis"]["economic_climate"]["growth_indicators"] = {
                "detected_projects": project_count,
                "mentioned_investments": all_amounts[:3] if all_amounts else [],
                "confidence": "medium"
            }
            
        elif category == "housing_market":
            # Extract housing market trends
            trends = []
            for r in results:
                if "affordable" in r.get("summary", "").lower():
                    trends.append("Focus on affordable housing solutions")
                if "shortage" in r.get("summary", "").lower():
                    trends.append("Housing shortage indicated")
                if "growth" in r.get("summary", "").lower():
                    trends.append("Housing market growth mentioned")
                    
            # Add unique trends to the meta analysis
            current_trends = self.search_results["meta_analysis"]["housing_market"]["detected_trends"]
            unique_trends = [t for t in trends if t not in current_trends]
            self.search_results["meta_analysis"]["housing_market"]["detected_trends"].extend(unique_trends)
    
    def get_structured_results(self):
        """Get the structured search results."""
        return self.search_results
    
    def get_results_by_category(self, category):
        """Get results for a specific category."""
        return [r for r in self.search_results.get("search_results", []) if r.get("category") == category]
    
    def get_meta_analysis(self):
        """Get the meta-analysis of all search results."""
        return self.search_results.get("meta_analysis", {})
    
    def __call__(self, query, max_results=5):
        """Make the tool callable directly."""
        # Check if query looks like a property data dictionary
        if isinstance(query, dict) and "City" in query:
            return self.execute_search_strategy(query, max_results_per_query=max_results)
        
        # Otherwise treat as a regular search query
        return self.search(query, max_results=max_results)


# For backward compatibility
class WebResearchTool(EnhancedWebResearchTool):
    """Legacy class for backward compatibility."""
    pass


# Testing function
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


if __name__ == "__main__":
    # Run a test if executed directly
    test_web_search() 