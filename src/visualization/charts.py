#!/usr/bin/env python3
"""
Chart generation module for property analysis visualizations.
Creates various charts and graphs for property reports.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path


def setup_chart_style():
    """Set up the styling for matplotlib charts."""
    # Use a clean, modern style
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Set custom colors
    colors = ['#2C3E50', '#E74C3C', '#3498DB', '#2ECC71', '#F39C12', 
              '#9B59B6', '#1ABC9C', '#34495E', '#D35400', '#7F8C8D']
    
    sns.set_palette(colors)
    
    # Increase font sizes for readability
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12


def save_chart(plt, filename, format='png', dpi=300, output_dir=None):
    """
    Save the chart to a file.
    
    Args:
        plt: Matplotlib pyplot instance
        filename: Name of the file (without extension)
        format: File format (default: png)
        dpi: Resolution (default: 300)
        output_dir: Directory to save the chart (default: ./outputs/charts)
    
    Returns:
        str: Path to the saved file
    """
    if output_dir is None:
        # Default to outputs/charts directory relative to project root
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "outputs" / "charts"
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create full path
    filepath = os.path.join(output_dir, f"{filename}.{format}")
    
    # Save the figure
    plt.savefig(filepath, format=format, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    return filepath


def create_population_growth_chart(data, city_name, output_dir=None):
    """
    Create a chart showing population growth over time.
    
    Args:
        data: Dictionary or DataFrame with years as keys/index and population as values
        city_name: Name of the city
        output_dir: Directory to save the chart (default: None)
    
    Returns:
        str: Path to the saved chart
    """
    setup_chart_style()
    
    # Convert to DataFrame if it's a dictionary
    if isinstance(data, dict):
        df = pd.DataFrame(list(data.items()), columns=['Year', 'Population'])
    else:
        df = data.copy()
    
    # Sort by year
    df = df.sort_values('Year')
    
    # Create the chart
    plt.figure(figsize=(10, 6))
    
    # Plot the data
    plt.plot(df['Year'], df['Population'], marker='o', linewidth=3, markersize=8)
    
    # Add trend line (linear regression)
    z = np.polyfit(range(len(df['Year'])), df['Population'], 1)
    p = np.poly1d(z)
    plt.plot(df['Year'], p(range(len(df['Year']))), "r--", linewidth=2, alpha=0.7)
    
    # Calculate the growth rate
    if len(df) > 1:
        first_year = df['Year'].iloc[0]
        last_year = df['Year'].iloc[-1]
        first_pop = df['Population'].iloc[0]
        last_pop = df['Population'].iloc[-1]
        years_diff = last_year - first_year
        growth_rate = ((last_pop / first_pop) ** (1 / years_diff) - 1) * 100
        
        # Add the growth rate annotation
        plt.annotate(f"CAGR: {growth_rate:.2f}%", 
                     xy=(0.7, 0.05), 
                     xycoords='axes fraction', 
                     fontsize=12,
                     bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
    
    # Add labels and title
    plt.title(f"Population Growth: {city_name}", fontweight='bold')
    plt.xlabel("Year")
    plt.ylabel("Population")
    plt.grid(True, alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save and return the path
    return save_chart(plt, f"population_growth_{city_name.lower().replace(' ', '_')}", 
                     output_dir=output_dir)


def create_income_distribution_chart(income_data, city_name, comparison_data=None, output_dir=None):
    """
    Create a chart showing income distribution.
    
    Args:
        income_data: Dictionary with income brackets as keys and percentages as values
        city_name: Name of the city
        comparison_data: Optional national/state data for comparison
        output_dir: Directory to save the chart
    
    Returns:
        str: Path to the saved chart
    """
    setup_chart_style()
    
    # Create the chart
    plt.figure(figsize=(12, 7))
    
    # Sort income brackets (assuming they're in the format "$X - $Y")
    sorted_brackets = sorted(income_data.keys(), 
                             key=lambda x: int(x.split('-')[0].replace('$', '').replace(',', '').strip()))
    
    x = np.arange(len(sorted_brackets))
    width = 0.35
    
    # Plot city data
    plt.bar(x - width/2 if comparison_data else x, 
            [income_data[bracket] for bracket in sorted_brackets], 
            width, 
            label=city_name)
    
    # Plot comparison data if provided
    if comparison_data:
        plt.bar(x + width/2, 
                [comparison_data.get(bracket, 0) for bracket in sorted_brackets], 
                width, 
                label='National Average')
    
    # Add labels and title
    plt.title(f"Income Distribution: {city_name}", fontweight='bold')
    plt.xlabel("Income Bracket")
    plt.ylabel("Percentage of Households")
    plt.xticks(x, sorted_brackets, rotation=45, ha='right')
    plt.grid(True, alpha=0.3, axis='y')
    
    if comparison_data:
        plt.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Save and return the path
    return save_chart(plt, f"income_distribution_{city_name.lower().replace(' ', '_')}", 
                     output_dir=output_dir)


def create_housing_value_chart(data, city_name, output_dir=None):
    """
    Create a chart showing housing value trends over time.
    
    Args:
        data: Dictionary or DataFrame with years as keys/index and median home values as values
        city_name: Name of the city
        output_dir: Directory to save the chart
    
    Returns:
        str: Path to the saved chart
    """
    setup_chart_style()
    
    # Convert to DataFrame if it's a dictionary
    if isinstance(data, dict):
        df = pd.DataFrame(list(data.items()), columns=['Year', 'Median Home Value'])
    else:
        df = data.copy()
    
    # Sort by year
    df = df.sort_values('Year')
    
    # Create the chart
    plt.figure(figsize=(10, 6))
    
    # Plot the data
    plt.plot(df['Year'], df['Median Home Value'], marker='o', linewidth=3, markersize=8)
    
    # Calculate the appreciation rate
    if len(df) > 1:
        first_year = df['Year'].iloc[0]
        last_year = df['Year'].iloc[-1]
        first_value = df['Median Home Value'].iloc[0]
        last_value = df['Median Home Value'].iloc[-1]
        years_diff = last_year - first_year
        appreciation_rate = ((last_value / first_value) ** (1 / years_diff) - 1) * 100
        
        # Add the appreciation rate annotation
        plt.annotate(f"Annual Appreciation: {appreciation_rate:.2f}%", 
                     xy=(0.05, 0.95), 
                     xycoords='axes fraction', 
                     fontsize=12,
                     bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))
    
    # Add dollar signs to y-axis
    plt.gca().yaxis.set_major_formatter('${x:,.0f}')
    
    # Add labels and title
    plt.title(f"Median Home Value Trends: {city_name}", fontweight='bold')
    plt.xlabel("Year")
    plt.ylabel("Median Home Value")
    plt.grid(True, alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save and return the path
    return save_chart(plt, f"housing_value_{city_name.lower().replace(' ', '_')}", 
                     output_dir=output_dir)


def create_age_demographic_chart(data, city_name, comparison_data=None, output_dir=None):
    """
    Create a chart showing age demographics.
    
    Args:
        data: Dictionary with age brackets as keys and percentages as values
        city_name: Name of the city
        comparison_data: Optional national/state data for comparison
        output_dir: Directory to save the chart
    
    Returns:
        str: Path to the saved chart
    """
    setup_chart_style()
    
    # Create the chart
    plt.figure(figsize=(12, 7))
    
    # Define standard age brackets if not consistent
    standard_brackets = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
    
    # Use provided brackets or standardized ones
    if all(bracket in data for bracket in standard_brackets):
        sorted_brackets = standard_brackets
    else:
        sorted_brackets = sorted(data.keys(), 
                                key=lambda x: int(x.split('-')[0].replace('+', '').strip()))
    
    x = np.arange(len(sorted_brackets))
    width = 0.35
    
    # Plot city data
    plt.bar(x - width/2 if comparison_data else x, 
            [data.get(bracket, 0) for bracket in sorted_brackets], 
            width, 
            label=city_name)
    
    # Plot comparison data if provided
    if comparison_data:
        plt.bar(x + width/2, 
                [comparison_data.get(bracket, 0) for bracket in sorted_brackets], 
                width, 
                label='National Average')
    
    # Add labels and title
    plt.title(f"Age Distribution: {city_name}", fontweight='bold')
    plt.xlabel("Age Group")
    plt.ylabel("Percentage of Population")
    plt.xticks(x, sorted_brackets)
    plt.grid(True, alpha=0.3, axis='y')
    
    if comparison_data:
        plt.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Save and return the path
    return save_chart(plt, f"age_distribution_{city_name.lower().replace(' ', '_')}", 
                     output_dir=output_dir)


def create_market_radar_chart(metrics, property_name, output_dir=None):
    """
    Create a radar chart comparing various market metrics.
    
    Args:
        metrics: Dictionary with metric names as keys and scores (0-10) as values
        property_name: Name of the property
        output_dir: Directory to save the chart
    
    Returns:
        str: Path to the saved chart
    """
    # Convert metrics to lists for plotly
    categories = list(metrics.keys())
    values = list(metrics.values())
    
    # Add the first value at the end to close the polygon
    values.append(values[0])
    categories.append(categories[0])
    
    # Create the radar chart using plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=property_name,
        line_color='#3498DB',
        fillcolor='rgba(52, 152, 219, 0.5)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        title=f"Market Analysis: {property_name}",
        title_font_size=16,
        showlegend=True
    )
    
    # Create output directory if needed
    if output_dir is None:
        # Default to outputs/charts directory relative to project root
        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "outputs" / "charts"
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create full path
    filepath = os.path.join(output_dir, f"market_radar_{property_name.lower().replace(' ', '_')}.png")
    
    # Save the figure
    fig.write_image(filepath, width=900, height=700)
    
    return filepath


def create_property_comparison_chart(properties_data, metrics, output_dir=None):
    """
    Create a grouped bar chart comparing multiple properties across metrics.
    
    Args:
        properties_data: List of dictionaries, each with 'name' and scores for each metric
        metrics: List of metric names to include
        output_dir: Directory to save the chart
    
    Returns:
        str: Path to the saved chart
    """
    setup_chart_style()
    
    # Number of properties and metrics
    n_properties = len(properties_data)
    n_metrics = len(metrics)
    
    # Create a figure with appropriate size
    plt.figure(figsize=(12, 8))
    
    # Set up the x-axis
    x = np.arange(n_metrics)
    width = 0.8 / n_properties  # Adjust bar width based on number of properties
    
    # Plot each property
    for i, prop in enumerate(properties_data):
        property_name = prop['name']
        scores = [prop.get(metric, 0) for metric in metrics]
        
        offset = (i - n_properties / 2 + 0.5) * width
        plt.bar(x + offset, scores, width, label=property_name)
    
    # Add labels and title
    plt.title("Property Comparison", fontweight='bold')
    plt.xlabel("Metrics")
    plt.ylabel("Score (0-10)")
    plt.xticks(x, metrics, rotation=45, ha='right')
    plt.yticks(np.arange(0, 11, 1))
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=n_properties)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save and return the path
    return save_chart(plt, "property_comparison", output_dir=output_dir) 