"""
Reorder Page - Simulation Controls Component
Interactive slider and controls for safety stock simulation
"""

import streamlit as st


def render_simulation_controls():
    """Render simulation controls (safety days slider and reset button)."""
    container = st.session_state.get('filter_container', st.sidebar)
    
    # Sidebar Controls for Simulation
    container.markdown(f'<div class="sidebar-filter-header">Simulation Settings</div>', unsafe_allow_html=True)
    
    # Dynamic Safety Days Slider with Session State
    if 'safety_days_sim' not in st.session_state:
        st.session_state['safety_days_sim'] = 30
        
    def reset_simulation():
        st.session_state['safety_days_sim'] = 30
        
    container.button("Reset Simulation", use_container_width=True, on_click=reset_simulation)
    
    safety_days = container.slider(
        "Secure Stock For (Days)", 
        min_value=14, 
        max_value=120, 
        key='safety_days_sim',
        step=7,
        help="Simulate the budget needed to secure stock for a specific duration."
    )
    
    return safety_days
