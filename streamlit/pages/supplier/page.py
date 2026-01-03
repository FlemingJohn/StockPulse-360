"""
Supplier Management Page
Main orchestrator for supplier features
"""

import streamlit as st
from utils import section_header
from .components import (
    render_purchase_orders,
    render_performance_metrics,
    render_supplier_comparison,
    render_delivery_schedule
)


def render_supplier_page():
    """Render Supplier Management page."""
    st.markdown(section_header("Supplier Management", "supplier"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create tabs for different supplier features
    tab1, tab2, tab3 = st.tabs([
        "Purchase Orders",
        "Supplier Comparison",
        "Delivery Calendar"
    ])
    
    with tab1:
        render_purchase_orders()
    
    with tab2:
        render_supplier_comparison()
    
    with tab3:
        render_delivery_schedule()
