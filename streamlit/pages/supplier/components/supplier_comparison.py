"""Supplier - Comparison Tab - Simplified stub"""
import streamlit as st
from utils import load_supplier_performance
import plotly.express as px

def render_supplier_comparison():
    """Render Supplier Comparison tab."""
    from utils import load_supplier_comparison
    
    st.markdown("### Supplier Benchmarking")
    st.markdown("Compare suppliers based on reliability, lead time, and pricing.")
    
    comparison_data = load_supplier_comparison()
    
    if comparison_data.empty:
        st.info("No comparison data available. Generate some purchase orders first.")
        return

    # Filter by item
    items = sorted(comparison_data['ITEM'].unique())
    selected_item = st.selectbox("Select Item to Benchmark", items)
    
    if selected_item:
        filtered_df = comparison_data[comparison_data['ITEM'] == selected_item].copy()
        
        # Display top recommendation
        top_supplier = filtered_df.iloc[0]
        st.success(f"🏆 **Top Recommendation:** {top_supplier['SUPPLIER_NAME']} (Score: {top_supplier['OVERALL_SCORE']})")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Multi-metric Scatter/Bubble Chart
            # X: Lead Time (Lower is better)
            # Y: Reliability (Higher is better)
            # Size: Overall Score
            # Color: Supplier Name
            
            fig = px.scatter(
                filtered_df,
                x='AVG_LEAD_TIME_DAYS',
                y='RELIABILITY_SCORE',
                size='OVERALL_SCORE',
                color='SUPPLIER_NAME',
                hover_name='SUPPLIER_NAME',
                text='SUPPLIER_NAME',
                title=f"Supplier Performance Matrix: {selected_item}",
                labels={
                    'AVG_LEAD_TIME_DAYS': 'Avg Lead Time (Days) - Lower is Better',
                    'RELIABILITY_SCORE': 'Reliability Score (%) - Higher is Better',
                    'OVERALL_SCORE': 'Overall Rating'
                },
                template="plotly_white",
                height=500
            )
            
            # Update markers to be more visible
            fig.update_traces(textposition='top center', marker=dict(line=dict(width=2, color='DarkSlateGrey')))
            
            # Add quadrants or reference lines
            fig.add_hline(y=filtered_df['RELIABILITY_SCORE'].mean(), line_dash="dot", annotation_text="Avg Reliability")
            fig.add_vline(x=filtered_df['AVG_LEAD_TIME_DAYS'].mean(), line_dash="dot", annotation_text="Avg Lead Time")
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("#### Comparison Details")
            # Show a simplified table
            display_df = filtered_df[['SUPPLIER_NAME', 'UNIT_PRICE', 'AVG_LEAD_TIME_DAYS', 'RELIABILITY_SCORE', 'OVERALL_SCORE']].copy()
            st.dataframe(
                display_df.style.background_gradient(subset=['OVERALL_SCORE'], cmap="BuGn"),
                use_container_width=True,
                hide_index=True
            )
            st.info("💡 **Overall Score** is weighted: 50% Reliability, 30% Lead Time, 20% Price.")
