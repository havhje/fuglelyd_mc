"""Progress tracking utilities for long-running operations"""

import streamlit as st
import threading
import time
from typing import Callable, Optional, Any
from pathlib import Path


class ProgressTracker:
    """Thread-safe progress tracker for background operations"""
    
    def __init__(self):
        self.progress = 0.0
        self.status = ""
        self.lock = threading.Lock()
        self.cancel_requested = False
    
    def update(self, progress: float, status: str = ""):
        """Update progress and status thread-safely"""
        with self.lock:
            self.progress = max(0.0, min(1.0, progress))
            if status:
                self.status = status
    
    def get_progress(self) -> tuple[float, str]:
        """Get current progress and status"""
        with self.lock:
            return self.progress, self.status
    
    def request_cancel(self):
        """Request cancellation"""
        with self.lock:
            self.cancel_requested = True
    
    def is_cancelled(self) -> bool:
        """Check if cancellation was requested"""
        with self.lock:
            return self.cancel_requested
    
    def reset(self):
        """Reset the tracker"""
        with self.lock:
            self.progress = 0.0
            self.status = ""
            self.cancel_requested = False


class AnalysisThread(threading.Thread):
    """Thread for running bird sound analysis in the background"""
    
    def __init__(self, 
                 input_dir: Path,
                 output_dir: Path,
                 params: dict,
                 progress_tracker: ProgressTracker,
                 completion_callback: Optional[Callable] = None):
        super().__init__(daemon=True)
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.params = params
        self.progress_tracker = progress_tracker
        self.completion_callback = completion_callback
        self.exception = None
    
    def run(self):
        """Run the analysis in a separate thread"""
        try:
            # Import here to avoid circular imports
            from functions.birdnetlib_api import run_birdnet_analysis, on_analyze_directory_complete
            from functions.artskart_api import fetch_artskart_taxon_info_by_name
            from functions.splitter_lydfilen import split_audio_by_detection
            from functions.statistics import generate_statistics_report
            from functions.joy2_tester import create_joypy_plot
            import pandas as pd
            import functools
            import logging
            from datetime import datetime
            
            # Import the main analysis functions
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from analyser_lyd_main import (
                clean_output_directories,
                initialize_dataframe,
                enrich_detections_with_taxonomy
            )
            
            # Update progress
            self.progress_tracker.update(0.1, "Cleaning output directories...")
            clean_output_directories(self.output_dir)
            
            if self.progress_tracker.is_cancelled():
                return
            
            # Prepare paths
            output_csv_path = self.output_dir / "interim" / "enriched_detections.csv"
            split_audio_output_dir = self.output_dir / "lydfiler"
            
            # Extract parameters
            birdnet_lon = self.params.get('lon', 15.4244)
            birdnet_lat = self.params.get('lat', 68.5968)
            birdnet_date = self.params.get('date', datetime.now())
            birdnet_min_conf = self.params.get('min_conf', 0.5)
            run_audio_splitting = self.params.get('split_audio', True)
            max_segments_per_species = self.params.get('max_segments', 10)
            custom_species_list_param = self.params.get('custom_species_list_param', None)
            logger_file_path = self.params.get('logger_file_path', None)
            
            # Create wrapped callback that updates progress
            def progress_callback(file_progress, file_name=""):
                if self.progress_tracker.is_cancelled():
                    return False  # Signal to stop
                # Map file progress (0-1) to overall progress (0.1-0.6)
                overall_progress = 0.1 + (file_progress * 0.5)
                status = f"Analyzing audio files... {file_name}"
                self.progress_tracker.update(overall_progress, status)
                return True  # Continue processing
            
            # Create the callback function with the determined input path
            prepared_callback_function = functools.partial(
                on_analyze_directory_complete, 
                base_input_path=self.input_dir
            )
            
            # Run BirdNET analysis
            self.progress_tracker.update(0.15, "Starting BirdNET analysis...")
            all_detections_list = run_birdnet_analysis(
                self.input_dir,
                prepared_callback_function,
                lon=birdnet_lon,
                lat=birdnet_lat,
                analysis_date=birdnet_date,
                min_confidence=birdnet_min_conf,
                custom_species_list_path=custom_species_list_param,
                progress_callback=progress_callback
            )
            
            if self.progress_tracker.is_cancelled():
                return
            
            # Initialize DataFrame
            self.progress_tracker.update(0.65, "Processing detections...")
            detections_df = initialize_dataframe(all_detections_list)
            if detections_df is None:
                self.progress_tracker.update(1.0, "No detections found")
                return
            
            # Enrich with taxonomic data
            self.progress_tracker.update(0.7, "Enriching with taxonomic data...")
            detections_df = enrich_detections_with_taxonomy(detections_df)
            
            if self.progress_tracker.is_cancelled():
                return
            
            # Save enriched DataFrame
            self.progress_tracker.update(0.8, "Saving results...")
            detections_df.to_csv(output_csv_path, index=False, sep=";")
            
            # Store results in session state
            st.session_state.current_results_df = detections_df
            st.session_state.enriched_csv_path = output_csv_path
            
            # Generate Joypy plot
            if not detections_df.empty:
                self.progress_tracker.update(0.85, "Generating visualization...")
                plot_output_dir = self.output_dir / "figur"
                joypy_output_path = plot_output_dir / "bird_detection_joypy_plot.png"
                create_joypy_plot(df=detections_df, output_path=joypy_output_path)
                st.session_state.joypy_plot_path = joypy_output_path
            
            if self.progress_tracker.is_cancelled():
                return
            
            # Split audio if requested
            if run_audio_splitting and not detections_df.empty:
                self.progress_tracker.update(0.9, "Splitting audio files...")
                split_audio_by_detection(
                    detections_df, 
                    split_audio_output_dir, 
                    max_segments_per_species
                )
                
                # Store audio file paths
                audio_files_dict = {}
                for species_dir in split_audio_output_dir.iterdir():
                    if species_dir.is_dir():
                        species_name = species_dir.name
                        audio_files = list(species_dir.glob("*.wav"))
                        if audio_files:
                            audio_files_dict[species_name] = sorted(audio_files)
                st.session_state.audio_files_dict = audio_files_dict
            
            # Generate statistics
            self.progress_tracker.update(0.95, "Generating statistics...")
            generate_statistics_report(output_csv_path, logger_file_path)
            
            # Complete
            self.progress_tracker.update(1.0, "Analysis complete!")
            st.session_state.analysis_complete = True
            
            if self.completion_callback:
                self.completion_callback()
                
        except Exception as e:
            self.exception = e
            self.progress_tracker.update(0.0, f"Error: {str(e)}")
            raise


