import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="TOKUMA Platform",
    page_icon="🌾",
    layout="wide"
)

if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = {}

def run_simulation():
    with st.spinner("Running simulation..."):
        pop = np.random.uniform(100, 120)
        supply = np.random.uniform(50, 70)
        demand = np.random.uniform(45, 65)
        ag_demand = np.random.uniform(30, 50)
        ag_cons = np.random.uniform(25, 45)
        yld = np.random.uniform(2.5, 4.5)
        wp = np.random.uniform(1.0, 2.0)
        temp = np.random.uniform(1.5, 2.5)
        eff = np.random.uniform(0.6, 0.8)
        
        st.session_state.simulation_results = {
            'pop': pop, 'supply': supply, 'demand': demand,
            'ag_demand': ag_demand, 'ag_cons': ag_cons, 'yld': yld,
            'wp': wp, 'temp': temp, 'eff': eff,
            'country': 'Ethiopia', 'target_year': 2030, 'crop_type': 'wheat'
        }
        st.session_state.simulation_run = True
        st.success("Simulation completed!")

def main():
    st.title("🌾 TOKUMA Research Platform")
    st.markdown("**Water-Energy-Food Nexus Modeling**")
    
    with st.sidebar:
        st.header("⚙️ Parameters")
        country = st.selectbox("Country", ["Ethiopia", "Kenya"])
        target_year = st.slider("Target Year", 2025, 2050, 2030)
        crop_type = st.selectbox("Crop", ["wheat", "maize"])
        
        run_trigger = st.button("🚀 Run Simulation", type="primary")
    
    if run_trigger:
        run_simulation()
    
    if st.session_state.get('simulation_run', False):
        results = st.session_state.simulation_results
        st.subheader(f"📈 Results for {results['country']} ({results['target_year']})")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Population", f"{results['pop']:.2f} M")
        col2.metric("Water Supply", f"{results['supply']:.2f} BCM")
        col3.metric("Water Demand", f"{results['demand']:.2f} BCM")
        col4.metric("Temperature Rise", f"+{results['temp']:.2f} °C")
        
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Agri Demand", f"{results['ag_demand']:.2f} BCM")
        col6.metric("Agri Consumed", f"{results['ag_cons']:.2f} BCM")
        col7.metric("Yield", f"{results['yld']:.2f} t/ha")
        col8.metric("Water Productivity", f"{results['wp']:.3f} kg/m³")
        
        st.success("✅ Results persist across tab switches!")
    else:
        st.info("Click 'Run Simulation' to see results")
    
    st.markdown("---")
    st.markdown("**🌾 TOKUMA Water-Energy-Food Nexus Platform** | Minimal Deployment Version")

if __name__ == "__main__":
    main()
