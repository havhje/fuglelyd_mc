"""Audio player utilities for Streamlit app"""

import streamlit as st
from pathlib import Path
from typing import List, Optional, Dict
import pandas as pd


def get_audio_metadata(audio_file: Path, detections_df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Extract metadata from audio file name and detections dataframe
    
    File format: originalfile_starttime_endtime_species_confidence.wav
    """
    metadata = {
        "file_path": audio_file,
        "file_name": audio_file.name,
        "species": "",
        "confidence": 0.0,
        "start_time": 0.0,
        "end_time": 0.0,
        "original_file": ""
    }
    
    try:
        # Parse filename
        parts = audio_file.stem.split('_')
        if len(parts) >= 5:
            metadata["original_file"] = parts[0]
            metadata["start_time"] = float(parts[1])
            metadata["end_time"] = float(parts[2])
            metadata["species"] = parts[3]
            metadata["confidence"] = float(parts[4])
    except Exception as e:
        st.warning(f"Could not parse metadata from {audio_file.name}: {e}")
    
    return metadata


def create_audio_player(audio_file: Path, 
                       metadata: Dict,
                       show_metadata: bool = True) -> None:
    """Create an audio player widget with optional metadata display"""
    
    if show_metadata:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Species:** {metadata.get('species', 'Unknown')}")
            st.markdown(f"**Source:** {metadata.get('original_file', 'Unknown')}")
        
        with col2:
            confidence = metadata.get('confidence', 0.0)
            st.metric("Confidence", f"{confidence:.2%}")
        
        with col3:
            duration = metadata.get('end_time', 0) - metadata.get('start_time', 0)
            st.metric("Duration", f"{duration:.1f}s")
    
    # Audio player
    try:
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format='audio/wav')
    except Exception as e:
        st.error(f"Could not load audio file: {e}")


def display_audio_gallery(audio_files: List[Path], 
                         detections_df: Optional[pd.DataFrame] = None,
                         columns: int = 2) -> None:
    """Display a gallery of audio players"""
    
    if not audio_files:
        st.info("No audio files to display")
        return
    
    # Sort by confidence (highest first)
    audio_files_with_metadata = []
    for audio_file in audio_files:
        metadata = get_audio_metadata(audio_file, detections_df)
        audio_files_with_metadata.append((audio_file, metadata))
    
    audio_files_with_metadata.sort(key=lambda x: x[1].get('confidence', 0), reverse=True)
    
    # Display in columns
    for i in range(0, len(audio_files_with_metadata), columns):
        cols = st.columns(columns)
        for j in range(columns):
            if i + j < len(audio_files_with_metadata):
                audio_file, metadata = audio_files_with_metadata[i + j]
                with cols[j]:
                    with st.container():
                        st.markdown(f"### 🎵 Clip {i + j + 1}")
                        create_audio_player(audio_file, metadata)
                        st.markdown("---")


def filter_audio_files(audio_files_dict: Dict[str, List[Path]], 
                      min_confidence: float = 0.0) -> Dict[str, List[Path]]:
    """Filter audio files by minimum confidence"""
    
    filtered_dict = {}
    
    for species, files in audio_files_dict.items():
        filtered_files = []
        for file in files:
            metadata = get_audio_metadata(file)
            if metadata.get('confidence', 0) >= min_confidence:
                filtered_files.append(file)
        
        if filtered_files:
            filtered_dict[species] = filtered_files
    
    return filtered_dict