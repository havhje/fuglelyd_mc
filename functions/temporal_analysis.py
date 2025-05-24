import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import re


def extract_timestamp_from_filename(filename: str) -> Optional[datetime]:
    """
    Extract datetime from various audio filename timestamp formats

    Supported formats:
    - 2MA06968_20250521_190002.wav (YYYYMMDD_HHMMSS)
    - recording_2025-05-21_19-00-02.wav (YYYY-MM-DD_HH-MM-SS)
    - audio_20250521T190002.wav (YYYYMMDDTHHMMSS)
    - 20250521_190002_logger.wav (YYYYMMDD_HHMMSS)
    - sound_2025_05_21_19_00_02.wav (YYYY_MM_DD_HH_MM_SS)

    Args:
        filename: Audio filename

    Returns:
        datetime object or None if parsing fails
    """
    patterns = [
        # Pattern 1: YYYYMMDD_HHMMSS (current format)
        (r"_(\d{8})_(\d{6})", "%Y%m%d_%H%M%S"),
        # Pattern 2: YYYY-MM-DD_HH-MM-SS
        (r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})", "%Y-%m-%d_%H-%M-%S"),
        # Pattern 3: YYYYMMDDTHHMMSS (ISO-like)
        (r"(\d{8})T(\d{6})", "%Y%m%dT%H%M%S"),
        # Pattern 4: YYYYMMDD_HHMMSS at start
        (r"^(\d{8})_(\d{6})", "%Y%m%d_%H%M%S"),
        # Pattern 5: YYYY_MM_DD_HH_MM_SS (underscore separated)
        (r"(\d{4}_\d{2}_\d{2})_(\d{2}_\d{2}_\d{2})", "%Y_%m_%d_%H_%M_%S"),
        # Pattern 6: YYYY-MM-DD-HH-MM-SS (all dashes)
        (r"(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})", "%Y-%m-%d-%H-%M-%S"),
        # Pattern 7: YYYYMMDDHHMM (no seconds)
        (r"_(\d{8})(\d{4})(?![\d])", "%Y%m%d%H%M"),
        # Pattern 8: Unix timestamp (10 digits)
        (r"(\d{10})", "unix"),
    ]

    for pattern, format_str in patterns:
        try:
            match = re.search(pattern, filename)
            if match:
                if format_str == "unix":
                    # Unix timestamp
                    timestamp = int(match.group(1))
                    return datetime.fromtimestamp(timestamp)
                elif len(match.groups()) == 2:
                    # Two groups (date and time)
                    date_time_str = f"{match.group(1)}_{match.group(2)}"
                    return datetime.strptime(date_time_str, format_str)
                else:
                    # Single group
                    return datetime.strptime(match.group(1), format_str)
        except Exception:
            continue

    # Log warning if no pattern matched
    logging.warning(f"Could not parse timestamp from filename: {filename}")
    return None


