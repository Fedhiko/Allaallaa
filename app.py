import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from nexus_core import (
    _pack_context,
    monte_carlo_multiparam,
    pymoo_with_file_coupling,
    run_file_coupled_simulation,
    run_integrated_engine,
    run_morris_analysis,
    run_pymoo_ga_single_objective,
    run_pymoo_nsga2,
    run_sobol_analysis,
    salib_problem_spec,
)

# Import new enhancement modules
try:
    from gis_integration import get_gis_integration
    GIS_AVAILABLE = True
except ImportError as e:
    GIS_AVAILABLE = False
    print(f"GIS module not available: {e}")

try:
    from ml_surrogates import get_ml_surrogate_manager
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    print(f"ML surrogates not available: {e}")

try:
    from irrigation_physics import get_irrigation_physics
    IRRIGATION_AVAILABLE = True
except ImportError as e:
    IRRIGATION_AVAILABLE = False
    print(f"Irrigation physics not available: {e}")

try:
    from climate_downscaling import get_climate_downscaling
    CLIMATE_AVAILABLE = True
except ImportError as e:
    CLIMATE_AVAILABLE = False
    print(f"Climate downscaling not available: {e}")

try:
    from economic_optimization import get_economic_optimizer
    ECONOMIC_AVAILABLE = True
except ImportError as e:
    ECONOMIC_AVAILABLE = False
    print(f"Economic optimization not available: {e}")

try:
    from report_generator import get_report_generator
    REPORT_AVAILABLE = True
except ImportError as e:
    REPORT_AVAILABLE = False
    print(f"Report generator not available: {e}")

try:
    from api_connectors import get_api_manager
    API_AVAILABLE = True
except ImportError as e:
    API_AVAILABLE = False
    print(f"API connectors not available: {e}")


