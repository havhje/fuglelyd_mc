"""
About Page - Documentation and help for the Bird Sound Analysis Tool
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Page configuration
st.set_page_config(
    page_title="About - Bird Sound Analysis",
    page_icon="ℹ️",
    layout="wide"
)

st.title("ℹ️ About Bird Sound Analysis Tool")
st.markdown("Documentation, usage guide, and attributions")
st.markdown("---")

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📖 Overview", "🚀 Usage Guide", "🔧 Troubleshooting", "🙏 Attributions", "📚 API Reference"])

with tab1:
    st.subheader("Project Overview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### What is this tool?
        
        The Bird Sound Analysis Tool is a comprehensive application for detecting and identifying bird species 
        from audio recordings. It combines state-of-the-art machine learning with local taxonomic data to provide 
        detailed insights into bird populations and their activity patterns.
        
        ### Key Features
        
        - **🎯 Automated Bird Detection**: Uses BirdNET AI to identify bird species from audio
        - **🇳🇴 Norwegian Taxonomic Data**: Enriches results with local species information
        - **📊 Temporal Analysis**: Analyzes bird activity patterns throughout the day
        - **✂️ Audio Segmentation**: Splits recordings into species-specific clips
        - **📈 Statistical Reports**: Generates comprehensive statistics and visualizations
        - **🔊 Interactive Playback**: Listen to detected bird sounds in your browser
        
        ### How it works
        
        1. **Audio Analysis**: The tool processes your audio files using BirdNET
        2. **Species Detection**: Identifies bird species with confidence scores
        3. **Data Enrichment**: Adds Norwegian names and taxonomic information
        4. **Temporal Analysis**: Extracts time patterns from filenames
        5. **Audio Splitting**: Creates individual clips for each detection
        6. **Visualization**: Generates activity plots and statistics
        """)
    
    with col2:
        st.info("""
        **Quick Facts**
        
        - 🎵 Supports multiple audio formats
        - 🌍 Location-based filtering
        - 📋 Custom species lists
        - 🔒 Runs locally on your machine
        - 📊 Export results as CSV
        - 🎨 Beautiful visualizations
        """)
        
        st.success("""
        **Perfect for:**
        
        - Researchers
        - Birdwatchers
        - Conservation projects
        - Educational purposes
        - Citizen science
        """)

with tab2:
    st.subheader("🚀 Getting Started Guide")
    
    st.markdown("""
    ### Step 1: Prepare Your Audio Files
    
    - Place all audio files in a single directory
    - Supported formats: WAV, MP3, FLAC, OGG, M4A, AAC, OPUS
    - For temporal analysis, use filenames with timestamps (e.g., `recording_20240520_063000.wav`)
    
    ### Step 2: Configure Analysis
    
    1. Navigate to the **🎵 Analysis** page
    2. Select your audio files directory
    3. Choose an output directory for results
    4. Select analysis mode:
       - **Location-based**: Uses coordinates and date to filter likely species
       - **Species list**: Uses a predefined list of species to search for
    
    ### Step 3: Set Parameters
    
    - **Minimum Confidence**: How certain BirdNET must be (0.5 = 50% is recommended)
    - **Audio Splitting**: Enable to create individual clips for each detection
    - **Max Segments**: Limit clips per species to save disk space
    
    ### Step 4: Run Analysis
    
    1. Click **🚀 Start Analysis**
    2. Monitor progress in real-time
    3. Cancel if needed with the stop button
    
    ### Step 5: Explore Results
    
    - **📊 Results**: View detections, statistics, and export data
    - **🔊 Audio Explorer**: Listen to detected bird sounds
    - **💾 Export**: Download CSV files and visualizations
    
    ---
    
    ### 💡 Pro Tips
    
    1. **Better Detection**:
       - Use high-quality recordings
       - Minimize background noise
       - Record during peak bird activity (dawn/dusk)
    
    2. **Filename Format**:
       - Include timestamps for temporal analysis
       - Format: `YYYYMMDD_HHMMSS` or similar
       - Example: `forest_20240520_063000.wav`
    
    3. **Species Lists**:
       - Create custom lists for targeted searches
       - Use scientific names (Latin)
       - One species per line
    
    4. **Performance**:
       - Process smaller batches for faster results
       - Higher confidence thresholds = fewer false positives
       - Disable audio splitting for overview analysis
    """)

