"""
Overview Page - Heatmap Component
Stock health heatmap visualization
"""

import streamlit as st
import plotly.express as px


def render_heatmap(filtered_data):
    """Render stock health heatmap visualization."""
    
    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Create pivot table for heatmap
    pivot_data = filtered_data.pivot_table(
        index='LOCATION',
        columns='ITEM',
        values='HEALTH_SCORE',
        aggfunc='first'
    )
    
    if not pivot_data.empty:
        fig = px.imshow(
            pivot_data,
            labels=dict(x="Item", y="Location", color="Health Score"),
            color_continuous_scale=[[0, '#DC143C'], [0.5, '#FFA500'], [1, '#29B5E8']],
            aspect="auto",
            title="Stock Health Score by Location and Item"
        )
        fig.update_layout(
            height=400,
            font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
            title_font=dict(size=20, color="#0F4C81", family="Segoe UI"),
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#F0F2F6'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for heatmap.")
