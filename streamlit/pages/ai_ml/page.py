"""
AI/ML Insights Page
Main orchestrator for AI/ML forecasting features
"""

import streamlit as st
from datetime import datetime
from utils import load_seasonal_forecasts, section_header
from ..shared.filters import render_page_sidebar_filters
from .components import render_forecast_chart, render_seasonal_factors


def render_ai_ml_page():
    """Render AI/ML Insights page with independent filters."""
    # Load raw forecasts
    forecasts = load_seasonal_forecasts()
    
    # Sidebar Filters
    filtered_data = render_page_sidebar_filters(forecasts, "AI/ML")
    
    st.markdown(section_header("AI/ML Insights", "trending"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    if filtered_data is not None and not filtered_data.empty:
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_forecasts = len(forecasts)
            st.metric("Total Forecasts", total_forecasts, help="Total number of AI-generated forecasts")
        with col2:
            unique_items = forecasts['ITEM'].nunique() if 'ITEM' in forecasts.columns else 0
            st.metric("Items Analyzed", unique_items, help="Number of unique items with forecasts")
        with col3:
            unique_locations = forecasts['LOCATION'].nunique() if 'LOCATION' in forecasts.columns else 0
            st.metric("Locations", unique_locations, help="Number of locations covered")
        with col4:
            avg_forecast = forecasts['FORECASTED_USAGE'].mean() if 'FORECASTED_USAGE' in forecasts.columns else 0
            st.metric("Avg Forecast", f"{avg_forecast:.1f}", help="Average forecasted usage")
        
        st.divider()
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["Seasonal Forecasts", "Forecast Data"])
        
        with tab1:
            st.markdown("### Seasonal Usage Forecasts")
            st.markdown("AI-powered forecasts based on weekly and monthly seasonal patterns")
            
            # Filter by location and item
            col1, col2 = st.columns(2)
            with col1:
                locations = ['All'] + sorted(forecasts['LOCATION'].unique().tolist()) if 'LOCATION' in forecasts.columns else ['All']
                selected_location = st.selectbox("Select Location", locations, key="ai_location")
            with col2:
                items = ['All'] + sorted(forecasts['ITEM'].unique().tolist()) if 'ITEM' in forecasts.columns else ['All']
                selected_item = st.selectbox("Select Item", items, key="ai_item")
            
            # Render charts
            filtered_forecasts = render_forecast_chart(forecasts, selected_location, selected_item)
            render_seasonal_factors(filtered_forecasts)
        
        with tab2:
            st.markdown("### Forecast Data Table")
            st.dataframe(
                forecasts,
                use_container_width=True,
                height=400
            )
            
            # Download button
            csv = forecasts.to_csv(index=False)
            st.download_button(
                label="Download Forecast Data (CSV)",
                data=csv,
                file_name=f"seasonal_forecasts_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
    else:
        st.info("AI/ML forecasts are being generated. Please run the seasonal forecasting script to populate data.")
