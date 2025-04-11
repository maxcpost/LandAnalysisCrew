#!/usr/bin/env python3
"""
Unit tests for the PropertyDataLoader class.
"""

import os
import sys
import unittest
import tempfile
import pandas as pd
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import the module to be tested
from src.data.loader import PropertyDataLoader


class TestPropertyDataLoader(unittest.TestCase):
    """Test suite for PropertyDataLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary CSV file with test data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.temp_dir.name, "test_data.csv")
        
        # Create test data
        self.test_data = pd.DataFrame({
            'StockNumber': ['12345', '67890', '24680'],
            'Property Address': ['123 Test St', '456 Sample Ave', '789 Demo Rd'],
            'City': ['Austin', 'Dallas', 'Houston'],
            'State': ['TX', 'TX', 'TX'],
            'Zip': ['78701', '75201', '77002'],
            'Land Area (AC)': [1.5, 2.3, 3.0],
            'For Sale Price': ['$500,000', '$750,000', '$1,000,000'],
            'Zoning': ['R1', 'R2', 'C1']
        })
        
        # Save test data to CSV
        self.test_data.to_csv(self.csv_path, index=False)
        
        # Create the loader with the test data
        self.loader = PropertyDataLoader(self.csv_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_get_property_list(self):
        """Test getting the list of all properties."""
        properties = self.loader.get_property_list()
        
        # Check that we got the expected number of properties
        self.assertEqual(len(properties), 3)
        
        # Check that the properties have the expected values
        self.assertEqual(properties[0]['StockNumber'], '12345')
        self.assertEqual(properties[1]['City'], 'Dallas')
        self.assertEqual(properties[2]['Property Address'], '789 Demo Rd')
    
    def test_get_property_data(self):
        """Test getting data for a specific property."""
        # Get data for a property that exists
        property_data = self.loader.get_property_data('12345')
        
        # Check that we got the expected property
        self.assertIsNotNone(property_data)
        self.assertEqual(property_data['StockNumber'], '12345')
        self.assertEqual(property_data['City'], 'Austin')
        self.assertEqual(property_data['Land Area (AC)'], 1.5)
        
        # Try getting a property that doesn't exist
        property_data = self.loader.get_property_data('99999')
        self.assertIsNone(property_data)
    
    def test_search_properties(self):
        """Test searching for properties."""
        # Search by city
        results = self.loader.search_properties('austin')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['StockNumber'], '12345')
        
        # Search by partial address
        results = self.loader.search_properties('sample')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['StockNumber'], '67890')
        
        # Search with no matches
        results = self.loader.search_properties('nonexistent')
        self.assertEqual(len(results), 0)
    
    def test_filter_properties(self):
        """Test filtering properties by criteria."""
        # Filter by state
        results = self.loader.filter_properties(state='TX')
        self.assertEqual(len(results), 3)
        
        # Filter by city
        results = self.loader.filter_properties(city='Dallas')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['StockNumber'], '67890')
        
        # Filter by multiple cities
        results = self.loader.filter_properties(city=['Austin', 'Houston'])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['StockNumber'], '12345')
        self.assertEqual(results[1]['StockNumber'], '24680')


if __name__ == '__main__':
    unittest.main() 