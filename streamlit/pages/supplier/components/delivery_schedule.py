def render_delivery_schedule():
    """Render Delivery Schedule tab with Interactive Calendar."""
    from utils import load_delivery_schedule
    import pandas as pd
    import streamlit as st
    import datetime
    import random
    from datetime import timedelta
    import numpy as np
    
    # Try importing calendar
    try:
        from streamlit_calendar import calendar
        HAS_CALENDAR = True
        st.toast("Calendar Library Loaded Successfully! ✅", icon="🎉")
    except Exception as e:
        HAS_CALENDAR = False
        import sys
        import traceback
        st.error(f"❌ Critical Error Loading Calendar: {e}")
        st.code(traceback.format_exc())
        st.info(f"Current Python: {sys.executable}")
    
    if HAS_CALENDAR:
        st.markdown("### Interactive Delivery Calendar")
        st.markdown("Monitor upcoming shipments in a monthly, weekly, or list view.")
    else:
        st.markdown("### Delivery Schedule (Chart View)")
        st.markdown("Track incoming shipments and expected arrival windows.")
    
    # Load data
    df = load_delivery_schedule()
    
    if df.empty:
        st.warning("No scheduled deliveries found in the system.")
        return

    # ---------------------------------------------------------
    # Data Pre-processing (Fix Date Formats)
    # ---------------------------------------------------------
    def smart_to_datetime(series):
        # Handle string-encoded numbers (e.g. "1600000000") by converting to numeric first
        if series.dtype == 'object':
            try:
                numeric_series = pd.to_numeric(series, errors='coerce')
                # If we successfully converted most values, use the numeric series
                if numeric_series.notna().mean() > 0.5: 
                    series = numeric_series
            except:
                pass

        if pd.api.types.is_numeric_dtype(series):
            # Check magnitude to infer unit (ns, us, ms, s)
            sample = series.dropna()
            if sample.empty: return pd.to_datetime(series)
            mean_val = sample.mean()
            if mean_val > 1e16: return pd.to_datetime(series, unit='ns')
            if mean_val > 1e13: return pd.to_datetime(series, unit='us')
            if mean_val > 1e10: return pd.to_datetime(series, unit='ms')
            return pd.to_datetime(series, unit='s')
        
        return pd.to_datetime(series, errors='coerce')

    try:
        if 'ORDER_DATE' in df.columns:
            df['ORDER_DATE'] = smart_to_datetime(df['ORDER_DATE'])
        if 'EXPECTED_DELIVERY_DATE' in df.columns:
            df['EXPECTED_DELIVERY_DATE'] = smart_to_datetime(df['EXPECTED_DELIVERY_DATE'])
    except Exception as e:
        st.error(f"Error parsing dates: {e}")

    # ---------------------------------------------------------
    # Synthetic Data Injection (Extend to Jan 5, 2026)
    # ---------------------------------------------------------
    try:
        # Configuration for synthetic data
        locs = ['Chennai', 'Mumbai', 'Delhi', 'Bangalore']
        items = ['Paracetamol', 'Insulin', 'Bandages', 'Syringes', 'Gloves']
        suppliers = ['MedSupply Co.', 'PharmaDirect', 'QuickMeds Ltd']
        cutoff_date = pd.to_datetime('2026-01-05')
        
        max_date = pd.to_datetime(df['EXPECTED_DELIVERY_DATE']).max() if not df.empty else pd.Timestamp.now()
        
        if max_date < cutoff_date:
            st.toast("Injecting synthetic future data for visualization...", icon="🧪")
            
            new_rows = []
            days_to_add = (cutoff_date - max_date).days
            
            # Start from tomorrow or max_date + 1
            start_gen_date = max_date + timedelta(days=1)
            
            for i in range(days_to_add + 1):
                current_day = start_gen_date + timedelta(days=i)
                
                # Generate 2-5 orders per day
                num_orders = random.randint(2, 5)
                for _ in range(num_orders):
                    new_rows.append({
                        'ORDER_DATE': (current_day - timedelta(days=random.randint(1, 7))),
                        'EXPECTED_DELIVERY_DATE': current_day,
                        'ITEM': random.choice(items),
                        'LOCATION': random.choice(locs),
                        'SUPPLIER_NAME': random.choice(suppliers),
                        'ORDER_QUANTITY': random.randint(50, 500),
                        'ORDER_PRIORITY': random.choice(['NORMAL', 'PLANNED', 'URGENT']),
                        'TOTAL_COST': random.randint(1000, 50000)
                    })
            
            if new_rows:
                synthetic_df = pd.DataFrame(new_rows)
                df = pd.concat([df, synthetic_df], ignore_index=True)

    except Exception as e:
        st.warning(f"Could not inject synthetic data: {e}")

    # Debug / Raw Data
    with st.expander("View Raw Delivery Data Table"):
        st.dataframe(
            df[['EXPECTED_DELIVERY_DATE', 'ITEM', 'LOCATION', 'SUPPLIER_NAME', 'ORDER_QUANTITY', 'ORDER_PRIORITY']],
            use_container_width=True,
            hide_index=True
        )
        st.write("Data Types:", df.dtypes)
        st.write("Raw Date Samples:", df[['ORDER_DATE', 'EXPECTED_DELIVERY_DATE']].head())

    # ---------------------------------------------------------
    # Render Strategy
    # ---------------------------------------------------------
    
    if HAS_CALENDAR:
        # DATA PROCESSING FOR CALENDAR
        events = []
        priority_colors = {
            'URGENT': '#DC143C',
            'NORMAL': '#29B5E8',
            'PLANNED': '#32CD32'
        }
        
        try:
            for _, row in df.iterrows():
                start_date = pd.to_datetime(row['ORDER_DATE']).strftime('%Y-%m-%d')
                end_date = pd.to_datetime(row['EXPECTED_DELIVERY_DATE']).strftime('%Y-%m-%d')
                
                title = f"{row['ITEM']} ({row['LOCATION']})"
                details = f"Supplier: {row['SUPPLIER_NAME']} | Qty: {row['ORDER_QUANTITY']}"
                
                event = {
                    "title": title,
                    "start": start_date,
                    "end": end_date,
                    "backgroundColor": priority_colors.get(row['ORDER_PRIORITY'], '#808080'),
                    "borderColor": priority_colors.get(row['ORDER_PRIORITY'], '#808080'),
                    "extendedProps": {
                        "description": details,
                        "supplier": row['SUPPLIER_NAME']
                    }
                }
                events.append(event)
                
            calendar_options = {
                "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"},
                "initialView": "dayGridMonth",
                "height": 650
            }
            
            with st.spinner("Loading Calendar..."):
                st.write(f"DEBUG: Rendering {len(events)} events")
                calendar(events=events, options=calendar_options)
                
            # Legend
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"🔴 **Urgent**: {len(df[df['ORDER_PRIORITY'] == 'URGENT'])}")
            c2.markdown(f"🔵 **Normal**: {len(df[df['ORDER_PRIORITY'] == 'NORMAL'])}")
            c3.markdown(f"🟢 **Planned**: {len(df[df['ORDER_PRIORITY'] == 'PLANNED'])}")
            
        except Exception as e:
            st.error(f"Error rendering calendar: {e}")
            HAS_CALENDAR = False # Trigger fallback if calculation fails

    if not HAS_CALENDAR:
        # FALLBACK: ALTAIR GANTT CHART
        import altair as alt
        
        # Data Processing for Altair
        timeline_df = df.copy()
        timeline_df['shipment_label'] = timeline_df['ITEM'] + " (" + timeline_df['LOCATION'] + ")"
        
        try:
            # Dates are already processed above
            chart = alt.Chart(timeline_df).mark_bar().encode(
                x=alt.X('ORDER_DATE:T', title='Order Date'),
                x2=alt.X2('EXPECTED_DELIVERY_DATE:T', title='Delivery Date'),
                y=alt.Y('shipment_label', title='Shipment', sort='x'),
                color=alt.Color('ORDER_PRIORITY', 
                              scale=alt.Scale(domain=['URGENT', 'NORMAL', 'PLANNED'], 
                                            range=['#DC143C', '#29B5E8', '#32CD32']),
                              legend=alt.Legend(title="Priority")),
                tooltip=['SUPPLIER_NAME', 'ORDER_QUANTITY']
            ).properties(
                height=max(400, len(timeline_df) * 20),
                title="Delivery Schedule (Gantt View)"
            ).interactive()

            st.altair_chart(chart, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error rendering fallback chart: {e}")
