import pandas as pd
from pathlib import Path
import logging

# Import pydub
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from tqdm import tqdm


def split_audio_by_detection(
    detections_df: pd.DataFrame,
    output_base_dir_path: Path,
    max_segments_per_species: int = 10,
):
    """
    Creates folders for each species and saves audio segments based on detections.
    Selects the highest confidence detections for each species up to the maximum limit.

    Args:
        detections_df: DataFrame containing detection information
        output_base_dir_path: Base directory to output split audio files
        max_segments_per_species: Maximum number of segments to save per species
    """
    if not output_base_dir_path.exists():
        output_base_dir_path.mkdir(parents=True, exist_ok=True)
        logging.info(
            f"Created base output directory for split audio: {output_base_dir_path}"
        )

    if detections_df is None or detections_df.empty:
        logging.info(
            "No detections provided to split_audio_by_detection. Nothing to do."
        )
        return

    # Required columns including confidence for ranking
    required_columns = [
        "filepath",
        "start_time",
        "end_time",
        "Species_NorwegianName",
        "filename",
        "confidence",
    ]
    for col in required_columns:
        if col not in detections_df.columns:
            logging.error(
                f"Missing required column '{col}' in detections DataFrame. Cannot proceed with splitting."
            )
            return

    logging.info(
        f"Starting confidence-based audio splitting for {len(detections_df)} detections (max {max_segments_per_species} per species)."
    )

    # Group by species and select top confidence detections for each species
    selected_detections = (
        detections_df.groupby("Species_NorwegianName")
        .apply(
            lambda group: group.nlargest(max_segments_per_species, "confidence")
        )
        .reset_index(drop=True)
    )

    if selected_detections.empty:
        logging.info("No detections selected after confidence-based filtering.")
        return

    logging.info(
        f"Selected {len(selected_detections)} high-confidence detections for audio splitting."
    )

    # Process each selected detection for audio splitting
    for index, row in tqdm(
        selected_detections.iterrows(),
        total=selected_detections.shape[0],
        desc="Splitting Audio Files",
        unit="segment",
    ):
        original_file_path_str = row["filepath"]
        original_file_path = Path(original_file_path_str)
        start_time_seconds = row["start_time"]
        end_time_seconds = row["end_time"]
        species_norwegian_name = row["Species_NorwegianName"]
        original_filename_stem = Path(row["filename"]).stem
        confidence = row["confidence"]

        if not original_file_path.exists():
            logging.warning(
                f"Original audio file not found: {original_file_path}. Skipping detection from this file."
            )
            continue

        if (
            pd.isna(species_norwegian_name)
            or not species_norwegian_name.strip()
        ):
            logging.warning(
                f"Skipping detection for '{original_filename_stem}' at {start_time_seconds}-{end_time_seconds}s due to missing Norwegian species name."
            )
            continue

        # Sanitize species name for folder creation
        sane_species_folder_name = (
            species_norwegian_name.replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        species_output_dir = output_base_dir_path / sane_species_folder_name
        if not species_output_dir.exists():
            species_output_dir.mkdir(parents=True, exist_ok=True)

        # Convert times to milliseconds for pydub
        start_time_ms = int(start_time_seconds * 1000)
        end_time_ms = int(end_time_seconds * 1000)

        # Construct filename including confidence score
        segment_filename = f"{original_filename_stem}_{start_time_ms}_{end_time_ms}_conf{confidence:.3f}_{sane_species_folder_name}.wav"
        output_segment_path = species_output_dir / segment_filename

        try:
            sound = AudioSegment.from_file(original_file_path)
            segment = sound[start_time_ms:end_time_ms]
            segment.export(output_segment_path, format="wav")
            logging.info(
                f"Successfully saved segment (confidence: {confidence:.3f}): {output_segment_path}"
            )
        except CouldntDecodeError:
            logging.error(
                f"pydub CouldntDecodeError: Failed to load or decode '{original_file_path}'. Ensure ffmpeg is installed and the file is a valid audio format. Skipping this segment."
            )
        except FileNotFoundError:
            logging.error(
                f"pydub FileNotFoundError: Original audio file '{original_file_path}' not found during segment export. This might indicate an issue with the path or file access. Skipping this segment."
            )
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while splitting '{original_file_path}' for segment {output_segment_path}: {e}",
                exc_info=True,
            )

    logging.info("Confidence-based audio splitting process completed.")


if __name__ == "__main__":
    # This is a placeholder for testing the function directly if needed.
    # You would create a dummy DataFrame and call split_audio_by_detection.
    pass
