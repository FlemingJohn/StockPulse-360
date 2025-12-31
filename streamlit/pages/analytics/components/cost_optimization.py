"""Analytics - Cost Optimization Component - See pages.py lines 762-980 for full implementation"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_budget_tracking, load_reorder_recommendations, load_abc_analysis, get_svg_icon

def render_cost_optimization():
    """Render Cost Optimization tab with interactive slider."""
    st.markdown("### Cost Optimization Dashboard")
    st.markdown("Track budget, identify savings, and optimize procurement costs")
    
    budget_data = load_budget_tracking()
    reorder_data = load_reorder_recommendations()
    abc_data = load_abc_analysis()
    
    if not budget_data.empty:
        row = budget_data.iloc[0]
        
        # Interactive Budget Slider
        st.markdown("---")
        st.markdown("#### 💡 Budget Scenario Planning")
        col_slider, col_info = st.columns([3, 1])
        
        with col_slider:
            adjusted_budget = st.slider(
                "Adjust Monthly Budget for Scenario Analysis (₹)",
                min_value=int(row['MONTHLY_BUDGET'] * 0.5),
                max_value=int(row['MONTHLY_BUDGET'] * 2),
                value=int(row['MONTHLY_BUDGET']),
                step=10000,
                help="Slide to see how different budget levels impact your procurement strategy"
            )
        
        with col_info:
            budget_change = ((adjusted_budget - row['MONTHLY_BUDGET']) / row['MONTHLY_BUDGET']) * 100
            change_color = "#32CD32" if budget_change > 0 else "#DC143C" if budget_change < 0 else "#FFA500"
            st.markdown(f"""
            <div style="background: {change_color}20; padding: 1rem; border-radius: 8px; border-left: 4px solid {change_color};">
                <div style="font-size: 0.9rem; color: #666;">Budget Change</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: {change_color};">{budget_change:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recalculate metrics based on adjusted budget
        adjusted_remaining = adjusted_budget - row['ESTIMATED_SPEND']
        adjusted_utilization = (row['ESTIMATED_SPEND'] / adjusted_budget) * 100
        
        if adjusted_utilization > 100:
            adjusted_status = "OVER_BUDGET"
        elif adjusted_utilization > 90:
            adjusted_status = "WARNING"
        elif adjusted_utilization > 75:
            adjusted_status = "MODERATE"
        else:
            adjusted_status = "HEALTHY"
        
        st.markdown("---")
        
        # Budget metrics with adjusted values
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Monthly Budget", f"₹{adjusted_budget:,.0f}", 
                     delta=f"₹{adjusted_budget - row['MONTHLY_BUDGET']:,.0f}" if adjusted_budget != row['MONTHLY_BUDGET'] else None)
        with col2:
            st.metric("Estimated Spend", f"₹{row['ESTIMATED_SPEND']:,.0f}")
        with col3:
            delta_color = "inverse" if adjusted_remaining < 0 else "normal"
            st.metric("Remaining Budget", f"₹{adjusted_remaining:,.0f}", 
                     delta=f"{adjusted_utilization:.1f}%")
        with col4:
            status_icon = {'HEALTHY': 'check', 'MODERATE': 'info', 'WARNING': 'alert', 'OVER_BUDGET': 'alert'}
            icon_svg = get_svg_icon(status_icon.get(adjusted_status, 'info'), size=18)
            st.markdown(f"**Budget Status:** {icon_svg} {adjusted_status}", unsafe_allow_html=True)
        
        st.markdown("---")
        
       # Budget gauge with adjusted value
        col_gauge, col_breakdown = st.columns([1, 1])
        
        with col_gauge:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = adjusted_utilization,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Budget Utilization %", 'font': {'size': 20}},
                delta = {'reference': 100},
                number = {'suffix': "%"},
                gauge = {
                    'axis': {'range': [None, 150]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 75], 'color': "#32CD32"},
                        {'range': [75, 90], 'color': "#FFD700"},
                        {'range': [90, 100], 'color': "#FFA500"},
                        {'range': [100, 150], 'color': "#DC143C"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 100}}
            ))
            fig.update_layout(height=350, font=dict(family="Segoe UI, sans-serif"))
            st.plotly_chart(fig, use_container_width=True)
        
        # Cost Breakdown by ABC Category
        with col_breakdown:
            st.markdown("#### 📊 Cost by ABC Category")
            
            if not reorder_data.empty and not abc_data.empty:
                # Merge reorder data with ABC classification
                reorder_with_abc = reorder_data.merge(
                    abc_data[['ITEM', 'ABC_CATEGORY']], 
                    on='ITEM', 
                    how='left'
                )
                reorder_with_abc['ABC_CATEGORY'] = reorder_with_abc['ABC_CATEGORY'].fillna('C')
                
                # Calculate cost by category
                category_cost = reorder_with_abc.groupby('ABC_CATEGORY')['ESTIMATED_COST'].sum().reset_index()
                category_cost.columns = ['Category', 'Total_Cost']
                
                # Pie chart
                fig_pie = px.pie(
                    category_cost,
                    values='Total_Cost',
                    names='Category',
                    title='',
                    color='Category',
                    color_discrete_map={'A': '#DC143C', 'B': '#FFA500', 'C': '#32CD32'},
                    hole=0.4
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(
                    height=350,
                    showlegend=True,
                    font=dict(family="Segoe UI, sans-serif"),
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Cost breakdown requires reorder and ABC data")
    else:
        st.info("🔧 Budget tracking view not found. Run `python/create_advanced_views.py` to create it.")
