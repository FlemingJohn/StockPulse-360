"""Analytics - ABC Analysis Component - Imports the tab content from old pages.py for now"""
import streamlit as st
import plotly.express as px
from utils import load_abc_analysis

def render_abc_analysis():
    """Render ABC Analysis tab."""
    st.markdown("### ABC Analysis")
    st.markdown("Classify inventory by value contribution (Pareto Principle)")
    
    abc_data = load_abc_analysis()
    
    if not abc_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            a_items = len(abc_data[abc_data['ABC_CATEGORY'] == 'A'])
            st.metric("Category A Items", a_items, help="High-value critical items")
        with col2:
            b_items = len(abc_data[abc_data['ABC_CATEGORY'] == 'B'])
            st.metric("Category B Items", b_items, help="Medium-value items")
        with col3:
            c_items = len(abc_data[abc_data['ABC_CATEGORY'] == 'C'])
            st.metric("Category C Items", c_items, help="Low-value items")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(abc_data, x='ITEM', y='TOTAL_VALUE', color='ABC_CATEGORY',
                         title="Item Value Distribution (ABC  Classification)",
                         labels={'TOTAL_VALUE': 'Total Value (₹)', 'ITEM': 'Item'},
                         color_discrete_map={'A': '#DC143C', 'B': '#FFA500', 'C': '#32CD32'})
            fig.update_layout(height=400, font=dict(family="Segoe UI, sans-serif", color="#0F4C81"),
                            plot_bgcolor='#FFFFFF', paper_bgcolor='#F0F2F6')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig2 = px.pie(abc_data, values='TOTAL_VALUE', names='ITEM', title="Value Contribution",
                         color='ABC_CATEGORY', color_discrete_map={'A': '#DC143C', 'B': '#FFA500', 'C': '#32CD32'})
            fig2.update_layout(height=400, font=dict(family="Segoe UI, sans-serif", color="#0F4C81"))
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("#### ABC Classification Details")
        st.dataframe(abc_data[['ITEM', 'TOTAL_VALUE', 'TOTAL_QUANTITY', 'VALUE_PERCENTAGE', 'ABC_CATEGORY', 'CATEGORY_DESCRIPTION']],
                    use_container_width=True, height=200)
    else:
        st.info("🔧 ABC Analysis view not found. Run `python/create_abc_view.py` to create it.")
