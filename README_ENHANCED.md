# TOKUMA 3-in-1 Research Platform - Enhanced Version

An advanced decision support system for Water-Food-Climate Nexus analysis with comprehensive PhD-level research capabilities.

## 🚀 New Enhanced Features

### 1. 🗺️ Geospatial Integration (GIS)
- **Interactive Maps**: Folium-based mapping with OpenStreetMap, Stamen, and CartoDB layers
- **Shapefile Support**: Upload and visualize watershed boundaries (.shp, .shx, .dbf, .prj)
- **Site-Specific Analysis**: Click on map to auto-fill soil and climate parameters
- **Ethiopia Regions**: Pre-configured regions with soil and climate data
- **Coordinate Extraction**: Automatic parameter extraction based on location

### 2. 🤖 Machine Learning Surrogate Models
- **Pre-trained Models**: Load .h5, .pkl, .joblib model files
- **Model Training**: Train Random Forest, Gradient Boosting, Neural Networks, and PINNs
- **SHAP Visualizations**: Global and local feature importance explanations
- **LIME Analysis**: Local interpretability for individual predictions
- **Model Comparison**: Performance metrics and visualization tools
- **Synthetic Data Generation**: Training data generation for surrogate models

### 3. ⚙️ Advanced Furrow Irrigation Physics
- **Kostiakov Equation**: Cumulative infiltration modeling with parameters k and a
- **Modified Kostiakov**: Includes steady-state infiltration rate
- **Philip's Equation**: Alternative infiltration model with sorptivity
- **Green-Ampt Model**: Physics-based infiltration simulation
- **Hydraulic Analysis**: Manning's equation for furrow flow calculations
- **Advance/Recession Curves**: Time-based water movement visualization
- **Efficiency Metrics**: Distribution uniformity, application efficiency, storage efficiency

### 4. 🌡️ Climate Change Projection Downscaling
- **CMIP6 Integration**: Support for multiple GCMs and SSP scenarios
- **Statistical Downscaling**: Delta method and quantile mapping approaches
- **Weather Generator**: Markov chain-based synthetic weather generation
- **Ethiopia Climate Zones**: Region-specific climate parameters
- **Scenario Analysis**: SSP1-2.6, SSP2-4.5, SSP5-8.5 projections
- **Time Series Analysis**: Historical vs projected climate comparison

### 5. 💰 Economic Optimization Module
- **Cost-Benefit Analysis**: Comprehensive production cost calculation
- **Multi-objective Optimization**: NSGA-II for profit vs water use trade-offs
- **Crop Economics**: Wheat, Maize, Teff with market prices
- **Irrigation Economics**: System costs, energy requirements, maintenance
- **Profitability Metrics**: ROI, profit margins, economic water productivity
- **Sensitivity Analysis**: Parameter impact on economic outcomes

### 6. 📄 Automated Thesis/Report Generator
- **LaTeX Export**: Professional academic report generation
- **PDF Reports**: Direct PDF generation with figures and tables
- **BibTeX Integration**: Automatic bibliography management
- **Template System**: Thesis, research paper, technical report templates
- **Figure Export**: Plotly figures integration
- **Customizable Content**: Editable abstracts and sections

### 7. 📡 Real-time API Connectors
- **FAO WaPOR API**: Actual evapotranspiration and NPP data
- **OpenWeatherMap API**: Current weather and forecasts
- **Data Caching**: 5-minute cache for API responses
- **Integrated Dashboard**: Combined visualization of multiple data sources
- **Export Options**: CSV and JSON data export
- **Auto-refresh**: Optional automatic data updates

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional)

### Quick Setup
```bash
# Clone or download the project
cd tokuma-3-in-1-enhanced

# Run the setup script
python setup.py

# Start the application
streamlit run app.py
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install additional packages
pip install folium streamlit-folium geopandas shapely fiona
pip install scikit-learn shap lime tensorflow
pip install netcdf4 xarray reportlab fpdf2
pip install pylatex python-bibtex pydantic pyproj rasterio
```

## 📋 API Keys Setup