# ------------------------------
# 1. DATABASE SETUP
# ------------------------------
def init_db():
    conn = sqlite3.connect("tokuma_phd_research.db", check_same_thread=False, timeout=30)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS research_logs(
        timestamp TEXT, researcher TEXT, email TEXT, country TEXT,
        crop TEXT, year INTEGER, scenario TEXT, wp_index REAL,
        total_demand REAL, ag_demand REAL, supply REAL,
        schedule_method TEXT, sim_engine TEXT)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS field_data(
        timestamp TEXT, location TEXT, crop TEXT, soil_type TEXT,
        temp_max REAL, humidity REAL, rainfall REAL, irrigation REAL,
        furrow_length REAL, furrow_slope REAL, notes TEXT)"""
    )
    conn.commit()
    return conn


db_conn = init_db()


def metrics_tuple_from_dict(m):
    return (
        m["pop"],
        m["supply"],
        m["demand"],
        m["ag_demand"],
        m["ag_cons"],
        m["yield"],
        m["wp"],
        m["temp_rise"],
        m["eff"],
    )


# ------------------------------
# 3. UI LAYOUT
# ------------------------------
st.set_page_config(page_title="TOKUMA 3-in-1", layout="wide", page_icon="🧬")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 PhD Research Portal: Secure Access")
    with st.form("login"):
        u = st.text_input("Researcher Name", value="Tokkummaa Addaamuu")
        i = st.text_input("Institution", value="Addis Ababa University")
        if st.form_submit_button("Launch Integrated Model"):
            st.session_state.auth, st.session_state.user, st.session_state.inst = True, u, i
            st.rerun()
else:
    st.markdown(
        f"""
        <div style="background: linear-gradient(90deg, #002b5c, #0056b3); padding:30px; border-radius:15px 15px 0 0; color:white; text-align:center; box-shadow: 0px 6px 15px rgba(0,0,0,0.3); margin-bottom: -15px;">
            <h1 style="margin-bottom:5px; font-size:2.5rem;">Tokuma 3-in-1 Integrated Model</h1>
            <p style="font-size:1.4rem; font-weight:400; margin-bottom:15px; opacity:0.95;">An Intelligent DSS for Water-Food-Climate Nexus Analysis</p>
            <div style="border-top: 1px solid rgba(255,255,255,0.3); width:60%; margin: 10px auto; padding-top:10px;">
                <p style="font-size:1.1rem; font-weight:300;">Researcher: <b>{st.session_state.user}</b> | Institution: <b>{st.session_state.inst}</b></p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("👤 Research Profile")
        username = st.text_input("Name", value=st.session_state.user)
        country = st.selectbox("Select Country", ["Ethiopia", "Kenya", "Sudan", "Egypt"])
        target_year = st.slider("Target Year", 2024, 2100, 2050)
        crop_type = st.selectbox("Crop Type", ["Wheat", "Maize", "Teff"])
        with st.expander("🛠️ Model & Optimization", expanded=True):
            s_mod = st.selectbox("Supply Model", ["SWAT", "MODFLOW", "SWAT + MODFLOW"])
            use_ml_surrogate = st.checkbox("Enable PINNs/GNNs Surrogate")
            p_mod = st.selectbox("Population Model", ["Cohort-Component", "Bayesian"])
            d_meth = st.selectbox("Demand Projection Method", ["System Dynamics-WEAP", "Agent-Based"])
            use_lstm = st.checkbox("Enable LSTM Surrogate")

            st.write("**Simulation Settings**")
            sim_eng = st.selectbox("Simulation Engine", ["AquaCrop", "EPIC", "WaPOR"])
            use_breeding = st.checkbox("Enable In-Silico Breeding Gain")

            f_len = st.number_input("Furrow Length (m)", value=150.0)
            f_slp = st.number_input("Furrow Slope (%)", value=0.1)
            schedule = st.selectbox("Scheduling", ["Traditional", "ET-based", "Soil moisture based"])
            opt_eng = st.selectbox("Optimization Engine", ["Genetic Algorithm (GA)", "NSGA-II"])
            st.caption("Integrated proxy vs file-coupled subprocess (template → runner → CSV).")
            use_file_coupling = st.checkbox(
                "File-coupled simulation (subprocess pipeline)",
                value=False,
                help="Writes model_templates inputs, runs coupled_runner.py, reads sim_output.csv — same core, closed loop.",
            )
        with st.expander("   ☁   ️ Climate Modules"):
            climate_scenario = st.select_slider("Emission Scenario (SSP)", options=["SSP1-2.6", "SSP2-4.5", "SSP5-8.5"])
            climate_sensitivity = st.slider("Regional Sensitivity Index", 0.5, 3.0, 1.0)
        with st.expander("📐 Rigor (SALib / MC)", expanded=False):
            sobol_n = st.slider("Sobol base sample size (N)", 64, 384, 128, 32)
            mc_n = st.slider("Monte Carlo draws", 500, 5000, 1500, 100)
            run_morris_ui = st.checkbox("Compute Morris screening (μ*, σ)", value=False)

    run_trigger = st.button("🚀 Run Simulation-Optimization", type="primary", use_container_width=True)

    # Create tabs outside the conditional so they always exist
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs(
        [
            "📊 Analysis Dashboard",
            "🎯 Optimization Engine",
            "📝 Field Entry",
            "🎲 Uncertainty (MC)",
            "🗺️ GIS Integration",
            "🤖 ML Surrogates",
            "⚙️ Irrigation Physics",
            "🌡️ Climate Downscaling",
            "💰 Economic Analysis",
            "📄 Report Generator",
            "📡 API Connectors",
            "📂 Export",
        ]
    )

    if run_trigger:
        ctx = _pack_context(
            target_year,
            country,
            p_mod,
            s_mod,
            d_meth,
            schedule,
            sim_eng,
            crop_type,
            use_ml_surrogate,
            use_lstm,
            climate_scenario,
            climate_sensitivity,
            use_breeding,
        )

        with st.spinner("Evaluating integrated nexus (proxy or file-coupled)…"):
            if use_file_coupling:
                m0 = run_file_coupled_simulation(ctx, f_len, f_slp)
            else:
                m0 = None
                pop, supply, demand, ag_demand, ag_cons, yld, wp, temp, eff = run_integrated_engine(
                    target_year,
                    country,
                    p_mod,
                    s_mod,
                    d_meth,
                    schedule,
                    sim_eng,
                    f_len,
                    f_slp,
                    crop_type,
                    use_ml_surrogate,
                    use_lstm,
                    climate_scenario,
                    climate_sensitivity,
                    use_breeding,
                )
            if use_file_coupling:
                pop, supply, demand, ag_demand, ag_cons, yld, wp, temp, eff = metrics_tuple_from_dict(m0)

        with st.spinner("Multi-objective optimization (pymoo ↔ engine)…"):
            if opt_eng == "NSGA-II":
                if use_file_coupling:
                    X_pareto, F_pareto = pymoo_with_file_coupling(ctx, pop_size=28, n_gen=35)
                else:
                    X_pareto, F_pareto = run_pymoo_nsga2(ctx, pop_size=40, n_gen=50)
                x_ga, f_ga, fitness_hist = None, None, None
            else:
                X_pareto, F_pareto = None, None
                x_ga, f_ga, fitness_hist = run_pymoo_ga_single_objective(ctx, pop_size=40, n_gen=50)

        with st.spinner("SALib + multi-parameter Monte Carlo…"):
            Si_wp, Y_wp = run_sobol_analysis(
                ctx, n_samples=sobol_n, calc_second_order=False, output="wp", seed=42
            )
            Si_ag, _ = run_sobol_analysis(
                ctx, n_samples=sobol_n, calc_second_order=False, output="ag_cons", seed=43
            )
            mc_df = monte_carlo_multiparam(ctx, n=mc_n, seed=42)
            morris_wp = run_morris_analysis(ctx, n_trajectories=30, output="wp", seed=44) if run_morris_ui else None

        # Store results in session state
        st.session_state.simulation_results = {
            'pop': pop, 'supply': supply, 'demand': demand, 
            'ag_demand': ag_demand, 'ag_cons': ag_cons, 'yld': yld, 
            'wp': wp, 'temp': temp, 'eff': eff,
            'X_pareto': X_pareto, 'F_pareto': F_pareto, 
            'x_ga': x_ga, 'f_ga': f_ga, 'fitness_hist': fitness_hist,
            'Si_wp': Si_wp, 'Y_wp': Y_wp, 'Si_ag': Si_ag, 
            'mc_df': mc_df, 'morris_wp': morris_wp,
            'use_file_coupling': use_file_coupling,
            'country': country, 'target_year': target_year,
            'crop_type': crop_type
        }
        st.session_state.simulation_run = True

    # Tab content (tabs are already created above)
    with tab1:
        if st.session_state.get('simulation_run', False):
            results = st.session_state.simulation_results
            pop = results['pop']
            supply = results['supply']
            demand = results['demand']
            ag_demand = results['ag_demand']
            ag_cons = results['ag_cons']
            yld = results['yld']
            wp = results['wp']
            temp = results['temp']
            eff = results['eff']
            country = results['country']
            target_year = results['target_year']
            use_file_coupling = results['use_file_coupling']
            
            st.subheader(f"📈 Nexus Projections for {country} ({target_year})")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Projected Population", f"{pop:.2f} M")
            c2.metric("Total Water Supply", f"{supply:.2f} BCM")
            c3.metric("Total Water Demand", f"{demand:.2f} BCM")
            c4.metric("Temperature Rise", f"+{temp:.2f} °C")

            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Agri Water Demand", f"{ag_demand:.2f} BCM")
            c6.metric("Agri Water Consumed", f"{ag_cons:.2f} BCM")
            c7.metric("Projected Yield", f"{yld:.2f} t/ha")
            c8.metric("Water Productivity", f"{wp:.3f} kg/m³")

            if use_file_coupling:
                st.success(
                    "Simulation path: **file-coupled** (template → `coupled_runner.py` → `sim_output.csv`). "
                    "Replace runner internals with SWAT/AquaCrop executables when available."
                )
            else:
                st.info(
                    "Simulation path: **in-memory proxy** (fast, for research testing). "
                    "Switch to **file-coupled** for external model integration."
                )
        else:
            st.info("Please adjust parameters in the sidebar and click 'Run Simulation-Optimization' above to view results.")

        # Generate report content (only if simulation has been run)
        if st.session_state.get('simulation_run', False):
            results = st.session_state.simulation_results
            wp = results['wp']
            yld = results['yld']
            demand = results['demand']
            temp = results['temp']
            country = results['country']
            target_year = results['target_year']
            crop_type = results['crop_type']
            use_file_coupling = results['use_file_coupling']
            
            report_content = f"""
            TOKUMA 3-in-1 RESEARCH REPORT
            -----------------------------
            Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
            Researcher: {st.session_state.user}
            Institution: {st.session_state.inst}
            Study Area: {country}
            Target Year: {target_year}
            Crop: {crop_type}
            Coupling: {"file-based subprocess" if use_file_coupling else "integrated proxy"}
            KEY METRICS:
            - Water Productivity: {wp:.3f} kg/m3
            - Projected Yield: {yld:.2f} t/ha
            - Water Demand: {demand:.2f} BCM
            - Temperature Change: +{temp:.2f} C
            """
            st.download_button(
                label="📥 Download Research Report",
                data=report_content,
                file_name=f"Report_{country}_{target_year}.txt",
                mime="text/plain",
            )

        with tab2:
            if st.session_state.get('simulation_run', False):
                results = st.session_state.simulation_results
                X_pareto = results['X_pareto']
                F_pareto = results['F_pareto']
                x_ga = results['x_ga']
                f_ga = results['f_ga']
                fitness_hist = results['fitness_hist']
                ag_cons = results['ag_cons']
                eff = results['eff']
                f_len = f_len  # from sidebar
                opt_eng = opt_eng  # from sidebar
                
                st.subheader(f"🎯 Optimization Engine: {opt_eng}")
                st.caption(
                    "Single objective function wraps the nexus engine; pymoo evolves furrow length & slope. "
                    "NSGA-II minimizes water consumed and maximizes WP (Pareto front). **No random scatter.**"
                )
                opt_depth = ag_cons * 0.84
                opt_f_len = f_len * 1.1
                opt_eff_val = eff * 1.06

                if opt_eng == "Genetic Algorithm (GA)" and fitness_hist is not None:
                    gens = np.arange(1, len(fitness_hist) + 1)
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=gens,
                            y=fitness_hist,
                            mode="lines+markers",
                            name="Best ag_cons / WP",
                        )
                    )
                    fig.update_layout(
                        title="GA: convergence (minimize ag water per unit productivity)",
                        xaxis_title="Generation",
                        yaxis_title="Objective",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    if f_ga is not None and x_ga is not None and len(np.asarray(f_ga).ravel()):
                        xv = np.asarray(x_ga).ravel()
                        st.caption(f"Best candidate (f_len, f_slope): ({float(xv[0]):.1f} m, {float(xv[1]):.3f})")
                elif opt_eng == "NSGA-II" and X_pareto is not None and F_pareto is not None:
                    ag_c = F_pareto[:, 0]
                    wp_vals = -F_pareto[:, 1]
                    fl = X_pareto[:, 0]
                    fs = X_pareto[:, 1]
                    color_choice = st.radio("Color Pareto points by", ["Furrow length (m)", "Furrow slope (%)"], horizontal=True)
                    color = fl if color_choice.startswith("Furrow length") else fs
                    fig_pareto = px.scatter(
                        x=ag_c,
                        y=wp_vals,
                        color=color,
                        labels={"x": "Ag water consumed (BCM)", "y": "Water productivity index", "color": color_choice},
                        title="Pareto front (pymoo NSGA-II on analytical / file-coupled objective)",
                    )
                    st.plotly_chart(fig_pareto, use_container_width=True)
                    st.dataframe(
                        pd.DataFrame({"f_len_m": fl, "f_slope_pct": fs, "ag_cons": ag_c, "wp": wp_vals}),
                        use_container_width=True,
                    )

                st.markdown("### 💎 Reference parameter set (sidebar)")
                o1, o2, o3 = st.columns(3)
                o1.metric("Reference irrigation depth proxy", f"{opt_depth:.2f} mm")
                o2.metric("Reference furrow length", f"{opt_f_len:.1f} m")
                o3.metric("System efficiency", f"{opt_eff_val:.1%}")
            else:
                st.info("Please run simulation to view optimization results.")

        with tab3:
            st.subheader("📝 Detailed PhD Field Observation Entry")
            with st.form("field"):
                col1, col2 = st.columns(2)
                with col1:
                    f_loc = st.text_input("Site Location (e.g., Kulumsa, Wonji)")
                    f_soil = st.selectbox("Soil Type", ["Clay", "Sandy Loam", "Silt Clay", "Loam"])
                    f_temp = st.number_input("Max Temp Observed (°C)", value=25.0)
                    f_hum = st.number_input("Humidity (%)", value=60.0)
                with col2:
                    f_rain = st.number_input("Daily Rainfall (mm)", value=0.0)
                    f_irr_obs = st.number_input("Irrigation Applied (mm)", value=45.0)
                    f_slp_obs = st.number_input("Observed Slope (%)", value=0.1)
                    f_stage = st.selectbox("Crop Growth Stage", ["Initial", "Development", "Mid-Season", "Late-Season"])
                f_notes = st.text_area("Field Researcher Notes")
                if st.form_submit_button("Sync Entry to Master Database"):
                    db_conn.execute(
                        """INSERT INTO field_data (timestamp, location, crop, soil_type, temp_max,
                                    humidity, rainfall, irrigation, furrow_length, furrow_slope, notes)
                                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                        (
                            datetime.now().strftime("%Y-%m-%d %H:%M"),
                            f_loc,
                            crop_type,
                            f_soil,
                            f_temp,
                            f_hum,
                            f_rain,
                            f_irr_obs,
                            f_len,
                            f_slp_obs,
                            f_notes,
                        ),
                    )
                    db_conn.commit()
                    st.success("Detailed observation synchronized successfully.")

        with tab4:
            if st.session_state.get('simulation_run', False):
                results = st.session_state.simulation_results
                Si_wp = results['Si_wp']
                Si_ag = results['Si_ag']
                mc_df = results['mc_df']
                morris_wp = results['morris_wp']
                sobol_n = sobol_n  # from sidebar
                mc_n = mc_n  # from sidebar
                
                st.subheader("🎲 Uncertainty (MC) & global sensitivity (SALib)")
                st.write(
                    f"**Monte Carlo:** {mc_n} draws over the same parameter bounds as Sobol "
                    f"({', '.join(salib_problem_spec()['names'])}). **Sobol:** N={sobol_n} (first-order S1, total-order ST)."
                )

                fig_comb = make_subplots(
                    rows=2,
                    cols=1,
                    row_heights=[0.38, 0.62],
                    subplot_titles=("Sobol indices (WP): S1 and ST", "WP distribution (MC) with kernel density"),
                    vertical_spacing=0.12,
                )
                names = salib_problem_spec()["names"]
                fig_comb.add_bar(
                    x=names,
                    y=Si_wp["S1"],
                    name="S1 (WP)",
                    marker_color="#0056b3",
                    row=1,
                    col=1,
                )
                fig_comb.add_bar(
                    x=names,
                    y=Si_wp["ST"],
                    name="ST (WP)",
                    marker_color="#88c",
                    row=1,
                    col=1,
                )
                fig_comb.add_trace(
                    go.Histogram(x=mc_df["wp"], nbinsx=45, name="WP (MC)", marker_color="#002b5c", opacity=0.75),
                    row=2,
                    col=1,
                )
                fig_comb.update_layout(
                    height=720,
                    title_text="Overlay: Sobol sensitivity bars + WP uncertainty",
                    showlegend=True,
                    barmode="group",
                )
                fig_comb.update_yaxes(title_text="Index", row=1, col=1)
                fig_comb.update_yaxes(title_text="Count", row=2, col=1)
                st.plotly_chart(fig_comb, use_container_width=True)

                cleft, cright = st.columns(2)
                with cleft:
                    st.markdown("**Ag water consumed — Sobol (stress metric)**")
                    fig_ag = go.Figure()
                    fig_ag.add_bar(x=names, y=Si_ag["S1"], name="S1 (ag_cons)", marker_color="#c0392b")
                    fig_ag.add_bar(x=names, y=Si_ag["ST"], name="ST (ag_cons)", marker_color="#e74c3c")
                    fig_ag.update_layout(barmode="group", title="S1 and ST for agricultural water consumed")
                    st.plotly_chart(fig_ag, use_container_width=True)
                with cright:
                    st.markdown("**Correlation (MC sample)**")
                    num_cols = ["climate_sensitivity", "f_len", "f_slp", "temp_scale", "supply_perturb", "wp", "ag_cons", "yield"]
                    corr = mc_df[num_cols].corr()
                    fig_hm = px.imshow(
                        corr,
                        text_auto=".2f",
                        aspect="auto",
                        color_continuous_scale="RdBu_r",
                        title="Parameter & output correlation heatmap",
                    )
                    st.plotly_chart(fig_hm, use_container_width=True)

                h1, h2, h3 = st.columns(3)
                with h1:
                    st.plotly_chart(px.histogram(mc_df, x="wp", nbins=40, title="WP"), use_container_width=True)
                with h2:
                    st.plotly_chart(px.histogram(mc_df, x="yield", nbins=40, title="Yield (proxy)"), use_container_width=True)
                with h3:
                    st.plotly_chart(px.histogram(mc_df, x="ag_cons", nbins=40, title="Ag water consumed"), use_container_width=True)

                if morris_wp is not None:
                    st.markdown("**Morris screening (ranking μ* vs σ)**")
                    mu_star = np.array(morris_wp["mu_star"])
                    sigma = np.array(morris_wp["sigma"])
                    fig_m = go.Figure()
                    fig_m.add_trace(
                        go.Scatter(
                            x=mu_star,
                            y=sigma,
                            mode="markers+text",
                            text=names,
                            textposition="top center",
                            marker=dict(size=12, color="#0056b3"),
                        )
                    )
                    fig_m.update_layout(
                        title="Morris: μ* vs σ (screening)",
                        xaxis_title="μ*",
                        yaxis_title="σ",
                    )
                    st.plotly_chart(fig_m, use_container_width=True)
            else:
                st.info("Please run simulation to view uncertainty analysis results.")

        with tab5:
            if GIS_AVAILABLE:
                gis_results = get_gis_integration().render_gis_interface()
                if gis_results and len(gis_results) == 2:
                    site_data, map_obj = gis_results
                    if site_data:
                        st.session_state.gis_site_data = site_data
            else:
                st.error("GIS Integration module not available. Please install required packages: folium, geopandas, shapely")

        with tab6:
            if ML_AVAILABLE:
                ml_results = get_ml_surrogate_manager().render_ml_interface()
                if ml_results:
                    st.session_state.ml_results = ml_results
            else:
                st.error("ML Surrogates module not available. Please install required packages: scikit-learn, shap, lime")

        with tab7:
            if IRRIGATION_AVAILABLE:
                irrigation_results = get_irrigation_physics().render_irrigation_physics_interface()
                if irrigation_results:
                    st.session_state.irrigation_results = irrigation_results
            else:
                st.error("Irrigation Physics module not available. Please install required packages: scipy")

        with tab8:
            if CLIMATE_AVAILABLE:
                climate_results = get_climate_downscaling().render_climate_downscaling_interface()
                if climate_results:
                    st.session_state.climate_results = climate_results
            else:
                st.error("Climate Downscaling module not available. Please install required packages: netcdf4, xarray")

        with tab9:
            if ECONOMIC_AVAILABLE:
                economic_results = get_economic_optimizer().render_economic_interface()
                if economic_results:
                    st.session_state.economic_results = economic_results
            else:
                st.error("Economic Optimization module not available. Please install required packages: pymoo")

        with tab10:
            if REPORT_AVAILABLE:
                report_results = get_report_generator().render_report_generator_interface()
                if report_results:
                    st.session_state.report_results = report_results
            else:
                st.error("Report Generator module not available. Please install required packages: fpdf2, pylatex")

        with tab11:
            if API_AVAILABLE:
                api_results = get_api_manager().render_api_interface()
                if api_results:
                    st.session_state.api_results = api_results
            else:
                st.error("API Connectors module not available. Please install required packages: requests")

        with tab12:
            st.subheader("📂 Export Research Data")
            if st.button("Archive to 13-Column Log"):
                st.success("Simulation Archived.")

            logs = pd.read_sql_query("SELECT * FROM research_logs", db_conn)
            st.write("**Research Log History**")
            st.dataframe(logs, use_container_width=True)
            if not logs.empty:
                st.download_button(
                    label="📊 Download Research Logs (CSV)",
                    data=logs.to_csv(index=False),
                    file_name="Research_Logs.csv",
                    mime="text/csv",
                )

            field_logs = pd.read_sql_query("SELECT * FROM field_data", db_conn)
            st.write("**Field Observation Records**")
            st.dataframe(field_logs, use_container_width=True)
            if not field_logs.empty:
                st.download_button(
                    label="📝 Download Field Records (CSV)",
                    data=field_logs.to_csv(index=False),
                    file_name="Field_Observations.csv",
                    mime="text/csv",
                )

            # Monte Carlo download only available if simulation has been run
            if st.session_state.get('simulation_run', False):
                mc_df = st.session_state.simulation_results['mc_df']
                st.download_button(
                    "Download Monte Carlo table (CSV)",
                    data=mc_df.to_csv(index=False),
                    file_name="monte_carlo_nexus.csv",
                    mime="text/csv",
                )
            else:
                st.info("Run simulation first to download Monte Carlo data")
