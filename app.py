import streamlit as st
import pandas as pd
import os
from datetime import datetime, date as date_type
from pathlib import Path
import subprocess
import json

# Import analysis functions
from functions.birdnetlib_api import run_birdnet_analysis, on_analyze_directory_complete
from functions.artskart_api import fetch_artskart_taxon_info_by_name
from functions.splitter_lydfilen import split_audio_by_detection
from functions.statistics import generate_statistics_report
from functions.joy2_tester import create_joypy_plot

st.set_page_config(
    page_title="Bird Sound Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "output_dir" not in st.session_state:
    st.session_state.output_dir = None

# Title
st.title("Bird Sound Analysis")
st.divider()

# Input Configuration Section
st.header("Configuration")

# Folder pickers side by side
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Directory")
    
    # Initialize browse path
    if "browse_path" not in st.session_state:
        st.session_state.browse_path = str(Path.home())
    if "selected_input_dir" not in st.session_state:
        st.session_state.selected_input_dir = ""
    
    current_path = Path(st.session_state.browse_path)
    
    # Show current selection
    if st.session_state.selected_input_dir:
        st.info(f"Selected: {st.session_state.selected_input_dir}")
    
    # Create navigation options
    nav_options = []
    if current_path.parent != current_path:
        nav_options.append((".. (Parent Directory)", str(current_path.parent)))
    
    # Add subdirectories
    try:
        subdirs = sorted([d for d in current_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
        for subdir in subdirs[:25]:
            nav_options.append((subdir.name, str(subdir)))
    except PermissionError:
        st.error("Permission denied")
    
    if nav_options:
        # Navigation selectbox
        selected = st.selectbox(
            f"Current: {current_path}",
            options=[opt[1] for opt in nav_options],
            format_func=lambda x: next(opt[0] for opt in nav_options if opt[1] == x),
            key="folder_nav"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Navigate", use_container_width=True):
                st.session_state.browse_path = selected
                st.rerun()
        with col_b:
            if st.button("Select", type="primary", use_container_width=True):
                st.session_state.selected_input_dir = st.session_state.browse_path
                st.rerun()
    
    # Set input_dir from selection
    input_dir = st.session_state.selected_input_dir

with col2:
    st.subheader("Output Directory")
    
    # Initialize output browse path
    if "output_browse_path" not in st.session_state:
        st.session_state.output_browse_path = str(Path.home())
    if "selected_output_dir" not in st.session_state:
        st.session_state.selected_output_dir = ""
    
    output_current_path = Path(st.session_state.output_browse_path)
    
    # Show current selection
    if st.session_state.selected_output_dir:
        st.info(f"Selected: {st.session_state.selected_output_dir}")
    
    # Create navigation options for output
    output_nav_options = []
    if output_current_path.parent != output_current_path:
        output_nav_options.append((".. (Parent Directory)", str(output_current_path.parent)))
    
    # Add subdirectories
    try:
        output_subdirs = sorted([d for d in output_current_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
        for subdir in output_subdirs[:25]:
            output_nav_options.append((subdir.name, str(subdir)))
    except PermissionError:
        st.error("Permission denied")
    
    if output_nav_options:
        # Navigation selectbox for output
        output_selected = st.selectbox(
            f"Current: {output_current_path}",
            options=[opt[1] for opt in output_nav_options],
            format_func=lambda x: next(opt[0] for opt in output_nav_options if opt[1] == x),
            key="output_folder_nav"
        )
        
        col_c, col_d = st.columns(2)
        with col_c:
            if st.button("Navigate", use_container_width=True, key="output_navigate"):
                st.session_state.output_browse_path = output_selected
                st.rerun()
        with col_d:
            if st.button("Select", type="primary", use_container_width=True, key="output_select"):
                st.session_state.selected_output_dir = st.session_state.output_browse_path
                st.rerun()
    
    # Set output_dir from selection
    output_dir = st.session_state.selected_output_dir

st.divider()

# Analysis configuration below
col3, col4 = st.columns([1, 2])

with col3:
    analysis_mode = st.radio(
        "Analysis Mode",
        ["Location-based", "Species List"],
        help="Choose analysis method"
    )
    
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Minimum confidence for detections"
    )

with col4:
    # Mode-specific inputs
    if analysis_mode == "Location-based":
        st.subheader("Location Settings")
        loc_col1, loc_col2, loc_col3 = st.columns(3)
        with loc_col1:
            latitude = st.number_input("Latitude", value=59.91, format="%.4f")
        with loc_col2:
            longitude = st.number_input("Longitude", value=10.75, format="%.4f")
        with loc_col3:
            date = st.date_input("Date", value=datetime.now().date())
    else:
        st.subheader("Species List")
        species_list = st.text_area(
            "Enter species names (one per line)",
            placeholder="Scientific names, one per line",
            height=150,
            label_visibility="collapsed"
        )

st.divider()

# Analysis Execution Section
st.header("Analysis")

if st.button("Run Analysis", type="primary", use_container_width=True):
    # Validate inputs
    if not input_dir or not os.path.exists(input_dir):
        st.error("Please select an input directory")
    else:
        # Use selected output directory or auto-generate
        if not output_dir:
            output_dir = os.path.join(
                os.path.dirname(input_dir),
                f"{os.path.basename(input_dir)}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
        else:
            # Create timestamped subfolder in selected output directory
            output_dir = os.path.join(
                output_dir,
                f"{os.path.basename(input_dir)}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        interim_dir = os.path.join(output_dir, "interim")
        os.makedirs(interim_dir, exist_ok=True)
        
        # Store output directory in session state
        st.session_state.output_dir = output_dir
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Analyze audio files
            status_text.text("Analyzing audio files...")
            progress_bar.progress(20)
            
            # Prepare arguments based on mode
            if analysis_mode == "Location-based":
                lat = latitude
                lon = longitude
                # Handle date - st.date_input returns a datetime.date object
                # Convert it to a full datetime object (with time set to midnight)
                if isinstance(date, str):
                    # If somehow we get a string, parse it
                    analysis_date = datetime.strptime(date, "%Y-%m-%d")
                else:
                    # Convert date object to datetime object
                    analysis_date = datetime.combine(date, datetime.min.time())
                custom_species_list = None
            else:
                lat = lon = analysis_date = None
                # Check if species_list is defined (it won't be if Location-based mode was selected)
                if 'species_list' in locals():
                    custom_species_list = [s.strip() for s in species_list.split('\n') if s.strip()]
                else:
                    custom_species_list = None
            
            # Create callback wrapper that includes base_input_path
            def analysis_callback(recordings):
                return on_analyze_directory_complete(recordings, input_dir)
            
            # Run BirdNET analysis
            all_detections = run_birdnet_analysis(
                input_dir,
                analysis_callback,
                lon=lon if analysis_mode == "Location-based" else None,
                lat=lat if analysis_mode == "Location-based" else None,
                analysis_date=analysis_date if analysis_mode == "Location-based" else None,
                min_confidence=confidence_threshold,
                custom_species_list_path=True if analysis_mode == "Species List" else None
            )
            
            if not all_detections:
                st.warning("No bird sounds detected in the audio files.")
                st.stop()
            
            # Convert detections to DataFrame
            detections_df = pd.DataFrame(all_detections)
            
            # Step 2: Enrich with taxonomic data
            status_text.text("Enriching with taxonomic data...")
            progress_bar.progress(40)
            
            # Enrich each detection with Artskart data
            enriched_detections = []
            unique_species = detections_df['common_name'].unique()
            
            for species in unique_species:
                # Get scientific name for this species
                scientific_name = detections_df[detections_df['common_name'] == species]['scientific_name'].iloc[0]
                taxon_info = fetch_artskart_taxon_info_by_name(scientific_name)
                species_detections = detections_df[detections_df['common_name'] == species].copy()
                
                if taxon_info:
                    # Extract Norwegian name from PopularNames list
                    popular_names = taxon_info.get('PopularNames', [])
                    norwegian_name = ''
                    for name_obj in popular_names:
                        if isinstance(name_obj, dict) and name_obj.get('language') in ['nb-NO', 'nn-NO']:
                            norwegian_name = name_obj.get('Name', '')
                            break
                    
                    # Use PrefferedPopularname as fallback
                    if not norwegian_name:
                        norwegian_name = taxon_info.get('PrefferedPopularname', '')
                    
                    species_detections['norsk_navn'] = norwegian_name
                    species_detections['Species_NorwegianName'] = norwegian_name  # For compatibility
                    species_detections['family'] = taxon_info.get('Family', '')
                    species_detections['Family_ScientificName'] = taxon_info.get('Family', '')  # For compatibility
                    species_detections['order'] = taxon_info.get('Order', '')
                    species_detections['Order_ScientificName'] = taxon_info.get('Order', '')  # For compatibility
                    species_detections['redlist_status'] = taxon_info.get('Status', '')
                    species_detections['Redlist_Status'] = taxon_info.get('Status', '')  # For compatibility
                else:
                    species_detections['norsk_navn'] = ''
                    species_detections['Species_NorwegianName'] = ''  # For compatibility
                    species_detections['family'] = ''
                    species_detections['Family_ScientificName'] = ''  # For compatibility
                    species_detections['order'] = ''
                    species_detections['Order_ScientificName'] = ''  # For compatibility
                    species_detections['redlist_status'] = ''
                    species_detections['Redlist_Status'] = ''  # For compatibility
                    
                enriched_detections.append(species_detections)
            
            enriched_df = pd.concat(enriched_detections, ignore_index=True)
            
            # Save enriched results
            enriched_path = os.path.join(interim_dir, "enriched_detections.csv")
            enriched_df.to_csv(enriched_path, index=False)
            
            # Step 3: Split audio files
            status_text.text("Splitting audio files...")
            progress_bar.progress(60)
            
            audio_output_dir = os.path.join(output_dir, "lydfiler")
            os.makedirs(audio_output_dir, exist_ok=True)
            
            # Split audio files based on detections
            split_audio_by_detection(
                enriched_df,
                Path(audio_output_dir),
                max_segments_per_species=10
            )
            
            # Step 4: Generate statistics
            status_text.text("Generating statistics...")
            progress_bar.progress(80)
            
            # Generate statistics report
            stats_output_path = os.path.join(interim_dir, "detection_statistics.txt")
            generate_statistics_report(enriched_df, stats_output_path)
            
            # Step 5: Generate visualization
            status_text.text("Creating visualization...")
            progress_bar.progress(90)
            
            figur_dir = os.path.join(output_dir, "figur")
            os.makedirs(figur_dir, exist_ok=True)
            
            # Generate joyplot
            create_joypy_plot(enriched_df, Path(figur_dir))
            
            # Complete
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            
            # Store results in session state
            st.session_state.analysis_complete = True
            st.session_state.results_df = enriched_df
            
            # Show success message
            st.success(f"Analysis complete! Results saved to: {output_dir}")
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            status_text.text("")
            progress_bar.empty()

st.divider()

# Results Display Section
if st.session_state.analysis_complete and st.session_state.results_df is not None:
    st.header("Results")
    
    df = st.session_state.results_df
    
    # Summary statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Detections", len(df))
    with col2:
        st.metric("Species Detected", df['common_name'].nunique())
    
    # Aggregate results by species
    species_summary = df.groupby(['common_name', 'norsk_navn']).agg({
        'confidence': ['count', 'mean']
    }).round(3)
    species_summary.columns = ['Detection Count', 'Average Confidence']
    species_summary = species_summary.reset_index()
    species_summary = species_summary.sort_values('Detection Count', ascending=False)
    
    # Display table
    st.subheader("Species Summary")
    st.dataframe(
        species_summary,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = species_summary.to_csv(index=False)
    st.download_button(
        label="Download Results (CSV)",
        data=csv,
        file_name=f"bird_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )