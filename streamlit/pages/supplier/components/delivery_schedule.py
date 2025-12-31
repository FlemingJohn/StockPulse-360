def render_delivery_schedule():
    """Render Delivery Schedule tab with Timeline."""
    from utils import load_delivery_schedule
    import plotly.express as px
    import pandas as pd
    
    st.markdown("### 📅 Logistics Timeline")
    st.markdown("Track incoming shipments and expected arrival windows.")
    
    df = load_delivery_schedule()
    
    if df.empty:
        st.info("No scheduled deliveries found.")
        return

    # Metrics Summary
    today_count = len(df[df['DELIVERY_TIMEFRAME'] == 'TODAY'])
    week_count = len(df[df['DELIVERY_TIMEFRAME'] != 'LATER'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Due Today", today_count)
    m2.metric("Due This Week", week_count)
    m3.metric("Total Pending", len(df))
    
    # Timeline Chart
    st.markdown("#### Shipment Gantt Chart")
    
    # Prepare data for timeline
    timeline_df = df.copy()
    timeline_df['ORDER_DATE'] = pd.to_datetime(timeline_df['ORDER_DATE'])
    timeline_df['EXPECTED_DELIVERY_DATE'] = pd.to_datetime(timeline_df['EXPECTED_DELIVERY_DATE'])
    
    # Create a descriptive task name
    timeline_df['SHIPMENT'] = timeline_df['ITEM'] + " (" + timeline_df['LOCATION'] + ")"
    
    fig = px.timeline(
        timeline_df,
        start="ORDER_DATE",
        end="EXPECTED_DELIVERY_DATE",
        y="SHIPMENT",
        color="ORDER_PRIORITY",
        hover_data=['SUPPLIER_NAME', 'ORDER_QUANTITY', 'TOTAL_COST'],
        title="Delivery Windows by Item & Location",
        color_discrete_map={
            'URGENT': '#DC143C',
            'NORMAL': '#29B5E8',
            'PLANNED': '#32CD32'
        },
        template="plotly_white",
        height=500
    )
    
    fig.update_yaxes(autorange="reversed")  # Latest on top
    fig.update_layout(xaxis_title="Date Range", yaxis_title="Shipment Detail")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detail Table
    st.markdown("#### Delivery Details")
    st.dataframe(
        df[['EXPECTED_DELIVERY_DATE', 'ITEM', 'LOCATION', 'SUPPLIER_NAME', 'ORDER_QUANTITY', 'ORDER_PRIORITY', 'DELIVERY_TIMEFRAME']],
        use_container_width=True,
        hide_index=True
    )