def run_analysis_with_progress(container, 
                              input_dir: Path,
                              output_dir: Path,
                              params: dict) -> bool:
    """
    Run analysis with progress tracking in the UI
    
    Returns:
        True if completed successfully, False otherwise
    """
    progress_tracker = ProgressTracker()
    
    # Create and start analysis thread
    analysis_thread = AnalysisThread(
        input_dir=input_dir,
        output_dir=output_dir,
        params=params,
        progress_tracker=progress_tracker
    )
    
    st.session_state.analysis_thread = analysis_thread
    analysis_thread.start()
    
    # Progress UI
    progress_bar = container.progress(0.0)
    status_text = container.empty()
    cancel_button = container.button("🛑 Cancel Analysis", key="cancel_analysis")
    
    # Monitor progress
    while analysis_thread.is_alive():
        if cancel_button or st.session_state.cancel_requested:
            progress_tracker.request_cancel()
            status_text.text("Cancelling analysis...")
            analysis_thread.join(timeout=5.0)
            if analysis_thread.is_alive():
                status_text.error("Failed to cancel analysis gracefully")
            else:
                status_text.warning("Analysis cancelled")
            return False
        
        progress, status = progress_tracker.get_progress()
        progress_bar.progress(progress)
        status_text.text(status)
        
        # Update session state
        st.session_state.analysis_progress = progress
        st.session_state.analysis_status = status
        
        time.sleep(0.1)
    
    # Check for exceptions
    if analysis_thread.exception:
        status_text.error(f"Analysis failed: {analysis_thread.exception}")
        return False
    
    progress_bar.progress(1.0)
    status_text.success("Analysis completed successfully!")
    return True