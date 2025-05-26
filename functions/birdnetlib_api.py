from birdnetlib.analyzer import Analyzer
from birdnetlib.batch import DirectoryMultiProcessingAnalyzer
from datetime import datetime
from pathlib import Path
import logging


def on_analyze_directory_complete(recordings, base_input_path):
    all_detections = []  # Initialize an empty list to store all detections

    for recording in recordings:
        if recording.error:
            print("Error processing this recording:", recording.error_message)
        else:
            # Augment and collect detections
            for detection in recording.detections:
                # Create a new dictionary to avoid modifying the original
                augmented_detection = detection.copy()
                # Add the filename from the recording path
                augmented_detection["filepath"] = str(recording.path)
                augmented_detection["filename"] = Path(recording.path).name
                all_detections.append(augmented_detection)

    return all_detections


def run_birdnet_analysis(
    directory_to_analyze,
    callback_func_from_main,
    lon=7.0070,
    lat=59.4451,
    analysis_date=None,
    min_confidence=0.01,
    custom_species_list_path=None,
):
    """
    Run BirdNET analysis on audio files in the specified directory.

    Args:
        directory_to_analyze: Path to directory with audio files
        callback_func_from_main: Callback function to process detections
        lon: Longitude for analysis location (ignored if custom_species_list_path is provided)
        lat: Latitude for analysis location (ignored if custom_species_list_path is provided)
        analysis_date: Date of recording for seasonal adjustments (datetime object, ignored if custom_species_list_path is provided)
        min_confidence: Minimum confidence threshold for detections (0.0-1.0)
        custom_species_list_path: Path to custom species list file (optional)

    Returns:
        List of detection dictionaries
    """
    # Use current date if none specified
    if analysis_date is None:
        analysis_date = datetime.now()

    detections_container = []  # This list will store the final detections.

    def analysis_complete_wrapper(recordings_from_birdnet):
        # This wrapper is called by birdnetlib when analysis of all files is complete.
        # It receives the list of Recording objects.
        # callback_func_from_main is on_analyze_directory_complete(recordings,
        # base_input_path=...)
        # It processes these recordings and returns a list of detection dicts.
        count = len(recordings_from_birdnet) if recordings_from_birdnet else 0
        logging.debug(
            f"Analysis complete wrapper called with {count} recordings."
        )
        processed_detections = callback_func_from_main(recordings_from_birdnet)
        if processed_detections:
            logging.debug(
                f"Callback processed {len(processed_detections)} detections."
            )
            detections_container.extend(processed_detections)
        elif processed_detections is None:
            logging.info("User callback returned None.")
        else:  # Empty list
            logging.info("User callback returned an empty list of detections.")

    # Handle custom species list vs location-based analysis
    if custom_species_list_path:
        # Validate custom species list file exists
        species_list_path = Path(custom_species_list_path)
        if not species_list_path.exists():
            raise FileNotFoundError(
                f"Custom species list file not found: {custom_species_list_path}"
            )

        logging.info(f"Using custom species list: {custom_species_list_path}")
        logging.info(
            "Note: Location parameters (lat/lon/date) are ignored when using custom species list"
        )

        # Create analyzer with custom species list
        analyzer = Analyzer(custom_species_list_path=str(species_list_path))

        # Create batch analyzer without location parameters
        batch = DirectoryMultiProcessingAnalyzer(
            directory_to_analyze,
            analyzers=[analyzer],
            min_conf=min_confidence,
        )
    else:
        # Standard location-based analysis
        logging.info(
            f"Using location-based analysis: {lat}°N, {lon}°E on {analysis_date.strftime('%Y-%m-%d')}"
        )

        # Create standard analyzer
        analyzer = Analyzer()

        # Create batch analyzer with location parameters
        batch = DirectoryMultiProcessingAnalyzer(
            directory_to_analyze,
            analyzers=[analyzer],
            lon=lon,
            lat=lat,
            date=analysis_date,
            min_conf=min_confidence,
        )

    batch.on_analyze_directory_complete = (
        analysis_complete_wrapper  # Assign wrapper
    )
    logging.info("Starting batch processing of audio files...")
    batch.process()  # Triggers analysis_complete_wrapper
    logging.info("Batch processing finished.")

    log_msg = f"Returning {len(detections_container)} detections from run_birdnet_analysis."
    logging.info(log_msg)
    return detections_container  # Return the populated list
