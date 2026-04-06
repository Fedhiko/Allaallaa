#!/usr/bin/env python3
"""
Setup script for TOKUMA 3-in-1 Research Platform Enhanced Version
Installs all required dependencies and sets up the environment
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Installing: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {e}")
        if e.stderr:
            print("Error output:", e.stderr)
        return False


def main():
    """Main setup function"""
    print("🧬 TOKUMA 3-in-1 Research Platform - Enhanced Setup")
    print("=" * 60)
    print("This script will install all required dependencies for the enhanced platform.")
    print("The enhanced version includes:")
    print("• Geospatial Integration (GIS) with Folium maps")
    print("• Machine Learning Surrogate Models with SHAP/LIME")
    print("• Advanced Furrow Irrigation Physics")
    print("• Climate Change Projection Downscaling")
    print("• Economic Optimization Module")
    print("• Automated Thesis/Report Generator")
    print("• Real-time API Connectors")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ ERROR: Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"✅ Working directory: {project_dir}")
    
    # Install requirements
    requirements_file = project_dir / "requirements.txt"
    if requirements_file.exists():
        success = run_command(
            f"{sys.executable} -m pip install -r requirements.txt",
            "Core dependencies from requirements.txt"
        )
        if not success:
            print("❌ Failed to install core dependencies")
            return False
    else:
        print("❌ requirements.txt not found")
        return False
    
    # Additional installations for enhanced features
    additional_packages = [
        ("folium", "Interactive maps"),
        ("streamlit-folium", "Streamlit-Folium integration"),
        ("geopandas", "Geospatial data analysis"),
        ("shapely", "Geometric operations"),
        ("fiona", "GIS file I/O"),
        ("scikit-learn", "Machine learning"),
        ("shap", "SHAP explanations"),
        ("lime", "LIME explanations"),
        ("tensorflow", "Deep learning"),
        ("netcdf4", "NetCDF climate data"),
        ("xarray", "Climate data analysis"),
        ("reportlab", "PDF generation"),
        ("fpdf2", "Alternative PDF"),
        ("pylatex", "LaTeX documents"),
        ("python-bibtex", "BibTeX support"),
        ("pydantic", "Data validation"),
        ("pyproj", "Map projections"),
        ("rasterio", "Raster data I/O"),
    ]
    
    for package, description in additional_packages:
        run_command(
            f"{sys.executable} -m pip install {package}",
            description
        )
    
    # Create necessary directories
    directories = [
        "model_templates",
        "exports",
        "uploads",
        "cache",
        "logs"
    ]
    
    print(f"\n{'='*60}")
    print("Creating necessary directories...")
    print('='*60)
    
    for directory in directories:
        dir_path = project_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Test imports
    print(f"\n{'='*60}")
    print("Testing imports...")
    print('='*60)
    
    test_modules = [
        ("streamlit", "Streamlit"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("plotly", "Plotly"),
        ("pymoo", "PyMOO"),
        ("SALib", "SALib"),
        ("folium", "Folium"),
        ("geopandas", "GeoPandas"),
        ("sklearn", "Scikit-learn"),
        ("tensorflow", "TensorFlow"),
        ("requests", "Requests"),
    ]
    
    failed_imports = []
    
    for module, name in test_modules:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError as e:
            print(f"❌ {name}: {e}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\n⚠️  WARNING: {len(failed_imports)} modules failed to import")
        print("Some features may not work correctly.")
    else:
        print("\n✅ All modules imported successfully!")
    
    # Final instructions
    print(f"\n{'='*60}")
    print("🎉 SETUP COMPLETE!")
    print('='*60)
    print("To run the enhanced TOKUMA platform:")
    print(f"1. cd {project_dir}")
    print("2. streamlit run app.py")
    print("\nEnhanced Features Available:")
    print("• 🗺️ GIS Integration - Interactive maps with shapefile support")
    print("• 🤖 ML Surrogates - Train and analyze ML models")
    print("• ⚙️ Irrigation Physics - Advanced hydraulic analysis")
    print("• 🌡️ Climate Downscaling - CMIP6 integration")
    print("• 💰 Economic Analysis - Cost-benefit optimization")
    print("• 📄 Report Generator - Automated LaTeX/PDF reports")
    print("• 📡 API Connectors - Real-time WaPOR and weather data")
    print("\nFor API access, you'll need:")
    print("• FAO WaPOR API key (optional)")
    print("• OpenWeatherMap API key (free tier available)")
    print("="*60)


if __name__ == "__main__":
    main()
