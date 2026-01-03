"""
Data Management Page
Allows users to upload CSV stock data directly to the database.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def render_data_management_page():
    """Render Data Management page."""
    
    st.markdown("### Data Management")
    st.markdown("Upload new stock data via CSV. The file must match the required schema.")
    
    # Required Schema
    REQUIRED_COLUMNS = [
        'LOCATION', 'ITEM', 'CURRENT_STOCK', 
        'ISSUED_QTY', 'RECEIVED_QTY', 'LAST_UPDATED_DATE'
    ]
    
    # Template Download
    st.markdown("#### 1. Download Template")
    template_data = {col: [] for col in REQUIRED_COLUMNS}
    template_df = pd.DataFrame(template_data)
    csv_template = template_df.to_csv(index=False)
    
    st.download_button(
        label="Download CSV Template",
        data=csv_template,
        file_name="stock_upload_template.csv",
        mime="text/csv"
    )
    
    # File Uploader
    st.markdown("#### 2. Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Read CSV
            df = pd.read_csv(uploaded_file)
            
            # Normalize column names to uppercase
            df.columns = [c.upper().strip() for c in df.columns]
            
            # Validate Schema
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
            
            if missing_cols:
                st.error(f"Invalid Schema. Missing columns: {', '.join(missing_cols)}")
                st.info(f"Required columns: {', '.join(REQUIRED_COLUMNS)}")
                return
            
            # Show Preview
            st.markdown("#### Preview")
            st.dataframe(df.head(), use_container_width=True)
            st.write(f"Total Rows: {len(df)}")
            
            # Upload Button
            if st.button("Upload to Database"):
                session = st.session_state.get('session')
                if not session:
                    st.error("Database session not found.")
                    return
                
                with st.spinner("Uploading data..."):
                    # Ensure date column is formatted correctly
                    if 'LAST_UPDATED_DATE' in df.columns:
                        df['LAST_UPDATED_DATE'] = pd.to_datetime(df['LAST_UPDATED_DATE']).dt.date
                    
                    # Fix SQL Error: Table has 7 columns (including CREATED_AT), but CSV has 6.
                    # Explicitly add CREATED_AT to match the schema.
                    df['CREATED_AT'] = datetime.now()
                    
                    # Write to Snowflake
                    # Using write_pandas is standard, but sometimes requires extra setup.
                    # Since we have an active session, we can try creating a dataframe and writing it.
                    try:
                        snowpark_df = session.create_dataframe(df)
                        snowpark_df.write.mode("append").save_as_table("RAW_STOCK")
                        st.success(f"Successfully uploaded {len(df)} records to RAW_STOCK.")
                    except Exception as e:
                        st.error(f"Upload failed: {str(e)}")
                        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
