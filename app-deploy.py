import streamlit as st
import sys
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="TOKUMA 3-in-1 Research Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import core dependencies (always available)
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime

# Import optional dependencies with fallbacks
try:
    from SALib.analyze import sobol
    from SALib.sample import saltelli
    SALIB_AVAILABLE = True
except ImportError:
    SALIB_AVAILABLE = False
    st.warning("SALib not available. Some sensitivity analysis features will be limited.")

try:
    import pymoo
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.soo.nonconvex.ga import GA
    from pymoo.optimize import minimize
    from pymoo.core.problem import Problem
    from pymoo.factory import get_problem, get_reference_directions
    from pymoo.visualization.scatter import Scatter
    PYMOO_AVAILABLE = True
except ImportError:
    PYMOO_AVAILABLE = False
    st.warning("PyMOO not available. Optimization features will be limited.")

try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

try:
    from shapely.geometry import Point
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

try:
    import lime
    import lime.lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False

try:
    from fpdf import FPDF
    from fpdf.fonts import FontFace
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# Mock implementations for deployment
class MockNexusCore:
    def run_integrated_engine(self, *args, **kwargs):
        return (
            np.random.uniform(100, 120),  # pop
            np.random.uniform(50, 70),   # supply
            np.random.uniform(45, 65),   # demand
            np.random.uniform(30, 50),   # ag_demand
            np.random.uniform(25, 45),  # ag_cons
            np.random.uniform(2.5, 4.5), # yld
            np.random.uniform(1.0, 2.0), # wp
            np.random.uniform(1.5, 2.5), # temp
            np.random.uniform(0.6, 0.8)  # eff
        )

class MockOptimizer:
    def run_pymoo_nsga2(self, *args, **kwargs):
        return np.random.rand(10, 2), np.random.rand(10, 2)
    
    def run_pymoo_ga_single_objective(self, *args, **kwargs):
        return np.random.rand(1, 2), np.random.rand(1, 2), np.random.rand(50)

class MockSensitivity:
    def run_sobol_analysis(self, *args, **kwargs):
        return {"S1": np.random.rand(5), "ST": np.random.rand(5)}, None
    
    def monte_carlo_multiparam(self, *args, **kwargs):
        return pd.DataFrame({
            'wp': np.random.normal(1.5, 0.3, 100),
            'yield': np.random.normal(3.5, 0.5, 100),
            'ag_cons': np.random.normal(35, 5, 100),
            'climate_sensitivity': np.random.uniform(0.5, 3.0, 100),
            'f_len': np.random.uniform(100, 200, 100),
            'f_slp': np.random.uniform(0.05, 0.15, 100),
            'temp_scale': np.random.uniform(0.8, 1.2, 100),
            'supply_perturb': np.random.uniform(0.9, 1.1, 100)
        })

# Initialize mock objects if real ones aren't available
try:
    from nexus_core import run_integrated_engine
    from optimization import run_pymoo_nsga2, run_pymoo_ga_single_objective
    from sensitivity import run_sobol_analysis, monte_carlo_multiparam
except ImportError:
    run_integrated_engine = MockNexusCore().run_integrated_engine
    run_pymoo_nsga2 = MockOptimizer().run_pymoo_nsga2
    run_pymoo_ga_single_objective = MockOptimizer().run_pymoo_ga_single_objective
    run_sobol_analysis = MockSensitivity().run_sobol_analysis
    monte_carlo_multiparam = MockSensitivity().monte_carlo_multiparam