def add_real_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add real datetime timestamps to detection data based on filename parsing

    Args:
        df: Detection DataFrame with filename and start_time/end_time columns

    Returns:
        DataFrame with real datetime columns added
    """
    df_updated = df.copy()

    # Extract recording start time from filename
    df_updated["recording_start_datetime"] = df_updated["filename"].apply(extract_timestamp_from_filename)

    # Calculate real detection timestamps
    df_updated["detection_datetime"] = df_updated.apply(
        lambda row: row["recording_start_datetime"] + timedelta(seconds=row["start_time"])
        if pd.notnull(row["recording_start_datetime"])
        else None,
        axis=1,
    )

    df_updated["detection_end_datetime"] = df_updated.apply(
        lambda row: row["recording_start_datetime"] + timedelta(seconds=row["end_time"])
        if pd.notnull(row["recording_start_datetime"])
        else None,
        axis=1,
    )

    # Add time-based features for analysis
    df_updated["hour_of_day"] = df_updated["detection_datetime"].dt.hour
    df_updated["day_of_year"] = df_updated["detection_datetime"].dt.dayofyear
    df_updated["is_dawn_chorus"] = df_updated["hour_of_day"].between(4, 8)  # 4-8 AM
    df_updated["is_evening_activity"] = df_updated["hour_of_day"].between(17, 21)  # 5-9 PM
    df_updated["date"] = df_updated["detection_datetime"].dt.date
    df_updated["time_of_day"] = df_updated["detection_datetime"].dt.time

    return df_updated


def analyze_daily_activity_patterns(df: pd.DataFrame) -> Dict:
    """
    Analyze bird activity patterns by time of day
    """
    if df.empty or "hour_of_day" not in df.columns:
        return {}

    # Overall activity by hour
    hourly_activity = df.groupby("hour_of_day").size().to_dict()

    # Species richness by hour (number of unique species)
    hourly_richness = df.groupby("hour_of_day")["Species_NorwegianName"].nunique().to_dict()

    # Dawn chorus participants (4-8 AM)
    dawn_species = df[df["is_dawn_chorus"] == True]["Species_NorwegianName"].value_counts().to_dict()

    # Evening activity participants (5-9 PM)
    evening_species = df[df["is_evening_activity"] == True]["Species_NorwegianName"].value_counts().to_dict()

    return {
        "hourly_activity": hourly_activity,
        "hourly_species_richness": hourly_richness,
        "dawn_chorus_species": dawn_species,
        "evening_activity_species": evening_species,
        "peak_activity_hour": max(hourly_activity, key=hourly_activity.get) if hourly_activity else None,
        "peak_richness_hour": max(hourly_richness, key=hourly_richness.get) if hourly_richness else None,
    }


def analyze_species_temporal_patterns(df: pd.DataFrame) -> Dict:
    """
    Analyze detailed temporal patterns for individual species
    """
    if df.empty or "detection_datetime" not in df.columns:
        return {}

    species_patterns = {}

    for species in df["Species_NorwegianName"].unique():
        if pd.isna(species):
            continue

        species_data = df[df["Species_NorwegianName"] == species].copy()

        if len(species_data) == 0:
            continue

        # Sort by detection time for analysis
        species_data = species_data.sort_values("detection_datetime")

        detection_count = len(species_data)

        # 1. Peak Activity Window (1-hour window with most detections)
        peak_activity_window = None
        max_detections_in_hour = 0

        if "hour_of_day" in species_data.columns:
            hourly_counts = species_data["hour_of_day"].value_counts()
            if not hourly_counts.empty:
                peak_hour = hourly_counts.idxmax()
                max_detections_in_hour = hourly_counts.max()
                peak_activity_window = (
                    f"{peak_hour:02d}:00-{(peak_hour + 1):02d}:00 ({max_detections_in_hour} detections)"
                )

        # 2. Active Period (first to last detection)
        active_period = None
        active_duration = None

        detection_times = species_data["detection_datetime"].dropna()
        if len(detection_times) > 0:
            first_detection = detection_times.min()
            last_detection = detection_times.max()

            if len(detection_times) > 1:
                duration = last_detection - first_detection
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)

                first_time = first_detection.strftime("%H:%M")
                last_time = last_detection.strftime("%H:%M")

                if hours > 0:
                    duration_str = f"{hours}h {minutes}m"
                else:
                    duration_str = f"{minutes}m"

                active_period = f"{first_time}-{last_time} ({duration_str})"
                active_duration = duration.total_seconds() / 60  # minutes
            else:
                # Single detection
                single_time = first_detection.strftime("%H:%M")
                active_period = f"{single_time} (single detection)"
                active_duration = 0

        # 3. Call Pattern Analysis
        call_pattern = None
        avg_gap_minutes = None
        gap_stats = None

        if len(detection_times) > 1:
            # Calculate time gaps between consecutive detections
            time_diffs = detection_times.diff().dt.total_seconds().dropna()
            gap_minutes = time_diffs / 60

            avg_gap_minutes = gap_minutes.mean()
            min_gap = gap_minutes.min()
            max_gap = gap_minutes.max()
            std_gap = gap_minutes.std()

            # Classify call pattern based on average gap
            if avg_gap_minutes < 5:
                pattern_type = "Clustered"
            elif avg_gap_minutes < 15:
                pattern_type = "Regular"
            else:
                pattern_type = "Sporadic"

            # Create detailed call pattern string
            call_pattern = f"{pattern_type} (avg {avg_gap_minutes:.1f} min gaps, range: {min_gap:.1f}-{max_gap:.1f} min, std: {std_gap:.1f} min)"

            gap_stats = {
                "avg": round(avg_gap_minutes, 1),
                "min": round(min_gap, 1),
                "max": round(max_gap, 1),
                "std": round(std_gap, 1),
            }
        elif len(detection_times) == 1:
            call_pattern = "Single call"

        species_patterns[species] = {
            "detection_count": detection_count,
            "peak_activity_window": peak_activity_window,
            "active_period": active_period,
            "active_duration_minutes": round(active_duration, 1) if active_duration is not None else None,
            "call_pattern": call_pattern,
            "gap_statistics": gap_stats,
        }

    return species_patterns


def analyze_recording_sessions(df: pd.DataFrame) -> Dict:
    """
    Analyze recording session patterns and coverage
    """
    if df.empty or "recording_start_datetime" not in df.columns:
        return {}

    session_data = df.dropna(subset=["recording_start_datetime"])
    if session_data.empty:
        return {}

    # Unique recording sessions
    unique_sessions = session_data["recording_start_datetime"].unique()

    # Time span analysis
    earliest = session_data["detection_datetime"].min()
    latest = session_data["detection_datetime"].max()
    total_span = latest - earliest if earliest and latest else None

    # Daily coverage
    dates = session_data["date"].unique()

    return {
        "total_sessions": len(unique_sessions),
        "dates_covered": len(dates),
        "time_span_hours": total_span.total_seconds() / 3600 if total_span else 0,
        "earliest_detection": earliest.strftime("%Y-%m-%d %H:%M:%S") if earliest else None,
        "latest_detection": latest.strftime("%Y-%m-%d %H:%M:%S") if latest else None,
        "session_start_times": [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in unique_sessions],
    }


def analyze_rare_species_timing(df: pd.DataFrame) -> Dict:
    """
    Analyze temporal patterns of rare and endangered species
    """
    if df.empty or "Redlist_Status" not in df.columns:
        return {}

    # Focus on threatened species (CR, EN, VU, NT)
    threatened_statuses = ["CR", "EN", "VU", "NT"]
    rare_species_data = df[df["Redlist_Status"].isin(threatened_statuses)]

    if rare_species_data.empty:
        return {}

    rare_patterns = {}

    for species in rare_species_data["Species_NorwegianName"].unique():
        species_data = rare_species_data[rare_species_data["Species_NorwegianName"] == species]
        status = species_data["Redlist_Status"].iloc[0]

        detection_times = []
        if "detection_datetime" in species_data.columns:
            detection_times = species_data["detection_datetime"].dropna().dt.strftime("%H:%M").tolist()

        rare_patterns[species] = {
            "redlist_status": status,
            "detection_count": len(species_data),
            "detection_times": detection_times,
            "avg_confidence": round(species_data["confidence"].mean(), 3),
            "peak_hour": species_data["hour_of_day"].mode().iloc[0]
            if "hour_of_day" in species_data.columns and not species_data.empty
            else None,
        }

    return rare_patterns


def generate_temporal_summary(df: pd.DataFrame, logger_file_path: str = None) -> Dict:
    """
    Generate comprehensive temporal analysis summary based on filename timestamps

    Args:
        df: Detection DataFrame with filename column containing timestamps
        logger_file_path: Ignored - kept for compatibility with existing code

    Returns:
        Dictionary containing all temporal analysis results
    """
    # Add timestamps from filenames
    df_with_time = add_real_timestamps(df)

    # Perform all analyses
    results = {
        "session_analysis": analyze_recording_sessions(df_with_time),
        "daily_patterns": analyze_daily_activity_patterns(df_with_time),
        "species_patterns": analyze_species_temporal_patterns(df_with_time),
        "rare_species_timing": analyze_rare_species_timing(df_with_time),
        "timestamp_parsing": {
            "total_detections": len(df),
            "successfully_parsed": len(df_with_time.dropna(subset=["recording_start_datetime"])),
            "parsing_success_rate": round(
                len(df_with_time.dropna(subset=["recording_start_datetime"])) / len(df) * 100, 1
            )
            if len(df) > 0
            else 0,
        },
    }

    return results


def print_temporal_analysis(temporal_results: Dict) -> None:
    """
    Print formatted temporal analysis results
    """
    if not temporal_results:
        print("No temporal analysis results to display.")
        return

    print("\n" + "=" * 60)
    print("TEMPORAL BIRD ACTIVITY ANALYSIS")
    print("=" * 60)

    # Timestamp parsing status
    parsing = temporal_results.get("timestamp_parsing", {})
    if parsing:
        print(f"\nTimestamp Parsing:")
        print(f"  Total detections: {parsing['total_detections']}")
        print(f"  Successfully parsed: {parsing['successfully_parsed']}")
        print(f"  Success rate: {parsing['parsing_success_rate']}%")

    # Recording session overview
    session_analysis = temporal_results.get("session_analysis", {})
    if session_analysis:
        print(f"\nRecording Sessions:")
        print(f"  Total sessions: {session_analysis['total_sessions']}")
        print(f"  Days covered: {session_analysis['dates_covered']}")
        print(f"  Time span: {session_analysis['time_span_hours']:.1f} hours")
        if session_analysis.get("earliest_detection") and session_analysis.get("latest_detection"):
            print(f"  Period: {session_analysis['earliest_detection']} to {session_analysis['latest_detection']}")

    # Show hourly activity distribution first
    daily = temporal_results.get("daily_patterns", {})
    if daily and daily.get("hourly_activity"):
        hourly = daily["hourly_activity"]
        print(f"\nHourly Activity Distribution:")

        # Calculate proper scaling for the bars
        max_count = max(hourly.values()) if hourly else 1
        scale_factor = max(1, max_count // 20)  # Scale so max bar is ~20 chars

        for hour in sorted(hourly.keys()):
            count = hourly[hour]
            bar_length = max(1, count // scale_factor)  # Ensure at least 1 char for any detection
            bar = "█" * min(bar_length, 20)
            print(f"  {hour:02d}:00 - {count:3d} detections {bar}")

    # Species temporal patterns
    species_patterns = temporal_results.get("species_patterns", {})
    if species_patterns:
        print(f"\nSPECIES TEMPORAL PROFILES:")

        # Sort species by detection count (most active first)
        sorted_species = sorted(species_patterns.items(), key=lambda x: x[1]["detection_count"], reverse=True)

        for species, data in sorted_species:
            print(f"\n{species}:")
            if data.get("peak_activity_window"):
                print(f"  Peak activity: {data['peak_activity_window']}")
            if data.get("active_period"):
                print(f"  Active period: {data['active_period']}")
            if data.get("call_pattern"):
                print(f"  Call pattern: {data['call_pattern']}")

    print("\n" + "=" * 60)
