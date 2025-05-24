#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Joy Division-style ridgeline plot for bird species detection patterns by time of day.

This script creates a visualization showing temporal activity patterns for multiple bird species,
with each species displayed as a horizontal ridge colored by detection confidence.

Usage:
    python joy_division_plot.py --sample                    # Use sample data
    python joy_division_plot.py --input data.csv           # Use real data
    python joy_division_plot.py --output plot.png          # Custom output
    python joy_division_plot.py --min-detections 10        # Filter threshold
    python joy_division_plot.py --width 15 --height 20     # Custom size

Author: Generated for Bird Detection Analysis Project
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.stats import gaussian_kde
from pathlib import Path
import argparse
import logging
from typing import Tuple, List, Dict, Optional
import warnings
from functions.temporal_analysis import add_real_timestamps

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_detection_data(csv_path: Path) -> pd.DataFrame:
    """
    Load bird detection data from CSV file.

    Args:
        csv_path: Path to CSV file with semicolon separators

    Returns:
        DataFrame with detection data

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    try:
        # Try different encodings
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                df = pd.read_csv(csv_path, sep=";", encoding=encoding)
                logger.info(f"Successfully loaded CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode CSV file with any common encoding")

        logger.info(f"Loaded {len(df)} detections from {csv_path}")

        # Check for required columns
        required_cols = ["Species_NorwegianName", "confidence"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Use add_real_timestamps to get hour_of_day from filenames
        logger.info("Attempting to derive real timestamps from filenames...")
        df = add_real_timestamps(df)

        if "hour_of_day" not in df.columns or df["hour_of_day"].isnull().all():
            logger.warning("Failed to derive 'hour_of_day' from filenames via add_real_timestamps.")
            # Fallback if add_real_timestamps doesn't populate hour_of_day, though it should.
            if "start_time" in df.columns:
                logger.info("Falling back to calculating hour_of_day from 'start_time' as offset from midnight.")
                df["hour_of_day"] = (df["start_time"] / 3600) % 24
            else:
                logger.error("Cannot determine hour_of_day. 'start_time' column also missing.")
                return pd.DataFrame()  # Return empty if no time data

        # Validate data ranges
        df = df.dropna(subset=["hour_of_day", "confidence", "Species_NorwegianName"])
        df = df[(df["hour_of_day"] >= 0) & (df["hour_of_day"] < 24)]
        df = df[(df["confidence"] >= 0) & (df["confidence"] <= 1)]

        logger.info(f"After validation: {len(df)} valid detections")
        return df

    except Exception as e:
        logger.error(f"Error loading CSV file: {e}")
        raise


def generate_sample_data() -> pd.DataFrame:
    """
    Generate realistic sample bird detection data for demonstration.

    Returns:
        DataFrame with sample detection data
    """
    np.random.seed(42)  # For reproducible results

    # Norwegian bird species with different activity patterns
    species_data = {
        "r�dstrupe": {"peak_hour": 6.0, "std": 1.5, "confidence": 0.85, "n_detections": 120},
        "l�vsanger": {"peak_hour": 6.5, "std": 2.0, "confidence": 0.82, "n_detections": 95},
        "bj�rk": {"peak_hour": 7.0, "std": 1.8, "confidence": 0.78, "n_detections": 80},
        "m�ltrost": {"peak_hour": 8.5, "std": 3.0, "confidence": 0.80, "n_detections": 70},
        "gr�meis": {"peak_hour": 12.0, "std": 4.0, "confidence": 0.75, "n_detections": 60},
        "kr�ke": {"peak_hour": 14.0, "std": 5.0, "confidence": 0.88, "n_detections": 45},
        "turdus": {"peak_hour": 19.0, "std": 2.5, "confidence": 0.83, "n_detections": 55},
        "nattravn": {"peak_hour": 22.0, "std": 2.0, "confidence": 0.90, "n_detections": 35},
        "hornugle": {"peak_hour": 2.0, "std": 1.5, "confidence": 0.92, "n_detections": 25},
    }

    detections = []

    for species, params in species_data.items():
        n_detections = params["n_detections"]
        peak_hour = params["peak_hour"]
        std = params["std"]
        base_confidence = params["confidence"]

        # Generate hours with Gaussian distribution around peak
        hours = np.random.normal(peak_hour, std, n_detections)
        # Handle wrapping around 24-hour cycle
        hours = hours % 24

        # Generate confidence scores with some variation
        confidences = np.random.normal(base_confidence, 0.05, n_detections)
        confidences = np.clip(confidences, 0.0, 1.0)

        # Create detection records
        for hour, conf in zip(hours, confidences):
            detections.append(
                {
                    "Species_NorwegianName": species,
                    "hour_of_day": hour,
                    "confidence": conf,
                    "filename": f"sample_recording_{int(hour):02d}{int((hour % 1) * 60):02d}.wav",
                }
            )

    df = pd.DataFrame(detections)
    logger.info(f"Generated {len(df)} sample detections for {len(species_data)} species")
    return df


def prepare_species_data(df: pd.DataFrame, min_detections: int = 5) -> Tuple[List[str], Dict]:
    """
    Prepare species data for plotting, calculating statistics and sorting by peak activity.

    Args:
        df: DataFrame with detection data
        min_detections: Minimum number of detections required per species

    Returns:
        Tuple of (sorted species list, species statistics dict)
    """
    species_stats = {}

    for species in df["Species_NorwegianName"].unique():
        species_data = df[df["Species_NorwegianName"] == species]

        if len(species_data) < min_detections:
            logger.info(f"Skipping {species}: only {len(species_data)} detections (< {min_detections})")
            continue

        hours = species_data["hour_of_day"].values
        confidences = species_data["confidence"].values

        # Calculate peak hour (weighted by confidence)
        weights = confidences / confidences.sum()
        peak_hour = np.average(hours, weights=weights)

        # Calculate average confidence
        avg_confidence = confidences.mean()

        species_stats[species] = {
            "peak_hour": peak_hour,
            "avg_confidence": avg_confidence,
            "n_detections": len(species_data),
            "hours": hours,
            "confidences": confidences,
        }

    # Sort species by peak hour (dawn singers first)
    sorted_species = sorted(species_stats.keys(), key=lambda x: species_stats[x]["peak_hour"])

    logger.info(f"Prepared data for {len(sorted_species)} species")
    return sorted_species, species_stats


def create_joy_division_plot(
    df: pd.DataFrame, output_path: Path, figsize: Tuple[float, float] = (12, 16), min_detections: int = 5
) -> None:
    """
    Create Joy Division-style ridgeline plot of bird detection patterns.

    Args:
        df: DataFrame with detection data
        output_path: Path for output image file
        figsize: Figure size as (width, height) in inches
        min_detections: Minimum detections required per species
    """
    if df.empty:
        logger.error("No data available for plotting")
        return

    # Prepare species data
    sorted_species, species_stats = prepare_species_data(df, min_detections)

    if not sorted_species:
        logger.error("No species meet minimum detection criteria")
        return

    n_species = len(sorted_species)

    # Create figure and subplots
    fig, axes = plt.subplots(n_species, 1, figsize=figsize, sharex=True)
    if n_species == 1:
        axes = [axes]

    # Set up colormap based on confidence range
    all_confidences = [species_stats[sp]["avg_confidence"] for sp in sorted_species]
    conf_min, conf_max = min(all_confidences), max(all_confidences)
    if conf_max - conf_min < 0.01:  # Avoid division by zero
        conf_min -= 0.05
        conf_max += 0.05

    norm = plt.Normalize(vmin=conf_min, vmax=conf_max)
    cmap = plt.cm.plasma_r  # Inverted plasma colormap

    # Create ridgelines
    x_range = np.linspace(0, 24, 1000)

    for i, species in enumerate(sorted_species):
        ax = axes[i]
        stats = species_stats[species]
        hours = stats["hours"]
        avg_conf = stats["avg_confidence"]

        try:
            # Create KDE for smooth curve
            if len(hours) > 1:
                kde = gaussian_kde(hours)
                kde.set_bandwidth(kde.factor * 0.8)  # Slightly smoother
                density = kde(x_range)
            else:
                # Fallback for single detection
                density = np.zeros_like(x_range)
                closest_idx = np.argmin(np.abs(x_range - hours[0]))
                density[closest_idx] = 1.0

        except Exception as e:
            logger.warning(f"KDE failed for {species}: {e}. Using histogram fallback.")
            hist, bins = np.histogram(hours, bins=50, range=(0, 24), density=True)
            x_centers = (bins[:-1] + bins[1:]) / 2
            density = np.interp(x_range, x_centers, hist)

        # Normalize density to 0-1 range
        if density.max() > 0:
            density = density / density.max()

        # Color based on average confidence
        color = cmap(norm(avg_conf))

        # Fill the ridgeline
        ax.fill_between(x_range, 0, density, color=color, alpha=0.9)
        ax.plot(x_range, density, color="black", linewidth=0.8, alpha=0.8)

        # Configure subplot
        ax.set_ylim(0, 1)
        ax.set_xlim(0, 24)
        ax.set_yticks([])
        ax.set_ylabel("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.patch.set_alpha(0)

        # Add species label
        ax.text(-0.01, 0.5, species, transform=ax.transAxes, fontsize=10, fontweight="bold", va="center", ha="right")

        # Only show x-axis on bottom plot
        if i < n_species - 1:
            ax.set_xticks([])

    # Configure overall plot
    plt.subplots_adjust(hspace=-0.4, left=0.2)  # Added left margin for labels

    # Set up bottom axis
    axes[-1].set_xlabel("Hour of Day", fontsize=12, fontweight="bold")
    axes[-1].set_xticks([0, 6, 12, 18, 24])
    axes[-1].set_xticklabels(["0", "6", "12", "18", "24"])

    # Add title and subtitle
    fig.suptitle("Bird Detection Patterns by Time of Day", fontsize=16, fontweight="bold", y=0.98)
    fig.text(
        0.5, 0.95, "Ridges sorted by earliest peak; Fill = Avg Confidence", ha="center", fontsize=12, style="italic"
    )

    # Add y-axis label
    fig.text(0.02, 0.5, "Species", rotation=90, va="center", fontsize=12, fontweight="bold")

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_label("Average Confidence", rotation=270, labelpad=20, fontweight="bold")

    # Save plot
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    logger.info(f"Plot saved to: {output_path}")
    plt.close()


def main():
    """Main function to handle command line arguments and execute plotting."""
    parser = argparse.ArgumentParser(
        description="Create Joy Division-style ridgeline plot of bird detection patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --sample                     # Generate plot with sample data
  %(prog)s --input detections.csv       # Use real detection data
  %(prog)s --output my_plot.png         # Custom output filename
  %(prog)s --min-detections 15          # Require minimum 15 detections per species
  %(prog)s --width 15 --height 20       # Custom figure dimensions
        """,
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--sample", action="store_true", help="Use generated sample data for demonstration")
    input_group.add_argument("--input", type=Path, metavar="CSV_FILE", help="Path to CSV file with detection data")

    # Output and formatting options
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("bird_detection_joy_division_plot.png"),
        help="Output file path (default: bird_detection_joy_division_plot.png)",
    )
    parser.add_argument(
        "--min-detections",
        type=int,
        default=5,
        metavar="N",
        help="Minimum number of detections required per species (default: 5)",
    )
    parser.add_argument(
        "--width", type=float, default=12, metavar="INCHES", help="Figure width in inches (default: 12)"
    )
    parser.add_argument(
        "--height", type=float, default=16, metavar="INCHES", help="Figure height in inches (default: 16)"
    )

    # Logging options
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress all output except errors")

    args = parser.parse_args()

    # Configure logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Load or generate data
        if args.sample:
            logger.info("Generating sample bird detection data...")
            df = generate_sample_data()
        else:
            logger.info(f"Loading detection data from: {args.input}")
            df = load_detection_data(args.input)

        if df.empty:
            logger.error("No valid data available for plotting")
            return 1

        # Create output directory if needed
        args.output.parent.mkdir(parents=True, exist_ok=True)

        # Create plot
        logger.info("Creating Joy Division-style ridgeline plot...")
        create_joy_division_plot(
            df=df, output_path=args.output, figsize=(args.width, args.height), min_detections=args.min_detections
        )

        logger.info("Plot creation completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
