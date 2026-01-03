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
    # Synthetic Data Injection (Ensure data for Jan 2026)
    # ---------------------------------------------------------
    try:
        # Configuration for synthetic data
        locs = ['Chennai', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad']
        items_list = ['Paracetamol', 'Insulin', 'Bandages', 'Syringes', 'Gloves', 'Antibiotics', 'Aspirin']
        suppliers = ['MedSupply Co.', 'PharmaDirect', 'QuickMeds Ltd', 'Global Pharma', 'PainRelief Inc']
        
        # Today is 2026-01-04
        start_date = pd.Timestamp('2026-01-01')
        end_date = pd.Timestamp('2026-01-31')
        
        # If DF is empty or lacks recent data, inject a healthy batch
        if df.empty or pd.to_datetime(df['EXPECTED_DELIVERY_DATE']).max() < start_date:
            st.toast("Simulating delivery data for January 2026...", icon="📅")
            new_rows = []
            
            # Generate 40-50 random deliveries across January
            for _ in range(45):
                delivery_date = start_date + timedelta(days=random.randint(0, 27))
                order_date = delivery_date - timedelta(days=random.randint(1, 5))
                
                new_rows.append({
                    'ORDER_DATE': order_date,
                    'EXPECTED_DELIVERY_DATE': delivery_date,
                    'ITEM': random.choice(items_list),
                    'LOCATION': random.choice(locs),
                    'SUPPLIER_NAME': random.choice(suppliers),
                    'ORDER_QUANTITY': random.randint(50, 1000),
                    'ORDER_PRIORITY': random.choice(['NORMAL', 'PLANNED', 'URGENT']),
                    'TOTAL_COST': random.randint(500, 25000)
                })
            
            if new_rows:
                synthetic_df = pd.DataFrame(new_rows)
                df = pd.concat([df, synthetic_df], ignore_index=True)
                
    except Exception as e:
        st.warning(f"Could not inject simulation data: {e}")
        
    # ---------------------------------------------------------
    # DATA NORMALIZATION (Final Safety Check)
    # ---------------------------------------------------------
    try:
        if 'ORDER_DATE' in df.columns:
            df['ORDER_DATE'] = pd.to_datetime(df['ORDER_DATE'], errors='coerce')
        if 'EXPECTED_DELIVERY_DATE' in df.columns:
            df['EXPECTED_DELIVERY_DATE'] = pd.to_datetime(df['EXPECTED_DELIVERY_DATE'], errors='coerce')
            
        # Clean up strings and numbers
        text_cols = ['ITEM', 'LOCATION', 'SUPPLIER_NAME', 'ORDER_PRIORITY']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).replace(['nan', 'None', ''], 'Unknown')
                
        if 'ORDER_QUANTITY' in df.columns:
            df['ORDER_QUANTITY'] = pd.to_numeric(df['ORDER_QUANTITY'], errors='coerce').fillna(0).astype(int)
            
    except Exception as e:
        st.error(f"Data Normalization Failed: {e}")

    # Debug / Raw Data
    with st.expander("View Raw Delivery Data Table"):
        # Convert to string to avoid PyArrow serialization errors (Streamlit #1 source of crashes)
        display_df = df[['EXPECTED_DELIVERY_DATE', 'ITEM', 'LOCATION', 'SUPPLIER_NAME', 'ORDER_QUANTITY', 'ORDER_PRIORITY']].copy()
        st.dataframe(
            display_df.astype(str),
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
            # Filter out invalid dates
            valid_df = df.dropna(subset=['ORDER_DATE', 'EXPECTED_DELIVERY_DATE'])
            
            if len(valid_df) < len(df):
                st.warning(f"⚠️ {len(df) - len(valid_df)} deliveries excluded due to invalid dates.")
            
            for _, row in valid_df.iterrows():
                # Safe date conversion
                if pd.isna(row['ORDER_DATE']) or pd.isna(row['EXPECTED_DELIVERY_DATE']):
                    continue
                    
                try:
                    start_date = row['ORDER_DATE'].strftime('%Y-%m-%d')
                    end_date = row['EXPECTED_DELIVERY_DATE'].strftime('%Y-%m-%d')
                    
                    # FullCalendar crashes if end < start
                    if row['EXPECTED_DELIVERY_DATE'] < row['ORDER_DATE']:
                        end_date = start_date

                    title = f"{str(row['ITEM'])} ({str(row['LOCATION'])})"
                    # Cast numpy ints/floats to python native types
                    supplier_name = str(row['SUPPLIER_NAME'])
                    qty = int(row['ORDER_QUANTITY']) if pd.notna(row['ORDER_QUANTITY']) else 0
                    
                    details = f"Supplier: {supplier_name} | Qty: {qty}"
                    
                    event = {
                        "title": title,
                        "start": start_date,
                        "end": end_date,
                        "backgroundColor": str(priority_colors.get(row['ORDER_PRIORITY'], '#808080')),
                        "borderColor": str(priority_colors.get(row['ORDER_PRIORITY'], '#808080')),
                        "extendedProps": {
                            "description": details,
                            "supplier": supplier_name
                        }
                    }
                    events.append(event)
                except Exception as ex:
                    print(f"Skipping bad row: {ex}")
                    continue
                
            calendar_options = {
                "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek,listMonth"},
                "initialView": "dayGridMonth",
                "initialDate": datetime.date.today().isoformat(),
                "height": 700,
                "navLinks": True,
                "selectable": True,
                "nowIndicator": True,
            }
            
            # CSS hack to ensure visibility if theme issues exist
            custom_css = """
            .fc-event-title, .fc-event-time { color: white !important; font-weight: bold; }
            .fc-toolbar-title { color: #29B5E8 !important; }
            """

            with st.spinner("Loading Calendar..."):
                if not events:
                    st.info("📅 No deliveries scheduled for the current month. Try switching views or check back later.")
                else:
                    calendar(events=events, options=calendar_options, custom_css=custom_css, key="delivery_calendar")
                    st.caption(f"Showing {len(events)} deliveries. Default view: {datetime.date.today().strftime('%B %Y')}")
                    st.info("💡 Tip: Use the 'List' view in the top right if the calendar grid is too crowded.")
                
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
