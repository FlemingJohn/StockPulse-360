"""
Reorder Recommendations Page
Main orchestrator for reorder recommendations with simulation capabilities
"""

import streamlit as st
from utils import load_reorder_recommendations, load_purchase_orders, section_header
from ..shared.filters import render_page_sidebar_filters
from .components import render_simulation_controls, render_strategy_matrix, render_recommendations_table

try:
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.metric_cards import style_metric_cards
    EXTRAS_AVAILABLE = True
except ImportError:
    EXTRAS_AVAILABLE = False


def render_reorder_page():
    """Render Reorder Recommendations page with its own filters."""
    
    # Simulation controls (safety days slider)
    safety_days = render_simulation_controls()
    
    # Load raw data
    raw_procurement = load_reorder_recommendations()
    po_data = load_purchase_orders()
    
    # Sidebar Filters
    filtered_data = render_page_sidebar_filters(raw_procurement, "Reorder")
    
    # Join with PO Data to get Best Supplier and Reliability Score
    if not filtered_data.empty and not po_data.empty:
        filtered_data = filtered_data.merge(
            po_data[['LOCATION', 'ITEM', 'SUPPLIER_NAME', 'RELIABILITY_SCORE']], 
            on=['LOCATION', 'ITEM'], 
            how='left'
        )
        filtered_data['SUPPLIER_NAME'] = filtered_data['SUPPLIER_NAME'].fillna('N/A')
        filtered_data['RELIABILITY_SCORE'] = filtered_data['RELIABILITY_SCORE'].fillna(75.0)

    # Dynamic Recalculation based on Safety Days
    if not filtered_data.empty:
        filtered_data = filtered_data.reset_index(drop=True)
        
        # Recalculate simulation quantities and costs
        filtered_data['SIMULATION_QUANTITY'] = (safety_days - filtered_data['DAYS_UNTIL_STOCKOUT']).clip(lower=0) * filtered_data['AVG_DAILY_USAGE']
        filtered_data['SIMULATION_QUANTITY'] = filtered_data['SIMULATION_QUANTITY'].fillna(0)
        
        filtered_data['UNIT_COST'] = filtered_data['ESTIMATED_COST'] / filtered_data['REORDER_QUANTITY'].replace(0, 1)
        filtered_data['UNIT_COST'] = filtered_data['UNIT_COST'].fillna(10.0)
        filtered_data['SIMULATION_COST'] = filtered_data['SIMULATION_QUANTITY'] * filtered_data['UNIT_COST']
        filtered_data['SIMULATION_COST'] = filtered_data['SIMULATION_COST'].fillna(0)
        
        filtered_data['COST_DELTA'] = filtered_data['SIMULATION_COST'] - filtered_data['ESTIMATED_COST']
        filtered_data['QTY_DELTA'] = filtered_data['SIMULATION_QUANTITY'] - filtered_data['REORDER_QUANTITY']

    # Header
    if EXTRAS_AVAILABLE:
        colored_header(
            label="Reorder Recommendations",
            description=f"Smart suggestions simulating {safety_days} days of coverage",
            color_name="green-70"
        )
    else:
        st.markdown(section_header("Reorder Recommendations", "cart"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if filtered_data is not None and not filtered_data.empty:
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Items to Reorder", len(filtered_data),
                     help="Total items requiring reorder")
        with col2:
            total_cost = filtered_data['SIMULATION_COST'].sum()
            delta_cost = filtered_data['COST_DELTA'].sum()
            st.metric("Total Estimated Cost", f"₹{total_cost:,.0f}",
                     delta=f"₹{delta_cost:,.0f} vs Baseline", delta_color="inverse",
                     help=f"Projected budget for {safety_days} days of stock")
        with col3:
            urgent_count = len(filtered_data[filtered_data['DAYS_UNTIL_STOCKOUT'] <= 1])
            st.metric("Urgent Orders", urgent_count,
                     help="Items needing immediate procurement")
        
        if EXTRAS_AVAILABLE:
            style_metric_cards(
                background_color="#FFFFFF",
                border_left_color="#4CAF50",
                border_color="#E0E0E0",
                box_shadow=True
            )
        
        st.divider()

        # Strategy Matrix
        render_strategy_matrix(filtered_data, safety_days)
        
        st.divider()

        # Recommendations Table
        render_recommendations_table(filtered_data)
    else:
        st.info("No reorder recommendations at this time.")
