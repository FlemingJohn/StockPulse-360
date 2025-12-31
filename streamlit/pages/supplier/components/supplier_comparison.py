"""Supplier - Comparison Tab - Simplified stub"""
import streamlit as st
from utils import load_supplier_performance
import plotly.express as px

def render_supplier_comparison():
    """Render Supplier Comparison tab."""
    st.markdown("### Supplier Comparison")
    perf_data = load_supplier_performance()
    
    if not perf_data.empty:
        fig = px.bar(perf_data, x='SUPPLIER_NAME', y='RELIABILITY_SCORE',
                    title="Supplier Reliability Comparison")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No comparison data available.")
