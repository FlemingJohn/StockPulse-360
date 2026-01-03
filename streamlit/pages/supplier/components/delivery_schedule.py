def render_delivery_schedule():
    """Render Delivery Schedule using Native Streamlit Grid (No External Libraries)."""
    from utils import load_delivery_schedule
    import pandas as pd
    import streamlit as st
    import datetime
    from datetime import timedelta
    import random
    import numpy as np

    st.markdown("### Delivery Schedule (Native View)")
    st.markdown("Monitor upcoming shipments in a robust, real-time grid view.")

    # 1. Load data
    df = load_delivery_schedule()

    # ---------------------------------------------------------
    # 2. Data Simulation (Ensure January 2026 is populated)
    # ---------------------------------------------------------
    try:
        # Configuration for simulation
        locs = ['Chennai', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad']
        items_list = ['Paracetamol', 'Insulin', 'Bandages', 'Syringes', 'Gloves', 'Antibiotics', 'Aspirin']
        suppliers = ['MedSupply Co.', 'PharmaDirect', 'QuickMeds Ltd', 'Global Pharma', 'PainRelief Inc']
        
        # We are simulating for Jan 2026
        target_month = 1
        target_year = 2026
        
        # Check if we have data for this month
        recent_data = False
        if not df.empty:
            df['EXPECTED_DELIVERY_DATE'] = pd.to_datetime(df['EXPECTED_DELIVERY_DATE'], errors='coerce')
            jan_data = df[(df['EXPECTED_DELIVERY_DATE'].dt.month == target_month) & 
                          (df['EXPECTED_DELIVERY_DATE'].dt.year == target_year)]
            if not jan_data.empty:
                recent_data = True

        if not recent_data:
            st.toast("Generating delivery schedule simulation...", icon="⚡")
            new_rows = []
            for _ in range(35):
                day = random.randint(1, 31)
                delivery_date = datetime.date(target_year, target_month, day)
                order_date = delivery_date - timedelta(days=random.randint(1, 5))
                
                new_rows.append({
                    'ORDER_DATE': order_date,
                    'EXPECTED_DELIVERY_DATE': delivery_date,
                    'ITEM': random.choice(items_list),
                    'LOCATION': random.choice(locs),
                    'SUPPLIER_NAME': random.choice(suppliers),
                    'ORDER_QUANTITY': random.randint(100, 2000),
                    'ORDER_PRIORITY': random.choice(['NORMAL', 'PLANNED', 'URGENT']),
                    'TOTAL_COST': random.randint(5000, 50000)
                })
            
            sim_df = pd.DataFrame(new_rows)
            df = pd.concat([df, sim_df], ignore_index=True)
            
    except Exception as e:
        st.warning(f"Note: Simulation data could not be merged: {e}")

    # 3. Final Data Normalization
    df['EXPECTED_DELIVERY_DATE'] = pd.to_datetime(df['EXPECTED_DELIVERY_DATE'], errors='coerce')
    df = df.dropna(subset=['EXPECTED_DELIVERY_DATE'])
    
    # ---------------------------------------------------------
    # 4. NATIVE CALENDAR RENDERING
    # ---------------------------------------------------------
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.markdown("#### Calendar Navigation")
        # Fixed view for Jan 2026 to match project context
        month_labels = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        st.info(f"Viewing: **January 2026**")
        st.write("---")
        st.markdown("""
        **Legend:**
        - <span style='color:#DC143C'>●</span> Urgent
        - <span style='color:#29B5E8'>●</span> Normal
        - <span style='color:#32CD32'>●</span> Planned
        """, unsafe_allow_html=True)

    with col2:
        # CSS for Native Calendar
        st.markdown("""
        <style>
        .calendar-header {
            font-weight: bold;
            text-align: center;
            background-color: #f0f2f6;
            padding: 5px;
            border-bottom: 2px solid #ddd;
        }
        .calendar-day {
            min-height: 120px;
            border: 1px solid #efefef;
            padding: 5px;
            background-color: white;
            position: relative;
        }
        .day-number {
            font-size: 0.8em;
            color: #999;
            margin-bottom: 5px;
            display: block;
        }
        .event-chip {
            font-size: 0.7em;
            padding: 2px 5px;
            margin-bottom: 2px;
            border-radius: 4px;
            color: white;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: pointer;
        }
        .urgent { background-color: #DC143C; }
        .normal { background-color: #29B5E8; }
        .planned { background-color: #32CD32; }
        </style>
        """, unsafe_allow_html=True)

        # Build Grid
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        grid_cols = st.columns(7)
        for i, day in enumerate(days):
            grid_cols[i].markdown(f"<div class='calendar-header'>{day}</div>", unsafe_allow_html=True)

        # January 2026 starts on Thursday (Index 3 in Mon=0)
        start_padding = 3
        current_day = 1
        
        # We need 5-6 rows
        for row in range(5):
            cols = st.columns(7)
            for col_idx in range(7):
                day_idx = row * 7 + col_idx
                
                if day_idx < start_padding or current_day > 31:
                    cols[col_idx].markdown("<div class='calendar-day' style='background-color:#fafafa;'></div>", unsafe_allow_html=True)
                else:
                    # Filter events for this day
                    day_events = df[df['EXPECTED_DELIVERY_DATE'].dt.day == current_day]
                    
                    event_html = ""
                    for _, event in day_events.head(3).iterrows():
                        p_class = event['ORDER_PRIORITY'].lower()
                        label = f"{event['ITEM']} ({event['LOCATION']})"
                        event_html += f"<div class='event-chip {p_class}' title='{event['SUPPLIER_NAME']} - Qty: {event['ORDER_QUANTITY']}'>{label}</div>"
                    
                    if len(day_events) > 3:
                        event_html += f"<div style='font-size:0.6em;color:#666;text-align:center;'>+ {len(day_events)-3} more</div>"

                    cols[col_idx].markdown(f"""
                    <div class='calendar-day'>
                        <span class='day-number'>{current_day}</span>
                        {event_html}
                    </div>
                    """, unsafe_allow_html=True)
                    current_day += 1

    st.markdown("---")
    with st.expander("View Full Delivery Schedule List"):
        st.dataframe(df.astype(str), use_container_width=True)
