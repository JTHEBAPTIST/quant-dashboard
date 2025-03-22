import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from engine.optimizer_engine import run_optimizer
import riskfolio as rp


@st.cache_data
def load_sector_options():
    df = pd.read_csv("data/tickers_full_cleaned.csv")
    return sorted(df['FactSet Econ Sector'].dropna().unique())


def analysis_tab():
    st.title("📊 Strategy Builder & Optimizer")

    st.subheader("🧠 Strategy Parameters")
    col1, col2, col3 = st.columns(3)

    with col1:
        optimization_type = st.selectbox("Optimization Type", ["Mean-Variance", "Max Sharpe"])
    
    sector_options = load_sector_options()
    with col2:
        select_all = st.checkbox("Select All Sectors")
        selected_universe = st.multiselect("Choose Sectors", sector_options,
                                           default=sector_options if select_all else [])
    
    with col3:
        risk_aversion = st.slider("Risk Aversion", 0.0, 10.0, 2.0)

    st.markdown("### 🔧 Constraints")
    col4, col5 = st.columns(2)
    with col4:
        max_weight = st.slider("Max Weight per Stock (%)", 5, 100, 20)
    with col5:
        max_holdings = st.slider("Max Number of Holdings", 5, 50, 15)

    tracking_error_limit = st.number_input("Tracking Error Limit (future use)", value=0.05)

    if st.button("🚀 Run Optimization"):
        with st.spinner("Optimizing portfolio using Riskfolio-Lib..."):
            try:
                if not selected_universe:
                    st.warning("⚠️ Please select at least one sector.")
                    return

                start_time = time.time()

                weights_df, port = run_optimizer(
                    sector_selection=selected_universe,
                    risk_aversion=risk_aversion,
                    tracking_error_limit=tracking_error_limit,
                    optimization_type=optimization_type,
                    max_weight=max_weight / 100,
                    max_holdings=max_holdings
                )

                elapsed = time.time() - start_time
                st.success(f"✅ Optimization completed in {elapsed:.2f} seconds")

                st.subheader("📋 Optimized Portfolio Allocation")
                st.dataframe(weights_df)

                csv = weights_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Portfolio as CSV", csv, file_name="optimized_portfolio.csv")

                st.subheader("📈 Efficient Frontier")
                fig = plot_efficient_frontier(port)
                st.pyplot(fig)

            except Exception as e:
                st.error(f"❌ Optimization failed: {e}")


# 🔧 Efficient Frontier Plot
def plot_efficient_frontier(portfolio_object):
    try:
        frontier = portfolio_object.efficient_frontier(model='Classic', rm='MV', points=50)
        fig, ax = plt.subplots(figsize=(10, 5))
        rp.plot_frontier(portfolio_object, frontier=frontier, ax=ax, rm='MV', showfig=False)
        ax.set_title("Efficient Frontier")
        return fig
    except Exception as e:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, f"Frontier failed:\n{e}", ha='center', va='center')
        return fig
