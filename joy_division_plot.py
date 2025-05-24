#!/usr/bin/env python3
"""
Joy Division-style ridgeline plot for bird detection patterns by time of day.
Creates a stacked ridgeline visualization where each species gets its own ridge,
colored by average confidence and showing detection density throughout the day.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy import stats
from pathlib import Path
import argparse
import logging
from typing import Dict, List, Tuple, Optional


def load_detection_data(csv_path: Path) -> pd.DataFrame:
    """
    Load and prepare detection data from CSV file

    Args:
        csv_path: Path to enriched detections CSV

    Returns:
        Cleaned DataFrame with hour_of_day column
    """
    try:
        df = pd.read_csv(csv_path, sep=";")

        # Add hour extraction if not present
        if "hour_of_day" not in df.columns:
            # Try to extract from timestamp in filename
            from functions.temporal_analysis import add_real_timestamps

            df = add_real_timestamps(df)

        # Filter out rows without valid species names or hour data
        df = df.dropna(subset=["Species_NorwegianName"])

        # If still no hour_of_day, try to extract from start_time assuming it's seconds from start of day
        if "hour_of_day" not in df.columns and "start_time" in df.columns:
            # Assume start_time is seconds from beginning of recording
            # This is a fallback - ideally we'd have proper timestamps
            df["hour_of_day"] = (df["start_time"] / 3600) % 24

        return df

    except Exception as e:
        logging.error(f"Error loading detection data: {e}")
        return pd.DataFrame()


def calculate_species_stats(df: pd.DataFrame, min_detections: int = 5) -> Dict:
    """
    Calculate hourly detection patterns and average confidence for each species

    Args:
        df: Detection DataFrame
        min_detections: Minimum number of detections required for a species to be included

    Returns:
        Dictionary with species statistics
    """
    species_stats = {}

    for species in df["Species_NorwegianName"].unique():
        if pd.isna(species):
            continue

        species_data = df[df["Species_NorwegianName"] == species].copy()

        # Skip species with too few detections
        if len(species_data) < min_detections:
            continue

        # Calculate average confidence
        avg_confidence = species_data["confidence"].mean() if "confidence" in species_data.columns else 0.8

        # Calculate hourly detection counts
        hourly_counts = species_data.groupby("hour_of_day").size()

        # Find peak activity hour for sorting
        peak_hour = hourly_counts.idxmax() if not hourly_counts.empty else 12

        # Create smooth density curve using KDE
        hours = species_data["hour_of_day"].values
        if len(hours) > 1:
            # Create kernel density estimate
            kde = stats.gaussian_kde(hours)
            hour_range = np.linspace(0, 24, 100)
            density = kde(hour_range)
            # Normalize density
            density = density / density.max() if density.max() > 0 else density
        else:
            # Single detection - create a spike
            hour_range = np.linspace(0, 24, 100)
            density = np.zeros(100)
            closest_idx = np.argmin(np.abs(hour_range - hours[0]))
            density[closest_idx] = 1.0

        species_stats[species] = {
            "avg_confidence": avg_confidence,
            "peak_hour": peak_hour,
            "total_detections": len(species_data),
            "hour_range": hour_range,
            "density": density,
            "hourly_counts": hourly_counts.to_dict(),
        }

    return species_stats


def create_joy_division_plot(
    species_stats: Dict, output_path: Optional[Path] = None, figsize: Tuple[int, int] = (12, 16)
) -> None:
    """
    Create Joy Division-style ridgeline plot

    Args:
        species_stats: Dictionary of species statistics
        output_path: Optional path to save the plot
        figsize: Figure size tuple
    """
    if not species_stats:
        logging.warning("No species data available for plotting")
        return

    # Sort species by peak activity hour (earliest first)
    sorted_species = sorted(species_stats.items(), key=lambda x: x[1]["peak_hour"])

    n_species = len(sorted_species)

    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")

    # Set up colormap for confidence values
    cmap = plt.cm.inferno  # Changed from plasma to inferno
    confidence_values = [stats["avg_confidence"] for _, stats in sorted_species]

    # Determine min/max for normalization, handling empty list
    min_conf = min(confidence_values) if confidence_values else 0.70
    max_conf = max(confidence_values) if confidence_values else 0.95
    norm = mcolors.Normalize(vmin=min_conf, vmax=max_conf)

    # Ridge spacing and scaling - adjust for overlap and appearance
    ridge_height = 1.0  # Adjusted for appearance
    ridge_spacing = 0.7  # Adjusted for appearance

    # Plot each species as a ridge
    y_positions = []
    species_names = []

    for i, (species, stats) in enumerate(sorted_species):
        y_base = i * ridge_spacing
        y_positions.append(y_base)
        # Shorten long species names if necessary for display
        display_species_name = species[:30] + "..." if len(species) > 30 else species
        species_names.append(display_species_name)

        # Get color based on confidence
        color = cmap(norm(stats["avg_confidence"]))

        # Scale density for visual appeal - ridges point upwards
        scaled_density = stats["density"] * ridge_height

        # Create the ridge line - pointing upwards from baseline
        hour_range = stats["hour_range"]
        y_values = y_base + scaled_density  # Add to base (upwards)

        # Fill the area under the curve
        ax.fill_between(hour_range, y_base, y_values, color=color, alpha=0.9, linewidth=0)  # Increased alpha

        # Remove outline for cleaner look like the example
        # ax.plot(hour_range, y_values, color="black", linewidth=0.5, alpha=0.7)

        # Baseline removed for cleaner look
        # ax.axhline(y=y_base, color="black", linewidth=0.3, alpha=0.3)

    # Customize the plot
    ax.set_xlim(-1, 25)  # Adjusted for a bit of padding
    ax.set_ylim(-0.5, (n_species - 1) * ridge_spacing + ridge_height + 0.5)

    # Set x-axis (hours)
    ax.set_xlabel("Hour of Day", fontsize=14, fontweight="normal")  # Removed bold
    hour_ticks = list(range(0, 31, 10))  # Changed ticks to 0, 10, 20, 30
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels([f"{h}" for h in hour_ticks], fontsize=10)  # Removed leading zero formatting

    # Set y-axis (species)
    ax.set_ylabel("Species", fontsize=14, fontweight="normal")  # Removed bold
    ax.set_yticks(y_positions)
    ax.set_yticklabels(species_names, fontsize=9)  # Adjusted fontsize

    # Invert y-axis so earliest peak species are at top
    ax.invert_yaxis()

    # Add vertical grid lines only
    ax.xaxis.grid(True, alpha=0.5, linestyle="-", linewidth=0.7)  # Adjusted alpha and linewidth
    ax.yaxis.grid(False)  # Turn off horizontal grid lines
    ax.set_axisbelow(True)

    # Add title and subtitle
    ax.set_title("Bird Detection Patterns by Time of Day", fontsize=16, fontweight="bold", pad=30)  # Adjusted padding
    fig.suptitle(
        "Ridges sorted by earliest peak; Fill = Avg Confidence", fontsize=10, y=0.93, style="italic", x=0.52
    )  # Used fig.suptitle for better placement

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Important for stand-alone colorbar

    # Position colorbar to the right, similar to example
    cbar_ax = fig.add_axes([0.82, 0.4, 0.03, 0.3])  # [left, bottom, width, height] in figure coords
    cbar = plt.colorbar(sm, cax=cbar_ax)  # Use the new axes for the colorbar

    cbar.set_label("Avg % Confidence", fontsize=10, fontweight="bold", labelpad=10)  # Adjusted fontsize and padding

    # Set specific ticks for the colorbar if desired, e.g., [0.75, 0.80, 0.85, 0.90]
    # These should ideally be derived from the actual data's range or desired presentation
    # For now, let's use a few ticks based on the norm.
    cbar_ticks_to_show = np.linspace(min_conf, max_conf, 4)
    if min_conf == 0.70 and max_conf == 0.95:  # Default if no confidence values
        cbar_ticks_to_show = [0.75, 0.80, 0.85, 0.90]

    cbar.set_ticks(cbar_ticks_to_show)
    cbar.set_ticklabels([f"{tick:.2f}" for tick in cbar_ticks_to_show], fontsize=9)
    cbar.ax.tick_params(labelsize=9)

    # Adjust layout - tight_layout might conflict with manually placed suptitle and colorbar
    # plt.tight_layout() # Removed for more manual control
    fig.subplots_adjust(left=0.2, right=0.78, top=0.88, bottom=0.1)  # Manually adjust subplot

    # Save or show
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
        print(f"Plot saved to: {output_path}")
    else:
        plt.show()

    plt.close()


def generate_sample_data() -> pd.DataFrame:
    """
    Generate sample data for testing the plot
    """
    np.random.seed(42)

    # Sample Norwegian bird species with different activity patterns
    species_patterns = {
        "Sanglerke": {"peak": 5, "spread": 2, "confidence": 0.85},  # Dawn singer
        "Rødstrupe": {"peak": 6, "spread": 3, "confidence": 0.82},  # Robin
        "Gråtrost": {"peak": 7, "spread": 4, "confidence": 0.79},  # Blackbird
        "Meiser": {"peak": 8, "spread": 5, "confidence": 0.77},  # Tits
        "Kråkefugl": {"peak": 10, "spread": 6, "confidence": 0.75},  # Crows
        "Måke": {"peak": 12, "spread": 4, "confidence": 0.73},  # Gulls
        "Spurvefugl": {"peak": 14, "spread": 3, "confidence": 0.81},  # Sparrows
        "Finker": {"peak": 16, "spread": 3, "confidence": 0.83},  # Finches
        "Ugle": {"peak": 22, "spread": 2, "confidence": 0.88},  # Owls
    }

    data = []

    for species, pattern in species_patterns.items():
        n_detections = np.random.randint(20, 100)

        # Generate hours around the peak with some spread
        hours = np.random.normal(pattern["peak"], pattern["spread"], n_detections)
        hours = np.clip(hours, 0, 23.99)  # Keep within 24-hour range

        # Generate confidence values around the average
        confidences = np.random.normal(pattern["confidence"], 0.05, n_detections)
        confidences = np.clip(confidences, 0.5, 1.0)  # Keep within valid range

        for i in range(n_detections):
            data.append(
                {
                    "Species_NorwegianName": species,
                    "hour_of_day": hours[i],
                    "confidence": confidences[i],
                    "start_time": hours[i] * 3600,  # Convert to seconds
                }
            )

    return pd.DataFrame(data)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Generate Joy Division-style bird detection plot")

    parser.add_argument("--input", "-i", type=str, help="Path to enriched detections CSV file")
    parser.add_argument("--output", "-o", type=str, help="Output path for the plot (PNG/PDF)")
    parser.add_argument("--sample", action="store_true", help="Use sample data instead of real data")
    parser.add_argument(
        "--min-detections", type=int, default=5, help="Minimum detections required per species (default: 5)"
    )
    parser.add_argument("--width", type=int, default=12, help="Figure width in inches (default: 12)")
    parser.add_argument("--height", type=int, default=16, help="Figure height in inches (default: 16)")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Load data
    if args.sample:
        print("Generating sample data...")
        df = generate_sample_data()
    elif args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            logging.error(f"Input file not found: {input_path}")
            return 1
        print(f"Loading data from: {input_path}")
        df = load_detection_data(input_path)
    else:
        # Try to find default CSV in output directory
        default_csv = Path("data_output_lyd/interim/enriched_detections.csv")
        if default_csv.exists():
            print(f"Loading data from default location: {default_csv}")
            df = load_detection_data(default_csv)
        else:
            logging.error("No input file specified and default CSV not found. Use --sample or --input")
            return 1

    if df.empty:
        logging.error("No data available for plotting")
        return 1

    print(f"Loaded {len(df)} detections for {df['Species_NorwegianName'].nunique()} species")

    # Calculate species statistics
    species_stats = calculate_species_stats(df, min_detections=args.min_detections)

    if not species_stats:
        logging.error(f"No species found with at least {args.min_detections} detections")
        return 1

    print(f"Creating plot for {len(species_stats)} species...")

    # Set output path
    output_path = None
    if args.output:
        output_path = Path(args.output)
    elif not args.sample:
        # Default output name based on input
        output_path = Path("bird_detection_joy_division_plot.png")

    # Create the plot
    create_joy_division_plot(species_stats, output_path, figsize=(args.width, args.height))

    print("Plot generation complete!")
    return 0


if __name__ == "__main__":
    exit(main())
