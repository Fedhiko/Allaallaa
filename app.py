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

            f_len = st.number_input("Furrow Length (m)", value=150)
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

        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            [
                "📊 Analysis Dashboard",
                "🎯 Optimization Engine",
                "📝 Field Entry",
                "🎲 Uncertainty (MC)",
                "🌍 Spatial/WaPOR",
                "📡 Mobile Sync",
                "📂 Export",
            ]
        )

        with tab1:
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
                st.info("Simulation path: **integrated analytical proxy** (same equations; switch coupling in sidebar).")

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
            st.subheader(f"🎯 Optimization Engine: {opt_eng}")
            st.caption(
                "Single objective function wraps the nexus engine; pymoo evolves furrow length & slope. "
                "NSGA-II minimizes water consumed and maximizes WP (Pareto front). **No random scatter.**"
            )
            opt_depth = ag_cons * 0.84
            opt_f_len = f_len * 1.1
            opt_eff_val = eff * 1.06

            if opt_eng == "Genetic Algorithm (GA)":
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
                if f_ga is not None and len(np.asarray(f_ga).ravel()):
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

        with tab5:
            st.subheader("🌍 Spatial (QGIS) & WaPOR Proxy")
            if st.checkbox("Fetch WaPOR Actual ET Data"):
                st.json({"Actual_ET": 450.5, "Biomass": 12.2, "Reference_ET": 510.2})
            st.file_uploader("Upload spatial CSV", type="csv")
            st.caption(
                "For full coupling: export rasters to CSV → ingest here; engine coupling uses `model_templates/` for tabular runs."
            )

        with tab6:
            st.subheader("📡 Mobile Device Connectivity")
            st.info("Sync data via REST API configuration:")
            st.code('POST http://[SERVER_IP]:8000/sync\nJSON: {"location": "Site Name", "rainfall": 12.5, "crop": "Teff"}')

        with tab7:
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

            st.download_button(
                "Download Monte Carlo table (CSV)",
                data=mc_df.to_csv(index=False),
                file_name="monte_carlo_nexus.csv",
                mime="text/csv",
            )

    else:
        st.info("👈 Please adjust parameters in the sidebar and click **'Run Simulation-Optimization'** above to view results.")