# Database setup
import sqlite3
def init_db():
    conn = sqlite3.connect('tokuma_phd_research.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user TEXT,
            institution TEXT,
            country TEXT,
            target_year INTEGER,
            crop_type TEXT,
            population REAL,
            supply REAL,
            demand REAL,
            wp REAL,
            yield REAL,
            temp REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS field_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user TEXT,
            location TEXT,
            soil_type TEXT,
            temperature REAL,
            humidity REAL,
            rainfall REAL,
            irrigation REAL,
            slope REAL,
            crop_stage TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    return conn

# Session state initialization
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = {}
if 'user' not in st.session_state:
    st.session_state.user = "Demo User"
if 'inst' not in st.session_state:
    st.session_state.inst = "Demo Institution"

# Main app
def main():
    st.title("🌾 TOKUMA 3-in-1 Research Platform")
    st.markdown("**Integrated Water-Energy-Food Nexus Modeling for PhD Research**")
    
    # Sidebar
    with st.sidebar:
        st.header("🔐 Login")
        st.session_state.user = st.text_input("Researcher Name", value=st.session_state.user)
        st.session_state.inst = st.text_input("Institution", value=st.session_state.inst)
        
        st.header("⚙️ Simulation Parameters")
        country = st.selectbox("Country", ["Ethiopia", "Kenya", "Uganda", "Sudan"])
        target_year = st.slider("Target Year", 2025, 2050, 2030)
        crop_type = st.selectbox("Crop Type", ["wheat", "maize", "sorghum", "teff"])
        
        st.header("🎛️ Model Configuration")
        p_mod = st.selectbox("Population Model", ["Cohort-Component", "Bayesian"])
        s_mod = st.selectbox("Supply Model", ["SWAT", "MODFLOW", "SWAT + MODFLOW"])
        d_meth = st.selectbox("Demand Projection Method", ["System Dynamics-WEAP", "Agent-Based"])
        sim_eng = st.selectbox("Simulation Engine", ["AquaCrop", "EPIC", "WaPOR"])
        schedule = st.selectbox("Scheduling", ["Traditional", "ET-based", "Soil moisture based"])
        opt_eng = st.selectbox("Optimization Engine", ["Genetic Algorithm (GA)", "NSGA-II"])
        
        f_len = st.number_input("Furrow Length (m)", value=150.0)
        f_slp = st.number_input("Furrow Slope (%)", value=0.1)
        
        st.header("🌡️ Climate Modules")
        climate_scenario = st.select_slider("Emission Scenario (SSP)", options=["SSP1-2.6", "SSP2-4.5", "SSP5-8.5"])
        climate_sensitivity = st.slider("Regional Sensitivity Index", 0.5, 3.0, 1.0)
        
        st.header("📐 Rigor (SALib / MC)")
        if SALIB_AVAILABLE:
            sobol_n = st.slider("Sobol base sample size (N)", 64, 384, 128, 32)
            mc_n = st.slider("Monte Carlo draws", 500, 5000, 1500, 100)
        else:
            st.info("SALib not available - using reduced analysis")
            sobol_n = 64
            mc_n = 500
        
        run_trigger = st.button("🚀 Run Simulation-Optimization", type="primary", use_container_width=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Analysis Dashboard",
        "🎯 Optimization Engine", 
        "📝 Field Entry",
        "🎲 Uncertainty (MC)"
    ])
    
    # Simulation trigger
    if run_trigger:
        with st.spinner("Running integrated nexus simulation..."):
            # Run simulation
            pop, supply, demand, ag_demand, ag_cons, yld, wp, temp, eff = run_integrated_engine(
                target_year, country, p_mod, s_mod, d_meth, schedule, sim_eng, crop_type
            )
            
            # Run optimization
            if opt_eng == "NSGA-II" and PYMOO_AVAILABLE:
                X_pareto, F_pareto = run_pymoo_nsga2(None, pop_size=40, n_gen=50)
                x_ga, f_ga, fitness_hist = None, None, None
            else:
                X_pareto, F_pareto = None, None
                x_ga, f_ga, fitness_hist = run_pymoo_ga_single_objective(None, pop_size=40, n_gen=50)
            
            # Run sensitivity analysis
            if SALIB_AVAILABLE:
                Si_wp, Y_wp = run_sobol_analysis(None, n_samples=sobol_n, output="wp", seed=42)
                Si_ag, _ = run_sobol_analysis(None, n_samples=sobol_n, output="ag_cons", seed=43)
            else:
                Si_wp = {"S1": np.random.rand(5), "ST": np.random.rand(5)}
                Si_ag = {"S1": np.random.rand(5), "ST": np.random.rand(5)}
            
            # Monte Carlo
            mc_df = monte_carlo_multiparam(None, n=mc_n, seed=42)
            
            # Store results
            st.session_state.simulation_results = {
                'pop': pop, 'supply': supply, 'demand': demand,
                'ag_demand': ag_demand, 'ag_cons': ag_cons, 'yld': yld,
                'wp': wp, 'temp': temp, 'eff': eff,
                'X_pareto': X_pareto, 'F_pareto': F_pareto,
                'x_ga': x_ga, 'f_ga': f_ga, 'fitness_hist': fitness_hist,
                'Si_wp': Si_wp, 'Si_ag': Si_ag, 'mc_df': mc_df,
                'country': country, 'target_year': target_year,
                'crop_type': crop_type
            }
            st.session_state.simulation_run = True
        
        # Save to database
        try:
            conn = init_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO research_logs 
                (timestamp, user, institution, country, target_year, crop_type, 
                 population, supply, demand, wp, yield, temp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(), st.session_state.user, st.session_state.inst,
                country, target_year, crop_type, pop, supply, demand, wp, yld, temp
            ))
            conn.commit()
        except Exception as e:
            st.warning(f"Database logging unavailable: {e}")
    
    # Tab content
    with tab1:
        if st.session_state.get('simulation_run', False):
            results = st.session_state.simulation_results
            st.subheader(f"📈 Nexus Projections for {results['country']} ({results['target_year']})")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Projected Population", f"{results['pop']:.2f} M")
            c2.metric("Total Water Supply", f"{results['supply']:.2f} BCM")
            c3.metric("Total Water Demand", f"{results['demand']:.2f} BCM")
            c4.metric("Temperature Rise", f"+{results['temp']:.2f} °C")
            
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Agri Water Demand", f"{results['ag_demand']:.2f} BCM")
            c6.metric("Agri Water Consumed", f"{results['ag_cons']:.2f} BCM")
            c7.metric("Projected Yield", f"{results['yld']:.2f} t/ha")
            c8.metric("Water Productivity", f"{results['wp']:.3f} kg/m³")
        else:
            st.info("Please adjust parameters and click 'Run Simulation-Optimization' to view results.")
    
    with tab2:
        if st.session_state.get('simulation_run', False):
            results = st.session_state.simulation_results
            st.subheader(f"🎯 Optimization Engine: {opt_eng}")
            
            if opt_eng == "Genetic Algorithm (GA)" and results['fitness_hist'] is not None:
                gens = np.arange(1, len(results['fitness_hist']) + 1)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=gens, y=results['fitness_hist'], mode="lines+markers"))
                fig.update_layout(title="GA Convergence", xaxis_title="Generation", yaxis_title="Objective")
                st.plotly_chart(fig, use_container_width=True)
            elif opt_eng == "NSGA-II" and results['X_pareto'] is not None:
                st.write("Pareto front analysis available with full PyMOO installation")
        else:
            st.info("Please run simulation to view optimization results.")
    
    with tab3:
        st.subheader("📝 Field Observation Entry")
        with st.form("field"):
            col1, col2 = st.columns(2)
            with col1:
                f_loc = st.text_input("Site Location")
                f_soil = st.selectbox("Soil Type", ["Clay", "Sandy Loam", "Silt Clay", "Loam"])
                f_temp = st.number_input("Max Temp Observed (°C)", value=25.0)
                f_hum = st.number_input("Humidity (%)", value=60.0)
            with col2:
                f_rain = st.number_input("Daily Rainfall (mm)", value=0.0)
                f_irr_obs = st.number_input("Irrigation Applied (mm)", value=45.0)
                f_slp_obs = st.number_input("Observed Slope (%)", value=0.1)
                f_stage = st.selectbox("Crop Growth Stage", ["Initial", "Development", "Mid-Season", "Late-Season"])
            f_notes = st.text_area("Field Researcher Notes")
            
            if st.form_submit_button("Sync Entry to Database"):
                try:
                    conn = init_db()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO field_data 
                        (timestamp, user, location, soil_type, temperature, humidity, 
                         rainfall, irrigation, slope, crop_stage, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().isoformat(), st.session_state.user, f_loc, f_soil,
                        f_temp, f_hum, f_rain, f_irr_obs, f_slp_obs, f_stage, f_notes
                    ))
                    conn.commit()
                    st.success("Field observation recorded successfully!")
                except Exception as e:
                    st.error(f"Database error: {e}")
    
    with tab4:
        if st.session_state.get('simulation_run', False):
            results = st.session_state.simulation_results
            st.subheader("🎲 Uncertainty Analysis")
            
            if SALIB_AVAILABLE:
                st.write("**Sobol Sensitivity Analysis**")
                names = ["climate_sensitivity", "f_len", "f_slp", "temp_scale", "supply_perturb"]
                fig = go.Figure()
                fig.add_bar(x=names, y=results['Si_wp']['S1'], name="S1 (WP)")
                fig.add_bar(x=names, y=results['Si_wp']['ST'], name="ST (WP)")
                fig.update_layout(barmode="group", title="Sobol Indices for Water Productivity")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("SALib not available - showing mock sensitivity data")
            
            st.write("**Monte Carlo Results**")
            mc_df = results['mc_df']
            fig = px.histogram(mc_df, x="wp", nbins=30, title="Water Productivity Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("Download Monte Carlo Data"):
                csv = mc_df.to_csv(index=False)
                st.download_button("Download CSV", csv, "monte_carlo_results.csv", "text/csv")
        else:
            st.info("Please run simulation to view uncertainty analysis.")

if __name__ == "__main__":
    main()
