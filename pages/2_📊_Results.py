"""
Results Page - Display analysis results and statistics
"""

import streamlit as st
from pathlib import Path
import pandas as pd
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from streamlit_utils.session_state import init_session_state

# Initialize session state
init_session_state()

# Page configuration
st.set_page_config(
    page_title="Results - Bird Sound Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analysis Results")
st.markdown("View and explore your bird sound analysis results")
st.markdown("---")

# Check if analysis has been completed
if not st.session_state.get("analysis_complete", False):
    st.warning("⚠️ No analysis results available yet")
    st.info("Please run an analysis from the Analysis page first")
    
    if st.button("🎵 Go to Analysis Page"):
        st.switch_page("pages/1_🎵_Analysis.py")
    
    st.stop()

# Load results
results_df = st.session_state.get("current_results_df")
enriched_csv_path = st.session_state.get("enriched_csv_path")
joypy_plot_path = st.session_state.get("joypy_plot_path")

if results_df is None and enriched_csv_path:
    # Try to load from CSV
    try:
        results_df = pd.read_csv(enriched_csv_path, sep=";")
        st.session_state.current_results_df = results_df
    except Exception as e:
        st.error(f"Failed to load results: {e}")
        st.stop()

if results_df is None:
    st.error("No results data available")
    st.stop()

# Summary Statistics
st.subheader("📈 Summary Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Detections",
        len(results_df),
        help="Total number of bird sound detections"
    )

with col2:
    unique_species = results_df['scientific_name'].nunique()
    st.metric(
        "Unique Species",
        unique_species,
        help="Number of different species detected"
    )

with col3:
    avg_confidence = results_df['confidence'].mean()
    st.metric(
        "Average Confidence",
        f"{avg_confidence:.2%}",
        help="Mean detection confidence across all detections"
    )

with col4:
    if 'file_path' in results_df.columns:
        files_analyzed = results_df['file_path'].nunique()
    else:
        files_analyzed = "N/A"
    st.metric(
        "Files Analyzed",
        files_analyzed,
        help="Number of audio files processed"
    )

st.markdown("---")

# Display options
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("🔍 Detection Details")

with col2:
    # Filters
    with st.expander("🎛️ Filters"):
        # Confidence filter
        min_confidence = st.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05
        )
        
        # Species filter
        all_species = ["All"] + sorted(results_df['scientific_name'].unique().tolist())
        selected_species = st.selectbox(
            "Species",
            options=all_species,
            index=0
        )
        
        # Norwegian name filter
        if 'Species_NorwegianName' in results_df.columns:
            nor_names = results_df['Species_NorwegianName'].dropna().unique()
            if len(nor_names) > 0:
                all_nor_names = ["All"] + sorted(nor_names.tolist())
                selected_nor_name = st.selectbox(
                    "Norwegian Name",
                    options=all_nor_names,
                    index=0
                )
            else:
                selected_nor_name = "All"
        else:
            selected_nor_name = "All"

# Apply filters
filtered_df = results_df.copy()

if min_confidence > 0:
    filtered_df = filtered_df[filtered_df['confidence'] >= min_confidence]

if selected_species != "All":
    filtered_df = filtered_df[filtered_df['scientific_name'] == selected_species]

if selected_nor_name != "All":
    filtered_df = filtered_df[filtered_df['Species_NorwegianName'] == selected_nor_name]

# Display filtered results
st.info(f"Showing {len(filtered_df)} of {len(results_df)} detections")

# Configure display columns
display_columns = [
    'scientific_name',
    'confidence',
    'start_time',
    'end_time'
]

# Add optional columns if they exist
optional_columns = [
    'Species_NorwegianName',
    'Family_ScientificName',
    'Order_ScientificName',
    'Redlist_Status',
    'file_path'
]

for col in optional_columns:
    if col in filtered_df.columns:
        display_columns.append(col)

# Column configuration for better display
column_config = {
    'scientific_name': st.column_config.TextColumn("Scientific Name", width="medium"),
    'confidence': st.column_config.ProgressColumn("Confidence", format="%.2f", min_value=0, max_value=1),
    'start_time': st.column_config.NumberColumn("Start (s)", format="%.1f"),
    'end_time': st.column_config.NumberColumn("End (s)", format="%.1f"),
    'Species_NorwegianName': st.column_config.TextColumn("Norwegian Name", width="medium"),
    'Family_ScientificName': st.column_config.TextColumn("Family", width="small"),
    'Order_ScientificName': st.column_config.TextColumn("Order", width="small"),
    'Redlist_Status': st.column_config.TextColumn("Red List", width="small"),
    'file_path': st.column_config.TextColumn("Audio File", width="large")
}

