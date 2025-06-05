#!/usr/bin/env python3
"""Standalone test script to run bird sound analysis without Streamlit UI.

This script helps debug analysis issues by running the same analysis pipeline
as the Streamlit app but in a controlled, debuggable environment.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from functions.birdnetlib_api import run_birdnet_analysis, on_analyze_directory_complete
from functions.artskart_api import fetch_artskart_taxon_info_by_name
from functions.splitter_lydfilen import split_audio_by_detection
from functions.statistics import generate_statistics_report
from functions.joy2_tester import create_joypy_plot


def test_analysis(
    input_dir: str,
    output_dir: str = None,
    mode: str = "location",
    lat: float = 59.91,
    lon: float = 10.75,
    date: str = None,
    species_list: list = None,
    confidence: float = 0.5
):
    """Run a complete analysis pipeline test.
    
    Args:
        input_dir: Directory containing audio files
        output_dir: Output directory (auto-generated if None)
        mode: "location" or "species_list"
        lat: Latitude for location-based analysis
        lon: Longitude for location-based analysis
        date: Date for location-based analysis (YYYY-MM-DD)
        species_list: List of species for species list mode
        confidence: Minimum confidence threshold
    """
    print(f"\n{'='*60}")
    print("BIRD SOUND ANALYSIS TEST")
    print(f"{'='*60}\n")
    
    # Validate input directory
    if not os.path.exists(input_dir):
        print(f"ERROR: Input directory does not exist: {input_dir}")
        return False
    
    # Auto-generate output directory if not provided
    if not output_dir:
        output_dir = os.path.join(
            os.path.dirname(input_dir),
            f"{os.path.basename(input_dir)}_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    interim_dir = os.path.join(output_dir, "interim")
    os.makedirs(interim_dir, exist_ok=True)
    
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Analysis mode: {mode}")
    print(f"Confidence threshold: {confidence}")
    
    try:
        # Step 1: Analyze audio files
        print("\n[1/5] Running BirdNET analysis...")
        
        # Prepare arguments based on mode
        if mode == "location":
            analysis_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
            print(f"  Location: {lat}, {lon}")
            print(f"  Date: {analysis_date.strftime('%Y-%m-%d')}")
            custom_species_list_path = None
        else:
            lat = lon = analysis_date = None
            custom_species_list_path = True
            print(f"  Using species list mode")
        
        # Create callback wrapper
        def analysis_callback(recordings):
            return on_analyze_directory_complete(recordings, input_dir)
        
        # Run BirdNET analysis
        all_detections = run_birdnet_analysis(
            input_dir,
            analysis_callback,
            lon=lon,
            lat=lat,
            analysis_date=analysis_date,
            min_confidence=confidence,
            custom_species_list_path=custom_species_list_path
        )
        
        if not all_detections:
            print("  No bird sounds detected!")
            return False
        
        print(f"  Found {len(all_detections)} detections")
        
        # Convert to DataFrame
        detections_df = pd.DataFrame(all_detections)
        print(f"  Columns in raw detections: {list(detections_df.columns)}")
        
        # Step 2: Enrich with taxonomic data
        print("\n[2/5] Enriching with taxonomic data...")
        
        enriched_detections = []
        unique_species = detections_df['common_name'].unique()
        print(f"  Found {len(unique_species)} unique species")
        
        for i, species in enumerate(unique_species):
            # Get scientific name for this species
            scientific_name = detections_df[detections_df['common_name'] == species]['scientific_name'].iloc[0]
            print(f"  Processing {i+1}/{len(unique_species)}: {species} ({scientific_name})")
            taxon_info = fetch_artskart_taxon_info_by_name(scientific_name)
            species_detections = detections_df[detections_df['common_name'] == species].copy()
            
            if taxon_info:
                # Debug: print what we got from API
                print(f"    API returned keys: {list(taxon_info.keys())[:10]}...")  # First 10 keys
                
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
                    if not norwegian_name:
                        print(f"    WARNING: No Norwegian name found")
                
                # Add both column name formats for compatibility
                species_detections['norsk_navn'] = norwegian_name
                species_detections['Species_NorwegianName'] = norwegian_name
                species_detections['family'] = taxon_info.get('Family', '')
                species_detections['Family_ScientificName'] = taxon_info.get('Family', '')
                species_detections['order'] = taxon_info.get('Order', '')
                species_detections['Order_ScientificName'] = taxon_info.get('Order', '')
                species_detections['redlist_status'] = taxon_info.get('Status', '')
                species_detections['Redlist_Status'] = taxon_info.get('Status', '')
            else:
                print(f"    WARNING: No taxonomic data found for {species}")
                species_detections['norsk_navn'] = ''
                species_detections['Species_NorwegianName'] = ''
                species_detections['family'] = ''
                species_detections['Family_ScientificName'] = ''
                species_detections['order'] = ''
                species_detections['Order_ScientificName'] = ''
                species_detections['redlist_status'] = ''
                species_detections['Redlist_Status'] = ''
            
            enriched_detections.append(species_detections)
        
        enriched_df = pd.concat(enriched_detections, ignore_index=True)
        print(f"  Enriched DataFrame has {len(enriched_df)} rows")
        print(f"  Columns after enrichment: {list(enriched_df.columns)}")
        
        # Save enriched results
        enriched_path = os.path.join(interim_dir, "enriched_detections.csv")
        enriched_df.to_csv(enriched_path, index=False)
        print(f"  Saved to: {enriched_path}")
        
        # Step 3: Split audio files
        print("\n[3/5] Splitting audio files...")
        
        audio_output_dir = os.path.join(output_dir, "lydfiler")
        os.makedirs(audio_output_dir, exist_ok=True)
        
        # Check required columns for splitting
        required_cols = ['filepath', 'start_time', 'end_time', 'Species_NorwegianName', 'filename', 'confidence']
        missing_cols = [col for col in required_cols if col not in enriched_df.columns]
        if missing_cols:
            print(f"  ERROR: Missing required columns for splitting: {missing_cols}")
            print(f"  Available columns: {list(enriched_df.columns)}")
        else:
            split_audio_by_detection(
                enriched_df,
                Path(audio_output_dir),
                max_segments_per_species=10
            )
            print(f"  Audio files saved to: {audio_output_dir}")
        
        # Step 4: Generate statistics
        print("\n[4/5] Generating statistics...")
        
        stats_output_path = os.path.join(interim_dir, "detection_statistics.txt")
        generate_statistics_report(enriched_df, stats_output_path)
        print(f"  Statistics saved to: {stats_output_path}")
        
        # Step 5: Generate visualization
        print("\n[5/5] Creating visualization...")
        
        figur_dir = os.path.join(output_dir, "figur")
        os.makedirs(figur_dir, exist_ok=True)
        
        create_joypy_plot(enriched_df, Path(figur_dir))
        print(f"  Visualization saved to: {figur_dir}")
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETED SUCCESSFULLY!")
        print(f"Results saved to: {output_dir}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n{'='*60}")
        print("ERROR DURING ANALYSIS!")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return False


if __name__ == "__main__":
    # Example usage - modify these paths for your testing
    
    # Use the specified test directory with smaller file
    input_path = "/Users/havardhjermstad-sollerud/Desktop/data_input_lyd"
    
    # Run test
    if os.path.exists(input_path):
        print(f"Testing with input directory: {input_path}")
        success = test_analysis(
            input_dir=input_path,
            mode="location",
            lat=59.91,
            lon=10.75,
            confidence=0.5
        )
        sys.exit(0 if success else 1)
    else:
        print("No test data found. Please specify an input directory.")
        print("\nUsage:")
        print("  python test_analysis_standalone.py")
        print("\nModify the input_path variable in the script to point to your audio files.")
        sys.exit(1)