"""AI/ML page - Forecast chart component"""
import streamlit as st
import plotly.express as px

def render_forecast_chart(forecasts, selected_location, selected_item):
    """Render forecast line chart."""
    filtered_forecasts = forecasts.copy()
    if selected_location != 'All':
        filtered_forecasts = filtered_forecasts[filtered_forecasts['LOCATION'] == selected_location]
    if selected_item != 'All':
        filtered_forecasts = filtered_forecasts[filtered_forecasts['ITEM'] == selected_item]
    
    if not filtered_forecasts.empty:
        fig = px.line(
            filtered_forecasts,
            x='FORECAST_DATE',
            y='FORECASTED_USAGE',
            color='ITEM' if selected_location != 'All' else 'LOCATION',
            title=f"Seasonal Forecast - {selected_location} - {selected_item}",
            labels={'FORECASTED_USAGE': 'Forecasted Usage', 'FORECAST_DATE': 'Date'},
            markers=True
        )
        fig.update_layout(
            height=400,
            font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
            title_font=dict(size=18, color="#0F4C81"),
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#F0F2F6',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        return filtered_forecasts
    else:
        st.info("No forecast data available for the selected filters.")
        return None
