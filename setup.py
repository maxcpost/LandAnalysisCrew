#!/usr/bin/env python3
"""
Setup script for Land Analysis Crew project.
"""

from setuptools import setup, find_packages

setup(
    name="land_analysis_crew",
    version="1.0.0",
    description="AI-powered property analysis system for attainable housing development",
    author="ADLA Team",
    packages=find_packages(),
    install_requires=[
        "crewai>=0.28.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
        "litellm>=1.14.0",
        "duckduckgo-search>=2.9.5",
        "requests>=2.31.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "plotly>=5.13.0"
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 