with tab3:
    st.subheader("🔧 Troubleshooting")
    
    with st.expander("❌ No birds detected"):
        st.markdown("""
        **Possible causes:**
        - Audio files contain no bird sounds
        - Confidence threshold too high
        - Wrong species list for your location
        - Poor audio quality
        
        **Solutions:**
        - Lower the confidence threshold to 0.3
        - Use location-based mode instead of species list
        - Check audio files manually for bird sounds
        - Ensure recordings are clear with minimal noise
        """)
    
    with st.expander("🐌 Analysis running slowly"):
        st.markdown("""
        **Possible causes:**
        - Large number of files
        - Long audio files
        - Audio splitting enabled
        - System resources limited
        
        **Solutions:**
        - Process files in smaller batches
        - Disable audio splitting for initial analysis
        - Close other applications
        - Use shorter audio clips (5-10 minutes ideal)
        """)
    
    with st.expander("🔊 Audio won't play"):
        st.markdown("""
        **Possible causes:**
        - Browser doesn't support audio format
        - File permissions issue
        - Corrupted audio file
        
        **Solutions:**
        - Try a different browser (Chrome/Firefox recommended)
        - Check file permissions
        - Verify audio files play in other applications
        - Ensure audio splitting completed successfully
        """)
    
    with st.expander("📁 Can't select directories"):
        st.markdown("""
        **Possible causes:**
        - Permission issues
        - Invalid path
        - Directory doesn't exist
        
        **Solutions:**
        - Use absolute paths
        - Check directory permissions
        - Create directory if it doesn't exist
        - Try copying the full path from file explorer
        """)
    
    with st.expander("🌐 No Norwegian names appearing"):
        st.markdown("""
        **Possible causes:**
        - Species not found in Norwegian database
        - API connection issues
        - Species name mismatch
        
        **Solutions:**
        - Check internet connection
        - Some species may not have Norwegian names
        - Verify scientific names are correct
        - Check Results page for any error messages
        """)

with tab4:
    st.subheader("🙏 Attributions and Credits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### BirdNET
        
        This tool uses **BirdNET**, developed by the Cornell Lab of Ornithology and Chemnitz University of Technology.
        
        - **Website**: [birdnet.cornell.edu](https://birdnet.cornell.edu)
        - **Paper**: Kahl, S., Wood, C. M., Eibl, M., & Klinck, H. (2021). BirdNET: A deep learning solution for avian diversity monitoring. Ecological Informatics, 61, 101236.
        - **License**: MIT License
        
        ### Artskart API
        
        Norwegian taxonomic data is provided by **Artskart** (Species Map Service).
        
        - **Provider**: Norwegian Biodiversity Information Centre (Artsdatabanken)
        - **Website**: [artskart.artsdatabanken.no](https://artskart.artsdatabanken.no)
        - **API**: Public REST API for taxonomic information
        - **Data License**: CC BY 4.0
        """)
    
    with col2:
        st.markdown("""
        ### Dependencies
        
        This application is built with:
        
        - **Streamlit**: Web application framework
        - **TensorFlow**: Machine learning backend for BirdNET
        - **Pandas**: Data manipulation and analysis
        - **Matplotlib/Seaborn**: Visualization libraries
        - **Pydub/FFmpeg**: Audio processing
        - **Requests**: API communication
        
        ### Acknowledgments
        
        Special thanks to:
        - The BirdNET team for their amazing model
        - Artsdatabanken for taxonomic data access
        - The open-source community
        - All contributors and testers
        
        ### License
        
        This tool is provided as-is for research and educational purposes.
        Please respect the licenses of the underlying components.
        """)
    
    st.markdown("---")
    
    st.info("""
    **📧 Contact & Support**
    
    For issues, suggestions, or contributions, please consult the project documentation or contact the development team.
    """)

with tab5:
    st.subheader("📚 API Reference")
    
    st.markdown("""
    ### Analysis Parameters
    
    | Parameter | Type | Default | Description |
    |-----------|------|---------|-------------|
    | `input_dir` | Path | Required | Directory containing audio files |
    | `output_dir` | Path | Required | Directory for saving results |
    | `lat` | float | Required* | Latitude for location-based analysis |
    | `lon` | float | Required* | Longitude for location-based analysis |
    | `date` | date | Today | Date for seasonal species filtering |
    | `min_conf` | float | 0.5 | Minimum confidence threshold (0-1) |
    | `split_audio` | bool | True | Enable audio segmentation |
    | `max_segments` | int | 10 | Max audio clips per species |
    | `custom_species_list` | Path | None | Path to custom species list |
    
    *Required for location-based analysis only
    
    ### Output Files
    
    ```
    output_dir/
    ├── interim/
    │   └── enriched_detections.csv    # Main results with all detections
    ├── lydfiler/
    │   ├── Species_1/                 # Audio clips for each species
    │   │   ├── clip_1.wav
    │   │   └── clip_2.wav
    │   └── Species_2/
    │       └── clip_1.wav
    └── figur/
        └── bird_detection_joypy_plot.png  # Temporal activity visualization
    ```
    
    ### CSV Output Format
    
    The enriched detections CSV contains:
    
    - `scientific_name`: Species scientific name
    - `confidence`: Detection confidence (0-1)
    - `start_time`: Detection start in seconds
    - `end_time`: Detection end in seconds
    - `file_path`: Source audio file
    - `Species_NorwegianName`: Norwegian common name
    - `Family_ScientificName`: Taxonomic family
    - `Order_ScientificName`: Taxonomic order
    - `Redlist_Status`: Conservation status
    - Additional taxonomic fields...
    
    ### Audio Clip Naming
    
    Split audio files follow this pattern:
    ```
    originalfilename_starttime_endtime_species_confidence.wav
    ```
    
    Example:
    ```
    recording_20240520_063000_180.5_183.5_Turdus_philomelos_0.95.wav
    ```
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Bird Sound Analysis Tool - Built with ❤️ using Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)