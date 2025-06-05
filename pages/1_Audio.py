import streamlit as st
import os
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Audio Playback",
    layout="wide"
)

st.title("Audio Playback")
st.divider()

# Check if analysis has been completed
if "output_dir" not in st.session_state or st.session_state.output_dir is None:
    st.warning("No analysis results available. Please run an analysis first.")
    st.stop()

audio_dir = os.path.join(st.session_state.output_dir, "lydfiler")

if not os.path.exists(audio_dir):
    st.warning("No audio files found. Make sure audio splitting was enabled during analysis.")
    st.stop()

# Get list of species folders
species_folders = [f for f in os.listdir(audio_dir) if os.path.isdir(os.path.join(audio_dir, f))]

if not species_folders:
    st.warning("No species audio folders found.")
    st.stop()

# Species selector
selected_species = st.selectbox(
    "Select Species",
    options=sorted(species_folders),
    format_func=lambda x: x.replace("_", " ")
)

st.divider()

# List audio files for selected species
species_path = os.path.join(audio_dir, selected_species)
audio_files = sorted([f for f in os.listdir(species_path) if f.endswith(('.mp3', '.wav', '.flac', '.ogg'))])

if not audio_files:
    st.info(f"No audio files found for {selected_species}")
else:
    st.subheader(f"Audio Clips: {selected_species.replace('_', ' ')}")
    st.text(f"Found {len(audio_files)} audio clips")
    
    # Display audio files
    for i, audio_file in enumerate(audio_files):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Extract confidence from filename if available
            # Format: species_confidence_timestamp.mp3
            parts = audio_file.split('_')
            if len(parts) >= 2:
                try:
                    confidence = float(parts[1])
                    st.text(f"Clip {i+1}: {audio_file} (Confidence: {confidence:.2f})")
                except:
                    st.text(f"Clip {i+1}: {audio_file}")
            else:
                st.text(f"Clip {i+1}: {audio_file}")
        
        # Audio player
        audio_path = os.path.join(species_path, audio_file)
        with open(audio_path, 'rb') as audio:
            st.audio(audio.read(), format=f'audio/{audio_file.split(".")[-1]}')
        
        st.divider()