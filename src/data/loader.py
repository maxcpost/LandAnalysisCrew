#!/usr/bin/env python3
"""
Property data loader for the Land Analysis Crew.
Provides utilities for loading and querying property data from CSV files.
"""

import os
import pandas as pd
from pathlib import Path
from ..utils.formatting import print_error, print_info

class PropertyDataLoader:
    """
    Loads and provides access to property data from CSV files.
    """
    
    def __init__(self, data_file=None):
        """
        Initialize the property data loader.
        
        Args:
            data_file: Path to the CSV file containing property data.
                       If None, will look for 'master.csv' in the default data directory.
        """
        if data_file is None:
            # Look for data file in default location
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            data_file = data_dir / "master.csv"
            
        self.data_file = data_file
        self.properties = None
        self._load_data()
        
    def _load_data(self):
        """Load property data from the CSV file."""
        try:
            if not os.path.exists(self.data_file):
                print_error(f"Data file not found: {self.data_file}")
                raise FileNotFoundError(f"Data file not found: {self.data_file}")
                
            # Load the CSV data
            self.properties = pd.read_csv(self.data_file)
            
            # Basic cleaning and normalization
            self._clean_data()
            
            print_info(f"Loaded {len(self.properties)} properties from {self.data_file}")
        except Exception as e:
            print_error(f"Error loading property data: {e}")
            raise
            
    def _clean_data(self):
        """Clean and normalize the property data."""
        if self.properties is None:
            return
            
        # Convert column names to more consistent format
        self.properties.columns = [col.strip() for col in self.properties.columns]
        
        # Ensure stock number is a string and strip any whitespace
        if 'StockNumber' in self.properties.columns:
            self.properties['StockNumber'] = self.properties['StockNumber'].astype(str).str.strip()
        
        # Fill NaN values in critical columns
        critical_columns = ['Property Address', 'City', 'State', 'Zip']
        for col in critical_columns:
            if col in self.properties.columns:
                self.properties[col] = self.properties[col].fillna('Unknown')
    
    def get_property_list(self):
        """
        Get a list of all properties.
        
        Returns:
            A list of dictionaries containing property information.
        """
        if self.properties is None:
            return []
            
        return self.properties.to_dict('records')
    
    def get_property_data(self, stock_number):
        """
        Get data for a specific property by stock number.
        
        Args:
            stock_number: The stock number of the property to retrieve.
            
        Returns:
            A dictionary containing the property data, or None if not found.
        """
        if self.properties is None:
            return None
            
        # Convert stock number to string for matching
        stock_number = str(stock_number).strip()
        
        # Find the property by stock number
        property_data = self.properties[self.properties['StockNumber'] == stock_number]
        
        if property_data.empty:
            return None
            
        return property_data.iloc[0].to_dict()
    
    def search_properties(self, query):
        """
        Search for properties matching the given query.
        
        Args:
            query: The search query (matched against address, city, state, etc.)
            
        Returns:
            A list of dictionaries containing matching properties.
        """
        if self.properties is None:
            return []
            
        # Convert query to lowercase for case-insensitive matching
        query = str(query).lower()
        
        # Search in relevant columns
        search_columns = ['Property Address', 'City', 'State', 'Zip', 'County']
        
        # Filter to only include columns that exist in the DataFrame
        search_columns = [col for col in search_columns if col in self.properties.columns]
        
        if not search_columns:
            return []
            
        # Create a mask for each column and combine with OR
        mask = False
        for col in search_columns:
            mask = mask | self.properties[col].astype(str).str.lower().str.contains(query, na=False)
            
        # Return matching properties
        return self.properties[mask].to_dict('records')
        
    def filter_properties(self, **filters):
        """
        Filter properties based on criteria.
        
        Args:
            **filters: Keyword arguments for filtering properties.
                       Example: min_acres=10, max_price=1000000, state='TX'
                       
        Returns:
            A list of dictionaries containing properties matching the filters.
        """
        if self.properties is None:
            return []
            
        # Start with all properties
        filtered = self.properties.copy()
        
        # Apply numeric filters
        if 'min_acres' in filters and 'Land Area (AC)' in filtered.columns:
            filtered = filtered[pd.to_numeric(filtered['Land Area (AC)'], errors='coerce') >= filters['min_acres']]
            
        if 'max_acres' in filters and 'Land Area (AC)' in filtered.columns:
            filtered = filtered[pd.to_numeric(filtered['Land Area (AC)'], errors='coerce') <= filters['max_acres']]
            
        if 'min_price' in filters and 'For Sale Price' in filtered.columns:
            # Remove $ and commas from price and convert to numeric
            prices = filtered['For Sale Price'].astype(str).str.replace('$', '').str.replace(',', '')
            filtered = filtered[pd.to_numeric(prices, errors='coerce') >= filters['min_price']]
            
        if 'max_price' in filters and 'For Sale Price' in filtered.columns:
            # Remove $ and commas from price and convert to numeric
            prices = filtered['For Sale Price'].astype(str).str.replace('$', '').str.replace(',', '')
            filtered = filtered[pd.to_numeric(prices, errors='coerce') <= filters['max_price']]
            
        # Apply categorical filters
        for col, value in filters.items():
            if col in ['state', 'State'] and 'State' in filtered.columns:
                filtered = filtered[filtered['State'] == value]
                
            if col in ['city', 'City'] and 'City' in filtered.columns:
                if isinstance(value, list):
                    filtered = filtered[filtered['City'].isin(value)]
                else:
                    filtered = filtered[filtered['City'] == value]
                    
            if col in ['county', 'County'] and 'County' in filtered.columns:
                if isinstance(value, list):
                    filtered = filtered[filtered['County'].isin(value)]
                else:
                    filtered = filtered[filtered['County'] == value]
        
        return filtered.to_dict('records')


if __name__ == "__main__":
    # Simple test if run directly
    try:
        loader = PropertyDataLoader()
        properties = loader.get_property_list()
        print(f"Loaded {len(properties)} properties")
        
        if properties:
            # Show first property as example
            first_property = properties[0]
            stock_number = first_property['StockNumber']
            print(f"\nExample property (Stock #{stock_number}):")
            
            # Get full property data
            full_data = loader.get_property_data(stock_number)
            for key in ['Property Address', 'City', 'State', 'Land Area (AC)', 'For Sale Price']:
                if key in full_data:
                    print(f"  {key}: {full_data[key]}")
        
    except Exception as e:
        print(f"Error testing PropertyDataLoader: {e}") 