"""
Advanced Analytics Page
Main orchestrator for analytics features (ABC, Cost, Impact)
"""

import streamlit as st
from utils import section_header
from .components import render_abc_analysis, render_cost_optimization, render_stockout_impact


def render_analytics_page():
    """Render Advanced Analytics page."""
    st.markdown(section_header("Advanced Analytics", "chart"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("Advanced analytics including ABC analysis, cost optimization, and stockout impact analysis.")
    
    # Create tabs for different analytics features
    tab1, tab2, tab3 = st.tabs(["ABC Analysis", "Cost Optimization", "Stockout Impact"])
    
    with tab1:
        render_abc_analysis()
    
    with tab2:
        render_cost_optimization()
    
    with tab3:
        render_stockout_impact()