### FAO WaPOR (Optional)
1. Register at [WaPOR Portal](https://wapor.apps.fao.org/)
2. Get your API key
3. Enter in the "API Connectors" tab

### OpenWeatherMap (Required for weather data)
1. Register at [OpenWeatherMap](https://openweathermap.org/api)
2. Get free API key
3. Enter in the "API Connectors" tab

## 🎯 Usage Guide

### Basic Workflow
1. **Login**: Enter your name and institution
2. **Configure**: Set parameters in the sidebar
3. **Run Simulation**: Click "Run Simulation-Optimization"
4. **Analyze Results**: Explore different tabs for detailed analysis

### Enhanced Features Workflow

#### GIS Integration
1. Go to "🗺️ GIS Integration" tab
2. Select region or enter coordinates manually
3. Click on map to extract site parameters
4. Upload shapefiles for watershed analysis
5. View extracted soil and climate data

#### ML Surrogates
1. Go to "🤖 ML Surrogates" tab
2. Choose model type and target variable
3. Train new model or load pre-trained model
4. Analyze with SHAP and LIME visualizations
5. Download trained models

#### Irrigation Physics
1. Go to "⚙️ Irrigation Physics" tab
2. Configure furrow parameters and soil properties
3. View infiltration curves and hydraulic analysis
4. Analyze advance/recession curves
5. Review efficiency metrics

#### Climate Downscaling
1. Go to "🌡️ Climate Downscaling" tab
2. Select CMIP6 scenario and GCM model
3. Set target location and downscaling method
4. Generate synthetic weather data
5. Compare historical vs projected climate

#### Economic Analysis
1. Go to "💰 Economic Analysis" tab
2. Configure crop prices and input costs
3. Run economic optimization
4. Analyze Pareto fronts and profitability
5. Perform sensitivity analysis

#### Report Generation
1. Go to "📄 Report Generator" tab
2. Select report type and customize content
3. Generate PDF or LaTeX output
4. Download BibTeX references
5. Include figures and tables

#### API Connectors
1. Go to "📡 API Connectors" tab
2. Enter API keys
3. Select location and fetch data
4. View integrated dashboard
5. Export real-time data

## 📊 Original Features (Preserved)

All original features remain intact:
- **📊 Analysis Dashboard**: Core nexus projections and metrics
- **🎯 Optimization Engine**: NSGA-II and GA optimization
- **📝 Field Entry**: Detailed field observation database
- **🎲 Uncertainty Analysis**: Monte Carlo and SALib sensitivity
- **📂 Export**: Data export and archiving

## 🔧 Technical Architecture

### Module Structure
```
tokuma-3-in-1-enhanced/
├── app.py                    # Main Streamlit application
├── nexus_core.py            # Core simulation engine
├── model_templates/         # File-coupled simulation templates
├── gis_integration.py       # Geospatial analysis module
├── ml_surrogates.py        # Machine learning surrogates
├── irrigation_physics.py   # Advanced irrigation modeling
├── climate_downscaling.py  # Climate projection tools
├── economic_optimization.py # Economic analysis module
├── report_generator.py     # Automated report generation
├── api_connectors.py      # Real-time data connectors
├── requirements.txt       # Python dependencies
├── setup.py             # Installation script
└── README_ENHANCED.md   # This documentation
```

### Dependencies
- **Core**: streamlit, pandas, numpy, plotly, pymoo, SALib
- **GIS**: folium, geopandas, shapely, fiona, rasterio
- **ML**: scikit-learn, tensorflow, shap, lime
- **Climate**: netcdf4, xarray, pyproj
- **Reports**: reportlab, fpdf2, pylatex, python-bibtex
- **APIs**: requests, pydantic

## 🎓 Academic Features for PhD Research

### Dissertation Support
- **Automated Citations**: BibTeX integration with standard references
- **Figure Generation**: Publication-ready plots and visualizations
- **Methodology Documentation**: Detailed technical documentation
- **Results Export**: Multiple formats for thesis inclusion

### Research Validation
- **Uncertainty Quantification**: Comprehensive sensitivity analysis
- **Model Comparison**: Multiple modeling approaches
- **Scenario Analysis**: Climate and economic scenarios
- **Peer Review Ready**: Transparent methodology and reproducible results

## 🤝 Contributing

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd tokuma-3-in-1-enhanced

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Adding New Features
1. Follow the modular structure in separate Python files
2. Add new tabs to the main app.py
3. Update requirements.txt for new dependencies
4. Document new features in README

## 📄 License

This project builds upon the original TOKUMA 3-in-1 platform with enhanced features for PhD-level research.

## 🆘 Support

### Common Issues
1. **Import Errors**: Run `python setup.py` to install all dependencies
2. **API Issues**: Check API keys and internet connection
3. **Memory Issues**: Reduce sample sizes in optimization
4. **GIS Issues**: Ensure shapefiles include all required components

### Getting Help
- Check the error messages in Streamlit
- Verify all dependencies are installed
- Ensure API keys are valid
- Check internet connectivity for API features

## 🎉 Acknowledgments

Enhanced based on reviewer suggestions for PhD dissertation robustness:
- Geospatial integration for site-specific analysis
- Machine learning surrogate models for fast simulations
- Advanced irrigation physics for accurate modeling
- Climate downscaling for future projections
- Economic optimization for decision support
- Automated reporting for academic documentation
- Real-time data integration for current conditions

---

**Original TOKUMA 3-in-1 Platform** + **Enhanced PhD Research Features** = **Comprehensive Decision Support System**
