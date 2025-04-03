# Land Analysis Crew Documentation

This directory contains documentation for the Land Analysis Crew project.

## Available Documentation

- [Data Dictionary](data_dictionary.md) - Comprehensive descriptions of all data columns in the `master.csv` file
- [Mac Setup Guide](mac_setup_guide.md) - Detailed instructions for setting up and running the application on macOS

## Automatic Setup with startup.sh

We've simplified the setup process to a single file solution. Mac users can now use the automated `startup.sh` script that:

1. Installs all required dependencies automatically
2. Sets up the complete environment with clear feedback
3. Runs the application when setup is complete

The script provides step-by-step feedback during the whole process and handles both first-time setup and subsequent runs in a single command.

The [Mac Setup Guide](mac_setup_guide.md) provides detailed information on:
- How the script works internally
- Troubleshooting common issues
- Alternative setup options if needed
- Using Claude AI instead of Llama 3

## Understanding Data Columns

The data dictionary provides detailed explanations for each column in the `master.csv` file. The columns are organized into categories:

1. **Basic Property Information** - Property identifiers, location, and physical characteristics
2. **Ownership and Sales Information** - Current owner details and transaction history
3. **Flood Risk Information** - FEMA flood zone classifications and risk metrics
4. **Population Growth Metrics** - Recent and projected growth within specified radii
5. **Population Data by Distance** - Historical, current, and projected population counts
6. **Income Data by Distance** - Median and average household income metrics
7. **Home Value Data by Distance** - Current and projected median home values
8. **Housing Unit Growth** - Growth rates for housing stock in the area
9. **Home Value Distribution Data** - Breakdown of homes by price brackets
10. **Detailed Demographic Data** - Household types, occupancy rates, and housing characteristics
11. **Nearby Amenities and Services** - Distance and travel time to key amenities
12. **Composite Scoring Metrics** - Overall property evaluation scores
13. **Percentile Rankings** - How properties compare to others in the dataset

## Using the Documentation

Refer to these documents when:
- Analyzing properties in the system
- Understanding the metrics used for scoring
- Adding new properties to the dataset
- Interpreting output from the AI agents 