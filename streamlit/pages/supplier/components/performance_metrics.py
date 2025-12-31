"""Supplier - Performance Metrics Tab - Simplified stub"""
import streamlit as st
from utils import load_supplier_performance
import plotly.express as px

def render_performance_metrics():
    """Render Performance Metrics tab."""
    st.markdown("### Supplier Performance Metrics")
    perf_data = load_supplier_performance()
    
    if not perf_data.empty:
        st.dataframe(perf_data, use_container_width=True, height=400)
    else:
        st.info("No performance data available.")
