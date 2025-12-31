"""
Overview & Heatmap Page
Main orchestrator for the overview page components
"""

import streamlit as st
from utils import load_stock_risk_data, section_header
from ..shared.filters import render_page_sidebar_filters
from .components import render_kpi_metrics, render_heatmap, render_table_view


def render_overview_page():
    """Render Overview & Heatmap page with its own filters."""
    # Load raw data
    stock_data = load_stock_risk_data()
    
    # Sidebar Filters
    filtered_data = render_page_sidebar_filters(stock_data, "Overview")
    
    container = st.session_state.get('filter_container', st.sidebar)
    
    # Additional Status Filter for Overview
    if not filtered_data.empty and 'STOCK_STATUS' in filtered_data.columns:
        status_options = ['All'] + sorted(filtered_data['STOCK_STATUS'].unique().tolist())
        selected_status = container.multiselect("Stock Status", status_options, default=['All'], key="ov_status")
        if 'All' not in selected_status and selected_status:
            filtered_data = filtered_data[filtered_data['STOCK_STATUS'].isin(selected_status)]

    # Check if data is available after filtering
    if filtered_data is None or filtered_data.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Render KPI Metrics
    render_kpi_metrics(filtered_data)
    
    st.divider()
    
    # Stock Health Heatmap
    st.markdown(section_header("Stock Health Heatmap", "map"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Heatmap View", "Table View"])
    
    with tab1:
        render_heatmap(filtered_data)
    
    with tab2:
        render_table_view(filtered_data)
