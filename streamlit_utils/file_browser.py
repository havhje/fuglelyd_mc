"""File browser utilities for Streamlit app"""

import os
from pathlib import Path
from typing import List, Optional
import streamlit as st


def get_subdirectories(path: str) -> List[str]:
    """Get list of subdirectories in the given path"""
    try:
        path_obj = Path(path)
        if not path_obj.exists() or not path_obj.is_dir():
            return []
        
        subdirs = [d.name for d in path_obj.iterdir() if d.is_dir() and not d.name.startswith('.')]
        return sorted(subdirs)
    except Exception:
        return []


def get_audio_files(directory: Path) -> List[Path]:
    """Get all audio files in a directory"""
    audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac', '.opus'}
    audio_files = []
    
    try:
        for file in directory.rglob('*'):
            if file.is_file() and file.suffix.lower() in audio_extensions:
                audio_files.append(file)
    except Exception as e:
        st.error(f"Error scanning directory: {e}")
    
    return sorted(audio_files)


def directory_picker(label: str, key: str, initial_path: Optional[str] = None) -> Optional[Path]:
    """
    Create a directory picker widget
    
    Args:
        label: Label for the directory picker
        key: Unique key for the widget
        initial_path: Initial path to start browsing from
        
    Returns:
        Selected directory path or None
    """
    # Initialize session state for navigation
    nav_key = f"{key}_nav_path"
    if nav_key not in st.session_state:
        st.session_state[nav_key] = initial_path or str(Path.home())
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Text input for direct path entry
        path_input = st.text_input(
            label,
            value=st.session_state[nav_key],
            key=f"{key}_input",
            help="Enter a directory path or use the browser below",
            on_change=lambda: setattr(st.session_state, nav_key, st.session_state[f"{key}_input"])
        )
    
    with col2:
        # Refresh button
        if st.button("🔄 Refresh", key=f"{key}_refresh"):
            st.rerun()
    
    # Validate and expand path
    try:
        current_path = Path(path_input).expanduser().resolve()
        if not current_path.exists():
            st.error(f"Path does not exist: {current_path}")
            return None
        if not current_path.is_dir():
            st.error(f"Path is not a directory: {current_path}")
            return None
    except Exception as e:
        st.error(f"Invalid path: {e}")
        return None
    
    # Directory browser
    st.caption(f"📁 Browsing: {current_path}")
    
    # Parent directory button
    if current_path.parent != current_path:
        if st.button("⬆️ Parent Directory", key=f"{key}_parent"):
            st.session_state[nav_key] = str(current_path.parent)
            st.rerun()
    
    # List subdirectories
    subdirs = get_subdirectories(str(current_path))
    if subdirs:
        selected_subdir = st.selectbox(
            "Subdirectories:",
            options=[""] + subdirs,
            key=f"{key}_subdir",
            format_func=lambda x: "Select a subdirectory..." if x == "" else f"📁 {x}"
        )
        
        if selected_subdir:
            new_path = current_path / selected_subdir
            if st.button(f"Enter {selected_subdir}", key=f"{key}_enter"):
                st.session_state[nav_key] = str(new_path)
                st.rerun()
    
    # Show some stats about the selected directory
    if current_path.exists() and current_path.is_dir():
        audio_files = get_audio_files(current_path)
        if audio_files:
            st.success(f"✅ Found {len(audio_files)} audio files in this directory")
        else:
            st.warning("⚠️ No audio files found in this directory")
    
    return current_path if current_path.exists() and current_path.is_dir() else None


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"