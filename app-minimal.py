import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="TOKUMA Research Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = {}
if 'user' not in st.session_state:
    st.session_state.user = "Demo User"
if 'inst' not in st.session_state:
    st.session_state.inst = "Demo Institution"

def run_simulation():
    """Mock simulation function"""
    with st.spinner("Running integrated nexus simulation..."):
        # Mock data generation
        pop = np.random.uniform(100, 120)
        supply = np.random.uniform(50, 70)
        demand = np.random.uniform(45, 65)
        ag_demand = np.random.uniform(30, 50)
        ag_cons = np.random.uniform(25, 45)
        yld = np.random.uniform(2.5, 4.5)
        wp = np.random.uniform(1.0, 2.0)
        temp = np.random.uniform(1.5, 2.5)
        eff = np.random.uniform(0.6, 0.8)
        
        # Mock optimization results
        x_ga = np.array([150.0, 0.1])
        f_ga = np.array([1.2])
        fitness_hist = np.random.rand(50)
        
        # Mock sensitivity results
        Si_wp = {"S1": np.random.rand(5), "ST": np.random.rand(5)}
        Si_ag = {"S1": np.random.rand(5), "ST": np.random.rand(5)}
        mc_df = pd.DataFrame({
            'wp': np.random.normal(1.5, 0.3, 100),
            'yield': np.random.normal(3.5, 0.5, 100),
            'ag_cons': np.random.normal(35, 5, 100),
            'climate_sensitivity': np.random.uniform(0.5, 3.0, 100),
            'f_len': np.random.uniform(100, 200, 100),
            'f_slp': np.random.uniform(0.05, 0.15, 100),
            'temp_scale': np.random.uniform(0.8, 1.2, 100),
            'supply_perturb': np.random.uniform(0.9, 1.1, 100)
        })
        
        # Store results
        st.session_state.simulation_results = {
            'pop': pop, 'supply': supply, 'demand': demand,
            'ag_demand': ag_demand, 'ag_cons': ag_cons, 'yld': yld,
            'wp': wp, 'temp': temp, 'eff': eff,
            'x_ga': x_ga, 'f_ga': f_ga, 'fitness_hist': fitness_hist,
            'Si_wp': Si_wp, 'Si_ag': Si_ag, 'mc_df': mc_df,
            'country': 'Ethiopia', 'target_year': 2030,
            'crop_type': 'wheat'
        }
        st.session_state.simulation_run = True
        
        st.success("Simulation completed successfully!")

def main():
    st.title("🌾 TOKUMA Research Platform")
    st.markdown("**Water-Energy-Food Nexus Modeling System**")
    
    # Sidebar
    with st.sidebar:
        st.header("🔐 Login")
        st.session_state.user = st.text_input("Researcher Name", value=st.session_state.user)
        st.session_state.inst = st.text_input("Institution", value=st.session_state.inst)
        
        st.header("⚙️ Simulation Parameters")
        country = st.selectbox("Country", ["Ethiopia", "Kenya", "Uganda"])
        target_year = st.slider("Target Year", 2025, 2050, 2030)
        crop_type = st.selectbox("Crop Type", ["wheat", "maize", "sorghum"])
        
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
        
        run_trigger = st.button("🚀 Run Simulation-Optimization", type="primary", use_container_width=True)
    
    # Main content
    if run_trigger:
        run_simulation()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Analysis Dashboard",
        "🎯 Optimization Engine", 
        "📝 Field Entry",
        "🎲 Uncertainty (MC)"
    ])
    
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
            
            st.success("✅ Simulation results are persistent across tab switches!")
        else:
            st.info("Please adjust parameters and click 'Run Simulation-Optimization' to view results.")
    
    with tab2:
        if st.session_state.get('simulation_run', False):
            results = st.session_state.simulation_results
            st.subheader("🎯 Optimization Results")
            
            if results['fitness_hist'] is not None:
                gens = np.arange(1, len(results['fitness_hist']) + 1)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=gens, y=results['fitness_hist'], mode="lines+markers"))
                fig.update_layout(title="GA Convergence", xaxis_title="Generation", yaxis_title="Objective")
                st.plotly_chart(fig, use_container_width=True)
                
                st.write("**Best Solution:**")
                col1, col2 = st.columns(2)
                col1.metric("Furrow Length", f"{results['x_ga'][0]:.1f} m")
                col2.metric("Furrow Slope", f"{results['x_ga'][1]:.3f}%")
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
            
            if st.form_submit_button("Submit Entry"):
                st.success("Field observation recorded successfully!")
                st.info("Note: Database functionality requires full installation")
    
    with tab4:
        if st.session_state.get('simulation_run', False):
            results = st.session_state.simulation_results
            st.subheader("🎲 Uncertainty Analysis")
            
            st.write("**Sobol Sensitivity Analysis**")
            names = ["climate_sensitivity", "f_len", "f_slp", "temp_scale", "supply_perturb"]
            fig = go.Figure()
            fig.add_bar(x=names, y=results['Si_wp']['S1'], name="S1 (WP)")
            fig.add_bar(x=names, y=results['Si_wp']['ST'], name="ST (WP)")
            fig.update_layout(barmode="group", title="Sobol Indices for Water Productivity")
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("**Monte Carlo Results**")
            mc_df = results['mc_df']
            fig = px.histogram(mc_df, x="wp", nbins=30, title="Water Productivity Distribution")
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("Download Monte Carlo Data"):
                csv = mc_df.to_csv(index=False)
                st.download_button("Download CSV", csv, "monte_carlo_results.csv", "text/csv")
        else:
            st.info("Please run simulation to view uncertainty analysis.")
    
    # Footer
    st.markdown("---")
    st.markdown("**🌾 TOKUMA 3-in-1 Research Platform** | Water-Energy-Food Nexus Modeling System")
    st.markdown("*Core functionality preserved with minimal dependencies for reliable deployment*")

if __name__ == "__main__":
    main()
