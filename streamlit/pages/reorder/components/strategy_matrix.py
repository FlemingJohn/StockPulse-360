"""
Reorder Page - Strategy Matrix Component  
Bubble chart showing procurement strategy by urgency and investment
"""

import streamlit as st
import plotly.express as px


def render_strategy_matrix(filtered_data, safety_days):
    """Render procurement strategy matrix (bubble chart)."""
    
    st.subheader("Procurement Strategy Matrix")
    st.markdown(f"*Strategic view of Urgency vs. Investment (Simulated: **{safety_days} Days**)*")
    
    # Create bubble chart
    fig = px.scatter(
        filtered_data,
        x="DAYS_UNTIL_STOCKOUT",
        y="SIMULATION_COST",
        size="SIMULATION_QUANTITY",
        color="RELIABILITY_SCORE",
        hover_name="ITEM",
        custom_data=['ESTIMATED_COST', 'REORDER_QUANTITY', 'COST_DELTA', 'SIMULATION_QUANTITY'],
        labels={
            "DAYS_UNTIL_STOCKOUT": "Order Within (Days)",
            "SIMULATION_COST": "Simulated Cost (₹)",
            "RELIABILITY_SCORE": "Reliability (%)",
            "SIMULATION_QUANTITY": "Simulated Qty"
        },
        color_continuous_scale="RdYlGn",
        template="plotly_white",
        height=500,
        size_max=40,
        range_x=[-1, max(30, filtered_data['DAYS_UNTIL_STOCKOUT'].max() * 1.1)],
        range_y=[0, max(1000, filtered_data['SIMULATION_COST'].max() * 1.2)]
    )
    
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>%{hovertext}</b>",
            "Urgency: Within %{x} days",
            "Simulated Cost: ₹%{y:,.0f}",
            "Simulated Qty: %{customdata[3]:,.0f}",
            "-----------------------",
            "Baseline Cost: ₹%{customdata[0]:,.0f}",
            "Baseline Qty: %{customdata[1]:,.0f}",
            "Delta: ₹%{customdata[2]:,.0f}",
            "<extra></extra>"
        ])
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode="closest",
        coloraxis_colorbar=dict(title="Reliability %")
    )
    
    st.plotly_chart(fig, use_container_width=True)
