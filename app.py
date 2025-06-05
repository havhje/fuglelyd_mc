"""
Bird Sound Analysis Tool - Streamlit App
Main entry point for the Streamlit web application
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="Bird Sound Analysis Tool",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "analysis_running" not in st.session_state:
    st.session_state.analysis_running = False
    st.session_state.analysis_progress = 0.0
    st.session_state.analysis_status = ""
    st.session_state.cancel_requested = False
    st.session_state.current_results_df = None
    st.session_state.analysis_complete = False
    st.session_state.output_directory = None
    st.session_state.input_directory = None
    st.session_state.analysis_params = {}
    st.session_state.enriched_csv_path = None
    st.session_state.joypy_plot_path = None

# Main page
st.title("🐦 Bird Sound Analysis Tool")
st.markdown("---")

# Sidebar navigation info
with st.sidebar:
    st.markdown("## Navigation")
    st.markdown("""
    Use the sidebar to navigate between pages:
    
    - **🎵 Analysis**: Configure and run analysis
    - **📊 Results**: View analysis results
    - **🔊 Audio Explorer**: Listen to detected bird sounds
    - **⚙️ Settings**: Configure analysis parameters
    - **ℹ️ About**: Documentation and help
    """)
    
    # Status indicator
    if st.session_state.analysis_running:
        st.markdown("---")
        st.markdown("### 🔄 Analysis Status")
        st.progress(st.session_state.analysis_progress)
        st.caption(st.session_state.analysis_status)

# Main content
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    ## Welcome to the Bird Sound Analysis Tool
    
    This tool uses **BirdNET** to detect and identify bird species from audio recordings,
    enriches the results with Norwegian taxonomic data from **Artskart API**, and provides
    comprehensive temporal analysis of bird activity patterns.
    
    ### 🚀 Getting Started
    
    1. Navigate to the **Analysis** page to configure your analysis
    2. Select your audio files directory
    3. Choose analysis mode (location-based or species list)
    4. Start the analysis and monitor progress
    5. View results, statistics, and listen to detected bird sounds
    
    ### 🎯 Key Features
    
    - **Automated Bird Detection**: Uses BirdNET AI for accurate species identification
    - **Norwegian Taxonomic Data**: Enriches detections with local species information
    - **Temporal Analysis**: Analyzes bird activity patterns throughout the day
    - **Audio Segmentation**: Splits recordings into species-specific clips
    - **Interactive Results**: Browse, filter, and export your findings
    - **Audio Playback**: Listen to detected bird sounds directly in your browser
    
    ### 📁 Output Structure
    
    The analysis creates the following output structure:
    ```
    output_dir/
    ├── interim/
    │   └── enriched_detections.csv
    ├── lydfiler/
    │   └── [species folders with audio segments]
    └── figur/
        └── bird_detection_joypy_plot.png
    ```
    
    Use the navigation menu on the left to begin your analysis! 👈
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Powered by BirdNET and Artskart API | Built with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True,
)