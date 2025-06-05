"""Session state management utilities for Streamlit app"""

import streamlit as st
from typing import Any, Dict


def init_session_state():
    """Initialize all session state variables if not already present"""
    defaults = {
        "analysis_running": False,
        "analysis_progress": 0.0,
        "analysis_status": "",
        "cancel_requested": False,
        "current_results_df": None,
        "analysis_complete": False,
        "output_directory": None,
        "input_directory": None,
        "analysis_params": {},
        "enriched_csv_path": None,
        "joypy_plot_path": None,
        "analysis_thread": None,
        "selected_species": None,
        "audio_files_dict": {},
        "logger_file_path": None,
        "custom_species_list": None,
        "use_default_species_list": False,
        "analysis_mode": "location",  # "location" or "species_list"
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_analysis_state():
    """Reset analysis-related session state variables"""
    st.session_state.analysis_running = False
    st.session_state.analysis_progress = 0.0
    st.session_state.analysis_status = ""
    st.session_state.cancel_requested = False
    st.session_state.current_results_df = None
    st.session_state.analysis_complete = False
    st.session_state.enriched_csv_path = None
    st.session_state.joypy_plot_path = None
    st.session_state.audio_files_dict = {}


def get_analysis_params() -> Dict[str, Any]:
    """Get current analysis parameters from session state"""
    return st.session_state.get("analysis_params", {})


def update_analysis_params(params: Dict[str, Any]):
    """Update analysis parameters in session state"""
    st.session_state.analysis_params = params


def is_analysis_running() -> bool:
    """Check if analysis is currently running"""
    return st.session_state.get("analysis_running", False)


def request_cancel():
    """Request cancellation of the current analysis"""
    st.session_state.cancel_requested = True


def is_cancel_requested() -> bool:
    """Check if cancellation has been requested"""
    return st.session_state.get("cancel_requested", False)


def update_progress(progress: float, status: str = ""):
    """Update analysis progress and status"""
    st.session_state.analysis_progress = progress
    if status:
        st.session_state.analysis_status = status