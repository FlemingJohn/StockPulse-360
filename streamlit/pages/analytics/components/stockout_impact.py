"""Analytics - Stockout Impact Component"""
import streamlit as st
import plotly.express as px
from utils import load_stockout_impact

def render_stockout_impact():
    """Render Stockout Impact Analysis tab."""
    st.markdown("### Stockout Impact Analysis")
    st.markdown("Quantify the patient/beneficiary impact of stock-outs")
    
    impact_data = load_stockout_impact()
    
    if not impact_data.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            total_affected = impact_data['PATIENTS_AFFECTED_UNTIL_STOCKOUT'].sum()
            st.metric("Total Patients Affected", f"{total_affected:,.0f}")
        with col2:
            critical_items = len(impact_data[impact_data['IMPACT_SEVERITY'].isin(['LIFE_THREATENING', 'HIGH_SEVERITY'])])
            st.metric("Critical Items", critical_items)
        with col3:
            avg_priority = impact_data['ACTION_PRIORITY'].mean()
            st.metric("Avg Action Priority", f"{avg_priority:.1f}")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(
                impact_data.sort_values('ACTION_PRIORITY'),
                x='ITEM', y='PATIENTS_AFFECTED_UNTIL_STOCKOUT',
                color='IMPACT_SEVERITY', facet_col='LOCATION',
                title="Patient Impact by Item and Location",
                labels={'PATIENTS_AFFECTED_UNTIL_STOCKOUT': 'Patients Affected', 'ITEM': 'Item'},
                color_discrete_map={
                    'LIFE_THREATENING': '#8B0000', 'HIGH_SEVERITY': '#DC143C',
                    'MODERATE_SEVERITY': '#FFA500', 'LOW_SEVERITY': '#FFD700'
                }
            )
            fig.update_layout(height=400, font=dict(family="Segoe UI, sans-serif", color="#0F4C81"), plot_bgcolor='#FFFFFF')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            severity_counts = impact_data['IMPACT_SEVERITY'].value_counts()
            fig2 = px.pie(
                values=severity_counts.values, names=severity_counts.index,
                title="Impact Severity Distribution", color=severity_counts.index,
                color_discrete_map={
                    'LIFE_THREATENING': '#8B0000', 'HIGH_SEVERITY': '#DC143C',
                    'MODERATE_SEVERITY': '#FFA500', 'LOW_SEVERITY': '#FFD700'
                }
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("#### Priority Action Items")
        st.dataframe(
            impact_data[['LOCATION', 'ITEM', 'STOCK_STATUS', 'PATIENTS_AFFECTED_UNTIL_STOCKOUT', 
                        'IMPACT_SEVERITY', 'ACTION_PRIORITY', 'ABC_CATEGORY']].sort_values('ACTION_PRIORITY').astype(str),
            use_container_width=True, height=300
        )
    else:
        st.info("🔧 Stockout impact view not found. Run `python/create_advanced_views.py` to create it.")
