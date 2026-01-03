"""AI/ML page - Seasonal factors component"""
import streamlit as st
import plotly.express as px
import pandas as pd

def render_seasonal_factors(filtered_forecasts):
    """Render seasonal factors bar chart."""
    if filtered_forecasts is None or filtered_forecasts.empty:
        return
    
    if 'SEASONAL_FACTOR' in filtered_forecasts.columns:
        # Safety: Ensure types are correct for Plotly
        try:
            filtered_forecasts = filtered_forecasts.copy()
            if 'FORECAST_DATE' in filtered_forecasts.columns:
                filtered_forecasts['FORECAST_DATE'] = pd.to_datetime(filtered_forecasts['FORECAST_DATE'])
            filtered_forecasts['SEASONAL_FACTOR'] = pd.to_numeric(filtered_forecasts['SEASONAL_FACTOR'], errors='coerce')
        except:
            pass
            
        st.markdown("#### Seasonal Adjustment Factors")
        st.markdown("Values > 1.0 indicate higher demand, < 1.0 indicate lower demand")
        
        fig2 = px.bar(
            filtered_forecasts,
            x='FORECAST_DATE',
            y='SEASONAL_FACTOR',
            color='SEASONAL_FACTOR',
            title="Seasonal Demand Patterns",
            labels={'SEASONAL_FACTOR': 'Seasonal Factor', 'FORECAST_DATE': 'Date'},
            color_continuous_scale=[[0, '#DC143C'], [0.5, '#FFA500'], [1, '#29B5E8']]
        )
        fig2.update_layout(
            height=300,
            font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#F0F2F6'
        )
        st.plotly_chart(fig2, use_container_width=True)