# Display dataframe
st.dataframe(
    filtered_df[display_columns],
    column_config=column_config,
    use_container_width=True,
    height=400
)

# Export options
st.markdown("---")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💾 Export Options")
    
    # CSV download
    csv = filtered_df.to_csv(index=False, sep=";")
    st.download_button(
        label="📥 Download Filtered Results (CSV)",
        data=csv,
        file_name=f"bird_detections_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    if enriched_csv_path and Path(enriched_csv_path).exists():
        with open(enriched_csv_path, 'rb') as f:
            st.download_button(
                label="📥 Download Full Results (CSV)",
                data=f.read(),
                file_name=f"bird_detections_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

with col2:
    st.subheader("📊 Visualizations")
    
    # Display Joypy plot if available
    if joypy_plot_path and Path(joypy_plot_path).exists():
        st.image(
            str(joypy_plot_path),
            caption="Bird Detection Activity Throughout the Day",
            use_column_width=True
        )
        
        # Download button for plot
        with open(joypy_plot_path, 'rb') as f:
            st.download_button(
                label="📥 Download Activity Plot",
                data=f.read(),
                file_name="bird_activity_plot.png",
                mime="image/png"
            )
    else:
        st.info("Activity plot not available")

# Additional statistics
st.markdown("---")
st.subheader("📊 Species Statistics")

# Species summary
species_summary = filtered_df.groupby('scientific_name').agg({
    'confidence': ['count', 'mean', 'std', 'min', 'max']
}).round(3)

species_summary.columns = ['Count', 'Mean Conf.', 'Std Dev', 'Min Conf.', 'Max Conf.']
species_summary = species_summary.sort_values('Count', ascending=False)

# Add Norwegian names if available
if 'Species_NorwegianName' in filtered_df.columns:
    nor_names_map = filtered_df.groupby('scientific_name')['Species_NorwegianName'].first()
    species_summary['Norwegian Name'] = species_summary.index.map(nor_names_map)
    
    # Reorder columns
    cols = ['Norwegian Name', 'Count', 'Mean Conf.', 'Std Dev', 'Min Conf.', 'Max Conf.']
    species_summary = species_summary[cols]

st.dataframe(
    species_summary,
    use_container_width=True,
    height=min(400, len(species_summary) * 35 + 50)
)

# Red List Status Summary (if available)
if 'Redlist_Status' in filtered_df.columns:
    st.markdown("---")
    st.subheader("🚨 Conservation Status Summary")
    
    redlist_summary = filtered_df['Redlist_Status'].value_counts()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(
            redlist_summary,
            use_container_width=True
        )
    
    with col2:
        # Create a pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = {
            'LC': '#28a745',  # Green
            'NT': '#ffc107',  # Yellow
            'VU': '#fd7e14',  # Orange
            'EN': '#dc3545',  # Red
            'CR': '#6f42c1',  # Purple
            'DD': '#6c757d',  # Gray
            'NE': '#adb5bd'   # Light gray
        }
        
        plot_colors = [colors.get(status, '#000000') for status in redlist_summary.index]
        
        ax.pie(redlist_summary.values, 
               labels=redlist_summary.index, 
               autopct='%1.1f%%',
               colors=plot_colors)
        ax.set_title("Red List Status Distribution")
        st.pyplot(fig)

# Time-based analysis
if 'start_time' in filtered_df.columns:
    st.markdown("---")
    st.subheader("⏰ Temporal Patterns")
    
    # Extract hour from filename if possible
    if 'file_path' in filtered_df.columns:
        # Try to extract time from filename
        try:
            # This is a simplified approach - adjust based on your filename format
            filtered_df['detection_hour'] = pd.to_datetime(
                filtered_df['file_path'].str.extract(r'(\d{6})', expand=False),
                format='%H%M%S',
                errors='coerce'
            ).dt.hour
            
            if not filtered_df['detection_hour'].isna().all():
                # Create hourly distribution
                hourly_counts = filtered_df['detection_hour'].value_counts().sort_index()
                
                fig, ax = plt.subplots(figsize=(12, 6))
                hourly_counts.plot(kind='bar', ax=ax)
                ax.set_xlabel("Hour of Day")
                ax.set_ylabel("Number of Detections")
                ax.set_title("Detections by Hour of Day")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
        except Exception as e:
            st.info("Could not extract temporal patterns from filenames")