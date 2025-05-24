import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from .temporal_analysis import generate_temporal_summary, print_temporal_analysis


def calculate_summary_statistics(df: pd.DataFrame, logger_file_path: str = None) -> Dict:
    """
    Calculate summary statistics from the detection DataFrame
    
    Args:
        df: DataFrame containing enriched detection data
        logger_file_path: Optional path to logger CSV file for real timestamp analysis
        
    Returns:
        Dictionary containing various summary statistics
    """
    if df is None or df.empty:
        logging.warning("Cannot calculate statistics: DataFrame is empty or None")
        return {}
    
    stats = {}
    
    # Total number of observations
    stats["total_observations"] = len(df)
    
    # Number of observations per species (using Norwegian name)
    species_counts = df["Species_NorwegianName"].value_counts().to_dict()
    stats["observations_per_species"] = species_counts
    
    # Top 10 most detected species
    stats["top_species"] = dict(sorted(species_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    # Number of unique species
    stats["unique_species_count"] = df["Species_NorwegianName"].nunique()
    
    # Confidence score statistics
    if "confidence" in df.columns:
        stats["confidence_overall"] = {
            "mean": round(df["confidence"].mean(), 3),
            "median": round(df["confidence"].median(), 3),
            "min": round(df["confidence"].min(), 3),
            "max": round(df["confidence"].max(), 3),
            "std": round(df["confidence"].std(), 3)
        }
        
        # Confidence statistics by species
        confidence_by_species = {}
        for species in df["Species_NorwegianName"].unique():
            if pd.isna(species):
                continue
            species_df = df[df["Species_NorwegianName"] == species]
            confidence_by_species[species] = {
                "mean": round(species_df["confidence"].mean(), 3),
                "median": round(species_df["confidence"].median(), 3),
                "min": round(species_df["confidence"].min(), 3),
                "max": round(species_df["confidence"].max(), 3),
                "count": len(species_df)
            }
        stats["confidence_by_species"] = confidence_by_species
        
        # Confidence distribution bands
        very_high = df[df["confidence"] >= 0.9]
        high = df[(df["confidence"] >= 0.7) & (df["confidence"] < 0.9)]
        medium = df[(df["confidence"] >= 0.5) & (df["confidence"] < 0.7)]
        low = df[df["confidence"] < 0.5]
        
        stats["confidence_distribution"] = {
            "very_high": {"count": len(very_high), "percentage": round((len(very_high) / len(df)) * 100, 1)},
            "high": {"count": len(high), "percentage": round((len(high) / len(df)) * 100, 1)},
            "medium": {"count": len(medium), "percentage": round((len(medium) / len(df)) * 100, 1)},
            "low": {"count": len(low), "percentage": round((len(low) / len(df)) * 100, 1)}
        }
        
        # High confidence detections (>0.8) with species breakdown
        high_conf_df = df[df["confidence"] > 0.8]
        stats["high_confidence_detections"] = {
            "count": len(high_conf_df),
            "percentage": round((len(high_conf_df) / len(df)) * 100, 1),
            "species_breakdown": high_conf_df["Species_NorwegianName"].value_counts().to_dict()
        }
        
        # Confidence by redlist status
        if "Redlist_Status" in df.columns:
            confidence_by_redlist = {}
            for status in df["Redlist_Status"].unique():
                if pd.isna(status):
                    continue
                status_df = df[df["Redlist_Status"] == status]
                confidence_by_redlist[status] = {
                    "mean": round(status_df["confidence"].mean(), 3),
                    "count": len(status_df)
                }
            stats["confidence_by_redlist_status"] = confidence_by_redlist
    
    # Observations by redlist status
    redlist_counts = df["Redlist_Status"].value_counts().to_dict()
    stats["observations_per_redlist_status"] = redlist_counts
    
    # Species by redlist status
    redlist_species = {}
    for status in df["Redlist_Status"].unique():
        if pd.isna(status):
            continue
        # Get subset of dataframe with this redlist status
        status_df = df[df["Redlist_Status"] == status]
        # Count observations per species with this status
        species_in_status = status_df["Species_NorwegianName"].value_counts().to_dict()
        redlist_species[status] = species_in_status
    
    stats["species_by_redlist_status"] = redlist_species
    
    # Number of observations per taxonomic order (using Norwegian name)
    order_counts = df["Order_NorwegianName"].value_counts().to_dict()
    stats["observations_per_order"] = order_counts
    
    # Temporal analysis
    temporal_stats = generate_temporal_summary(df, logger_file_path)
    stats["temporal_analysis"] = temporal_stats
    
    return stats


def print_summary_statistics(stats: Dict) -> None:
    """
    Print formatted summary statistics to the console
    
    Args:
        stats: Dictionary of statistics generated by calculate_summary_statistics
    """
    if not stats:
        logging.warning("No statistics to print")
        return
    
    print("\n" + "="*50)
    print("ANALYSIS SUMMARY")
    print("="*50)
    
    # Total observations
    print(f"\nTotal observations: {stats.get('total_observations', 0)}")
    print(f"Unique species detected: {stats.get('unique_species_count', 0)}")
    
    # Recording analysis
    if 'recording_analysis' in stats:
        rec_analysis = stats['recording_analysis']
        print(f"Recording duration: {rec_analysis['total_duration_minutes']} minutes ({rec_analysis['total_duration_seconds']} seconds)")
        print(f"Detection density: {rec_analysis['detection_density_per_minute']} detections per minute")
        print(f"Analysis period: {rec_analysis['first_detection_time']:.0f}s to {rec_analysis['last_detection_time']:.0f}s")
    
    # Confidence analysis (moved up to be more prominent)
    if 'confidence_overall' in stats:
        conf_overall = stats['confidence_overall']
        print(f"Overall confidence: Mean={conf_overall['mean']}, Median={conf_overall['median']}, Range={conf_overall['min']}-{conf_overall['max']}")
        
        # High confidence detections
        if 'high_confidence_detections' in stats:
            high_conf = stats['high_confidence_detections']
            print(f"High confidence detections (>0.8): {high_conf['count']} of {stats['total_observations']} ({high_conf['percentage']}%)")
    
    # Top species
    print("\nMost frequently detected species:")
    for species, count in stats.get('top_species', {}).items():
        print(f"  {species}: {count} observations")
    
    # Redlist status breakdown in conservation priority order
    redlist_order = ["CR", "EN", "VU", "NT", "LC", "DD", "NA", "NE"]
    species_by_status = stats.get('species_by_redlist_status', {})
    
    print("\nObservations by redlist status (ordered by conservation priority):")
    
    # Display total counts by status in conservation priority order
    redlist_counts = stats.get('observations_per_redlist_status', {})
    for status in redlist_order:
        if status in redlist_counts:
            count = redlist_counts[status]
            print(f"  {status}: {count} observations")
            
            # List species within this status category
            if status in species_by_status:
                species_counts = species_by_status[status]
                # Sort species by observation count (descending)
                for species, sp_count in sorted(species_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"    - {species}: {sp_count} observations")
    
    # Handle any statuses not in our predefined order
    for status, count in redlist_counts.items():
        if status not in redlist_order and status:
            status_display = status
            print(f"  {status_display}: {count} observations")
            
            # List species within this status category
            if status in species_by_status:
                species_counts = species_by_status[status]
                # Sort species by observation count (descending)
                for species, sp_count in sorted(species_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"    - {species}: {sp_count} observations")
    
    # Order breakdown (top 5)
    order_counts = stats.get('observations_per_order', {})
    if order_counts:
        print("\nObservations by taxonomic order (top 5):")
        for order, count in sorted(order_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {order}: {count} observations")
    
    # Detailed confidence analysis section
    if 'confidence_overall' in stats:
        print("\n" + "="*50)
        print("DETAILED CONFIDENCE ANALYSIS")
        print("="*50)
        
        # Confidence distribution
        if 'confidence_distribution' in stats:
            conf_dist = stats['confidence_distribution']
            print(f"\nConfidence distribution:")
            print(f"  Very High (0.9+): {conf_dist['very_high']['count']} detections ({conf_dist['very_high']['percentage']}%)")
            print(f"  High (0.7-0.9): {conf_dist['high']['count']} detections ({conf_dist['high']['percentage']}%)")
            print(f"  Medium (0.5-0.7): {conf_dist['medium']['count']} detections ({conf_dist['medium']['percentage']}%)")
            print(f"  Low (<0.5): {conf_dist['low']['count']} detections ({conf_dist['low']['percentage']}%)")
        
        # Species by average confidence (all species)
        if 'confidence_by_species' in stats:
            conf_by_species = stats['confidence_by_species']
            sorted_species = sorted(conf_by_species.items(), key=lambda x: x[1]['mean'], reverse=True)
            print(f"\nSpecies by average confidence (all species):")
            for species, conf_data in sorted_species:
                print(f"  {species}: {conf_data['mean']} (range: {conf_data['min']}-{conf_data['max']}, n={conf_data['count']})")
    
    # Temporal analysis section
    if 'temporal_analysis' in stats:
        print_temporal_analysis(stats['temporal_analysis'])
    
    print("\n" + "="*50)


def generate_statistics_report(csv_path: Path, logger_file_path: str = None) -> Dict:
    """
    Generate and print summary statistics from the enriched detections CSV
    
    Args:
        csv_path: Path to the enriched detections CSV file
        logger_file_path: Optional path to logger CSV file for real timestamp analysis
        
    Returns:
        Dictionary containing the calculated statistics
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path, sep=";")
        
        # Calculate statistics
        stats = calculate_summary_statistics(df, logger_file_path)
        
        # Print statistics to console
        print_summary_statistics(stats)
        
        return stats
        
    except Exception as e:
        logging.error(f"Error generating statistics report: {e}", exc_info=True)
        return {}