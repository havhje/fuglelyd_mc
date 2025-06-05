"""
Analysis Page - Configure and run bird sound analysis
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from streamlit_utils.session_state import init_session_state, reset_analysis_state, update_analysis_params
from streamlit_utils.file_browser import directory_picker, get_audio_files
from streamlit_utils.progress_tracker import run_analysis_with_progress
from utils import setup_ffmpeg

# Initialize session state
init_session_state()

# Page configuration
st.set_page_config(
    page_title="Analysis - Bird Sound Analysis",
    page_icon="🎵",
    layout="wide"
)

# Setup FFmpeg
if not setup_ffmpeg():
    st.error("Failed to configure FFmpeg. Audio splitting may not work correctly.")

st.title("🎵 Bird Sound Analysis")
st.markdown("Configure and run analysis on your audio files")
st.markdown("---")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Input directory selection
    st.subheader("📁 Select Audio Files Directory")
    input_dir = directory_picker(
        "Input Directory",
        key="input_dir_picker",
        initial_path=st.session_state.get("input_directory", str(Path.home()))
    )
    
    if input_dir:
        st.session_state.input_directory = str(input_dir)
        audio_files = get_audio_files(input_dir)
        if audio_files:
            st.success(f"✅ Found {len(audio_files)} audio files")
            with st.expander("Show audio files"):
                for i, file in enumerate(audio_files[:10]):  # Show first 10
                    st.text(f"{i+1}. {file.name}")
                if len(audio_files) > 10:
                    st.text(f"... and {len(audio_files) - 10} more files")
    
    st.markdown("---")
    
    # Output directory selection
    st.subheader("💾 Select Output Directory")
    output_dir = directory_picker(
        "Output Directory",
        key="output_dir_picker",
        initial_path=st.session_state.get("output_directory", str(Path.home()))
    )
    
    if output_dir:
        st.session_state.output_directory = str(output_dir)
        st.info(f"Results will be saved to: {output_dir}")

with col2:
    st.subheader("⚙️ Analysis Parameters")
    
    # Analysis mode selection
    analysis_mode = st.radio(
        "Analysis Mode",
        options=["location", "species_list"],
        format_func=lambda x: "📍 Location-based" if x == "location" else "📋 Species list",
        key="analysis_mode_selector"
    )
    st.session_state.analysis_mode = analysis_mode
    
    # Parameters based on mode
    params = {}
    
    if analysis_mode == "location":
        st.markdown("#### Location Parameters")
        params['lat'] = st.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=59.91,
            step=0.01,
            help="Latitude for location-based species filtering"
        )
        
        params['lon'] = st.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=10.75,
            step=0.01,
            help="Longitude for location-based species filtering"
        )
        
        params['date'] = st.date_input(
            "Analysis Date",
            value=datetime.now().date(),
            help="Date for seasonal species adjustments"
        )
        
        params['custom_species_list_param'] = None
        
    else:  # species_list mode
        st.markdown("#### Species List")
        
        use_default = st.checkbox(
            "Use default species list",
            value=st.session_state.get("use_default_species_list", False),
            help="Use the project's default species list (data_input_artsliste/arter.txt)"
        )
        st.session_state.use_default_species_list = use_default
        
        if use_default:
            params['custom_species_list_param'] = True
            st.info("Using default species list from data_input_artsliste/arter.txt")
        else:
            # Custom species list file
            custom_list_path = st.text_input(
                "Custom species list file",
                value=st.session_state.get("custom_species_list", ""),
                help="Path to custom species list file"
            )
            
            if custom_list_path:
                try:
                    list_path = Path(custom_list_path)
                    if list_path.exists() and list_path.is_file():
                        st.session_state.custom_species_list = custom_list_path
                        params['custom_species_list_param'] = custom_list_path
                        st.success(f"✅ Using custom list: {list_path.name}")
                        
                        # Show preview
                        with st.expander("Preview species list"):
                            with open(list_path, 'r') as f:
                                lines = f.readlines()[:10]
                                for line in lines:
                                    st.text(line.strip())
                                if len(lines) == 10:
                                    st.text("...")
                    else:
                        st.error("File not found")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
    
    st.markdown("---")
    
    # Common parameters
    st.markdown("#### Detection Parameters")
    
    params['min_conf'] = st.slider(
        "Minimum Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Minimum confidence threshold for detections"
    )
    
    params['split_audio'] = st.checkbox(
        "Split audio files",
        value=True,
        help="Create individual audio clips for each detection"
    )
    
    if params['split_audio']:
        params['max_segments'] = st.number_input(
            "Max segments per species",
            min_value=1,
            max_value=100,
            value=10,
            help="Maximum number of audio clips to save per species"
        )
    else:
        params['max_segments'] = 0
    
    # Logger file (optional)
    with st.expander("Advanced Options"):
        logger_file = st.text_input(
            "Logger CSV file (optional)",
            value=st.session_state.get("logger_file_path", ""),
            help="Path to logger CSV for timestamp analysis"
        )
        if logger_file:
            st.session_state.logger_file_path = logger_file
            params['logger_file_path'] = logger_file

# Update parameters in session state
update_analysis_params(params)

# Analysis control section
st.markdown("---")

# Check if ready to analyze
ready_to_analyze = all([
    input_dir is not None,
    output_dir is not None,
    (analysis_mode == "location" or params.get('custom_species_list_param') is not None)
])

if ready_to_analyze:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.analysis_running:
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                # Reset previous analysis state
                reset_analysis_state()
                
                # Set running state
                st.session_state.analysis_running = True
                st.session_state.output_directory = str(output_dir)
                
                # Create progress container
                progress_container = st.container()
                
                # Run analysis with progress tracking
                with progress_container:
                    st.info("Starting analysis...")
                    success = run_analysis_with_progress(
                        progress_container,
                        input_dir,
                        output_dir,
                        params
                    )
                    
                    if success:
                        st.success("✅ Analysis completed successfully!")
                        st.balloons()
                        
                        # Show navigation options
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.page_link("pages/2_📊_Results.py", 
                                       label="View Results", 
                                       icon="📊",
                                       use_container_width=True)
                        with col2:
                            st.page_link("pages/3_🔊_Audio_Explorer.py", 
                                       label="Explore Audio", 
                                       icon="🔊",
                                       use_container_width=True)
                        with col3:
                            if st.button("🔄 New Analysis", use_container_width=True):
                                reset_analysis_state()
                                st.rerun()
                    else:
                        st.error("❌ Analysis failed or was cancelled")
                
                # Reset running state
                st.session_state.analysis_running = False
                
        else:
            st.warning("⏳ Analysis is already running...")
            
            # Show current progress
            progress_bar = st.progress(st.session_state.analysis_progress)
            st.text(st.session_state.analysis_status)
            
            if st.button("🛑 Cancel Analysis", type="secondary"):
                st.session_state.cancel_requested = True
                st.info("Cancellation requested...")
else:
    st.info("👆 Please configure all required parameters above to start the analysis")
    
    missing = []
    if not input_dir:
        missing.append("- Select input directory with audio files")
    if not output_dir:
        missing.append("- Select output directory for results")
    if analysis_mode == "location":
        if not params.get('lat') or not params.get('lon'):
            missing.append("- Set location coordinates")
    else:
        if not params.get('custom_species_list_param'):
            missing.append("- Select or provide a species list")
    
    if missing:
        st.markdown("**Missing:**")
        for item in missing:
            st.markdown(item)