"""
Settings Page - Configure analysis parameters and paths
"""

import streamlit as st
from pathlib import Path
import sys
import subprocess
import platform

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from streamlit_utils.session_state import init_session_state
from streamlit_utils.file_browser import directory_picker

# Initialize session state
init_session_state()

# Page configuration
st.set_page_config(
    page_title="Settings - Bird Sound Analysis",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Settings")
st.markdown("Configure analysis parameters and application settings")
st.markdown("---")

# Create tabs for different settings categories
tab1, tab2, tab3, tab4 = st.tabs(["📁 Paths", "📋 Species Lists", "🔧 System", "💾 Preferences"])

with tab1:
    st.subheader("Directory Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Default Input Directory")
        default_input = st.text_input(
            "Default directory for audio files",
            value=st.session_state.get("default_input_dir", str(Path.home())),
            help="This directory will be pre-selected in the Analysis page"
        )
        if st.button("📁 Set as Default Input", key="set_default_input"):
            st.session_state.default_input_dir = default_input
            st.success("✅ Default input directory updated")
    
    with col2:
        st.markdown("#### Default Output Directory")
        default_output = st.text_input(
            "Default directory for results",
            value=st.session_state.get("default_output_dir", str(Path.home())),
            help="This directory will be pre-selected for saving results"
        )
        if st.button("📁 Set as Default Output", key="set_default_output"):
            st.session_state.default_output_dir = default_output
            st.success("✅ Default output directory updated")
    
    st.markdown("---")
    
    st.markdown("#### Logger File Path")
    logger_path = st.text_input(
        "Logger CSV file path (optional)",
        value=st.session_state.get("default_logger_path", ""),
        help="Path to logger CSV for real timestamp analysis"
    )
    if logger_path:
        if st.button("📁 Set Logger Path"):
            st.session_state.default_logger_path = logger_path
            st.success("✅ Logger file path updated")

with tab2:
    st.subheader("Species List Management")
    
    # Default species list
    default_list_path = Path("data_input_artsliste/arter.txt")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Default Species List")
        st.info(f"Location: {default_list_path}")
        
        if default_list_path.exists():
            with open(default_list_path, 'r', encoding='utf-8') as f:
                species_content = f.read()
            
            # Count species
            species_lines = [line.strip() for line in species_content.split('\n') if line.strip()]
            st.success(f"✅ Found {len(species_lines)} species in default list")
            
            # Edit species list
            edited_content = st.text_area(
                "Edit default species list (one species per line):",
                value=species_content,
                height=400,
                help="Edit the species list directly. Changes will be saved to the file."
            )
            
            if st.button("💾 Save Changes", type="primary"):
                try:
                    with open(default_list_path, 'w', encoding='utf-8') as f:
                        f.write(edited_content)
                    st.success("✅ Species list updated successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Failed to save: {e}")
        else:
            st.warning("Default species list not found")
            st.info("Creating new species list...")
            
            new_content = st.text_area(
                "Create new species list (one species per line):",
                value="",
                height=400,
                placeholder="Enter species names, one per line..."
            )
            
            if st.button("💾 Create Species List", type="primary"):
                try:
                    default_list_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(default_list_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    st.success("✅ Species list created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create: {e}")
    
    with col2:
        st.markdown("#### Import/Export")
        
        # Upload new species list
        uploaded_file = st.file_uploader(
            "Upload species list",
            type=['txt'],
            help="Upload a text file with one species per line"
        )
        
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            st.text_area("Preview:", value=content[:500] + "..." if len(content) > 500 else content, height=200)
            
            if st.button("📥 Import This List"):
                try:
                    with open(default_list_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    st.success("✅ Species list imported successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to import: {e}")
        
        # Download current list
        if default_list_path.exists():
            with open(default_list_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            st.download_button(
                label="📤 Export Current List",
                data=current_content,
                file_name="species_list.txt",
                mime="text/plain"
            )

with tab3:
    st.subheader("System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### FFmpeg Configuration")
        
        system = platform.system()
        if system == "Darwin":  # macOS
            ffmpeg_dir = Path("ffmpeg_macos_bin")
        elif system == "Windows":
            ffmpeg_dir = Path("ffmpeg_win_bin")
        else:
            ffmpeg_dir = None
        
        if ffmpeg_dir and ffmpeg_dir.exists():
            st.success(f"✅ FFmpeg directory found: {ffmpeg_dir}")
            
            # Check FFmpeg executable
            ffmpeg_path = ffmpeg_dir / "ffmpeg"
            if system == "Windows":
                ffmpeg_path = ffmpeg_path.with_suffix(".exe")
            
            if ffmpeg_path.exists():
                st.success(f"✅ FFmpeg executable found")
                
                # Try to get version
                try:
                    result = subprocess.run(
                        [str(ffmpeg_path), "-version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        version_line = result.stdout.split('\n')[0]
                        st.info(f"Version: {version_line}")
                except Exception as e:
                    st.warning(f"Could not get FFmpeg version: {e}")
            else:
                st.error("❌ FFmpeg executable not found")
        else:
            st.warning("FFmpeg directory not found for this platform")
        
        st.markdown("---")
        
        st.markdown("#### Python Environment")
        st.code(f"Python {sys.version}")
        st.code(f"Platform: {platform.platform()}")
    
    with col2:
        st.markdown("#### BirdNET Configuration")
        
        st.info("BirdNET is automatically configured when running analysis")
        
        # Analysis defaults
        st.markdown("##### Default Analysis Parameters")
        
        default_confidence = st.slider(
            "Default minimum confidence",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get("default_min_confidence", 0.5),
            step=0.05
        )
        
        if st.button("💾 Save Defaults"):
            st.session_state.default_min_confidence = default_confidence
            st.success("✅ Default parameters saved")
        
        st.markdown("---")
        
        # Performance settings
        st.markdown("##### Performance Settings")
        
        max_workers = st.number_input(
            "Max parallel workers",
            min_value=1,
            max_value=16,
            value=st.session_state.get("max_workers", 4),
            help="Number of parallel threads for processing"
        )
        
        if st.button("💾 Save Performance Settings"):
            st.session_state.max_workers = max_workers
            st.success("✅ Performance settings saved")

with tab4:
    st.subheader("Application Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Display Preferences")
        
        # Theme preference (note: actual theme is controlled by Streamlit config)
        st.info("Theme can be changed in Streamlit settings (top right menu → Settings)")
        
        # Data display preferences
        st.markdown("##### Data Display")
        
        show_scientific_names = st.checkbox(
            "Always show scientific names",
            value=st.session_state.get("show_scientific_names", True)
        )
        
        show_norwegian_names = st.checkbox(
            "Show Norwegian names when available",
            value=st.session_state.get("show_norwegian_names", True)
        )
        
        decimal_places = st.number_input(
            "Decimal places for confidence",
            min_value=0,
            max_value=4,
            value=st.session_state.get("decimal_places", 2)
        )
        
        if st.button("💾 Save Display Preferences"):
            st.session_state.show_scientific_names = show_scientific_names
            st.session_state.show_norwegian_names = show_norwegian_names
            st.session_state.decimal_places = decimal_places
            st.success("✅ Display preferences saved")
    
    with col2:
        st.markdown("#### Export Preferences")
        
        # CSV separator
        csv_separator = st.selectbox(
            "CSV separator",
            options=[";", ",", "\t", "|"],
            index=0,
            help="Character used to separate values in CSV exports"
        )
        
        # File naming
        st.markdown("##### File Naming")
        
        include_timestamp = st.checkbox(
            "Include timestamp in exported filenames",
            value=st.session_state.get("include_timestamp", True)
        )
        
        timestamp_format = st.selectbox(
            "Timestamp format",
            options=["%Y%m%d_%H%M%S", "%Y-%m-%d_%H-%M-%S", "%Y%m%d", "%d-%m-%Y"],
            index=0 if not st.session_state.get("timestamp_format") else 
                  ["%Y%m%d_%H%M%S", "%Y-%m-%d_%H-%M-%S", "%Y%m%d", "%d-%m-%Y"].index(
                      st.session_state.get("timestamp_format", "%Y%m%d_%H%M%S")
                  )
        )
        
        if st.button("💾 Save Export Preferences"):
            st.session_state.csv_separator = csv_separator
            st.session_state.include_timestamp = include_timestamp
            st.session_state.timestamp_format = timestamp_format
            st.success("✅ Export preferences saved")

# Reset settings
st.markdown("---")
st.markdown("### 🔄 Reset Settings")

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🗑️ Reset All Settings to Defaults", type="secondary", use_container_width=True):
        # Clear relevant session state
        keys_to_reset = [
            "default_input_dir", "default_output_dir", "default_logger_path",
            "default_min_confidence", "max_workers", "show_scientific_names",
            "show_norwegian_names", "decimal_places", "csv_separator",
            "include_timestamp", "timestamp_format"
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("✅ All settings reset to defaults!")
        st.rerun()