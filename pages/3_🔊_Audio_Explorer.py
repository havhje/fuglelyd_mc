"""
Audio Explorer Page - Browse and play detected bird sounds
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from streamlit_utils.session_state import init_session_state
from streamlit_utils.audio_player import (
    get_audio_metadata, 
    create_audio_player, 
    display_audio_gallery,
    filter_audio_files
)

# Initialize session state
init_session_state()

# Page configuration
st.set_page_config(
    page_title="Audio Explorer - Bird Sound Analysis",
    page_icon="🔊",
    layout="wide"
)

st.title("🔊 Audio Explorer")
st.markdown("Listen to detected bird sounds from your analysis")
st.markdown("---")

# Check if analysis has been completed
if not st.session_state.get("analysis_complete", False):
    st.warning("⚠️ No audio files available yet")
    st.info("Please run an analysis with audio splitting enabled from the Analysis page first")
    
    if st.button("🎵 Go to Analysis Page"):
        st.switch_page("pages/1_🎵_Analysis.py")
    
    st.stop()

# Get audio files from session state
audio_files_dict = st.session_state.get("audio_files_dict", {})
results_df = st.session_state.get("current_results_df")

if not audio_files_dict:
    # Try to load from output directory
    output_dir = st.session_state.get("output_directory")
    if output_dir:
        lydfiler_dir = Path(output_dir) / "lydfiler"
        if lydfiler_dir.exists():
            audio_files_dict = {}
            for species_dir in lydfiler_dir.iterdir():
                if species_dir.is_dir():
                    species_name = species_dir.name
                    audio_files = list(species_dir.glob("*.wav"))
                    if audio_files:
                        audio_files_dict[species_name] = sorted(audio_files)
            st.session_state.audio_files_dict = audio_files_dict

if not audio_files_dict:
    st.warning("No audio files found. Make sure audio splitting was enabled during analysis.")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.subheader("🎛️ Audio Controls")
    
    # Species selector
    all_species = sorted(audio_files_dict.keys())
    selected_species = st.selectbox(
        "Select Species",
        options=["All Species"] + all_species,
        index=0,
        format_func=lambda x: f"🐦 {x}" if x != "All Species" else "🌍 All Species"
    )
    
    # Confidence filter
    min_confidence_filter = st.slider(
        "Minimum Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
        help="Filter audio clips by minimum confidence"
    )
    
    # Display mode
    display_mode = st.radio(
        "Display Mode",
        options=["Gallery", "List"],
        index=0,
        help="Choose how to display audio clips"
    )
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Statistics")
    
    total_clips = sum(len(files) for files in audio_files_dict.values())
    st.metric("Total Audio Clips", total_clips)
    st.metric("Species with Audio", len(audio_files_dict))
    
    if selected_species != "All Species":
        species_clips = len(audio_files_dict.get(selected_species, []))
        st.metric(f"Clips for {selected_species}", species_clips)

# Main content area
if selected_species == "All Species":
    st.subheader("🌍 All Species Audio Clips")
    
    # Apply confidence filter
    filtered_dict = filter_audio_files(audio_files_dict, min_confidence_filter)
    
    if not filtered_dict:
        st.warning(f"No audio clips found with confidence ≥ {min_confidence_filter:.0%}")
        st.stop()
    
    # Display species by species
    for species in sorted(filtered_dict.keys()):
        audio_files = filtered_dict[species]
        
        # Get Norwegian name if available
        norwegian_name = ""
        if results_df is not None and 'Species_NorwegianName' in results_df.columns:
            nor_name_row = results_df[results_df['scientific_name'] == species]['Species_NorwegianName'].first_valid_index()
            if nor_name_row is not None:
                norwegian_name = results_df.loc[nor_name_row, 'Species_NorwegianName']
                if pd.notna(norwegian_name):
                    norwegian_name = f" ({norwegian_name})"
        
        st.markdown(f"### 🐦 {species}{norwegian_name}")
        st.caption(f"{len(audio_files)} audio clips")
        
        if display_mode == "Gallery":
            display_audio_gallery(audio_files[:6], results_df, columns=3)  # Show max 6 per species
            if len(audio_files) > 6:
                st.info(f"Showing 6 of {len(audio_files)} clips. Select this species to see all.")
        else:
            # List mode
            for i, audio_file in enumerate(audio_files[:3]):  # Show max 3 in list mode
                metadata = get_audio_metadata(audio_file, results_df)
                st.markdown(f"**Clip {i+1}**")
                create_audio_player(audio_file, metadata, show_metadata=True)
            if len(audio_files) > 3:
                st.info(f"Showing 3 of {len(audio_files)} clips. Select this species to see all.")
        
        st.markdown("---")
        
else:
    # Single species view
    st.subheader(f"🐦 {selected_species}")
    
    # Get Norwegian name if available
    if results_df is not None and 'Species_NorwegianName' in results_df.columns:
        nor_name_row = results_df[results_df['scientific_name'] == selected_species]['Species_NorwegianName'].first_valid_index()
        if nor_name_row is not None:
            norwegian_name = results_df.loc[nor_name_row, 'Species_NorwegianName']
            if pd.notna(norwegian_name):
                st.caption(f"Norwegian: {norwegian_name}")
    
    # Get species info if available
    if results_df is not None:
        species_data = results_df[results_df['scientific_name'] == selected_species]
        if not species_data.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Detections", len(species_data))
            
            with col2:
                avg_conf = species_data['confidence'].mean()
                st.metric("Avg Confidence", f"{avg_conf:.2%}")
            
            with col3:
                if 'Family_ScientificName' in species_data.columns:
                    family = species_data['Family_ScientificName'].iloc[0]
                    st.metric("Family", family if pd.notna(family) else "Unknown")
            
            with col4:
                if 'Redlist_Status' in species_data.columns:
                    status = species_data['Redlist_Status'].iloc[0]
                    st.metric("Red List", status if pd.notna(status) else "Not Listed")
    
    st.markdown("---")
    
    # Get audio files for selected species
    audio_files = audio_files_dict.get(selected_species, [])
    
    # Apply confidence filter
    filtered_files = []
    for file in audio_files:
        metadata = get_audio_metadata(file)
        if metadata.get('confidence', 0) >= min_confidence_filter:
            filtered_files.append(file)
    
    if not filtered_files:
        st.warning(f"No audio clips found with confidence ≥ {min_confidence_filter:.0%}")
    else:
        st.info(f"Showing {len(filtered_files)} of {len(audio_files)} clips (filtered by confidence)")
        
        if display_mode == "Gallery":
            display_audio_gallery(filtered_files, results_df, columns=2)
        else:
            # List mode with detailed view
            for i, audio_file in enumerate(filtered_files):
                with st.container():
                    st.markdown(f"### 🎵 Clip {i+1} of {len(filtered_files)}")
                    
                    metadata = get_audio_metadata(audio_file, results_df)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        create_audio_player(audio_file, metadata, show_metadata=False)
                    
                    with col2:
                        st.markdown("**Metadata:**")
                        st.markdown(f"- Confidence: {metadata.get('confidence', 0):.2%}")
                        st.markdown(f"- Duration: {metadata.get('end_time', 0) - metadata.get('start_time', 0):.1f}s")
                        st.markdown(f"- Start: {metadata.get('start_time', 0):.1f}s")
                        st.markdown(f"- End: {metadata.get('end_time', 0):.1f}s")
                        st.markdown(f"- Source: {metadata.get('original_file', 'Unknown')}")
                    
                    st.markdown("---")

# Export options
st.markdown("---")
st.subheader("💾 Export Options")

col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Download Audio Metadata (CSV)"):
        # Create metadata CSV
        metadata_list = []
        for species, files in audio_files_dict.items():
            for file in files:
                metadata = get_audio_metadata(file)
                metadata['species'] = species
                metadata['file_name'] = file.name
                metadata_list.append(metadata)
        
        if metadata_list:
            metadata_df = pd.DataFrame(metadata_list)
            csv = metadata_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="audio_clips_metadata.csv",
                mime="text/csv"
            )

with col2:
    output_dir = st.session_state.get("output_directory")
    if output_dir:
        st.info(f"Audio files location: {output_dir}/lydfiler/")