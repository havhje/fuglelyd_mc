import pathlib
import joypy
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from functions.temporal_analysis import add_real_timestamps


def create_joypy_plot(df: pd.DataFrame, output_path: pathlib.Path, min_detections: int = 5) -> None:
    """
    Create a joypy ridgeline plot with confidence-based coloring and save as PNG.

    Args:
        df: DataFrame with detection data (must have columns: Species_NorwegianName, confidence, filename)
        output_path: Path where the PNG file should be saved
        min_detections: Minimum number of detections required per species
    """
    if df.empty:
        print("No data available for joypy plot")
        return

    # Use add_real_timestamps to get actual hour_of_day from filenames
    df = add_real_timestamps(df)

    # Fallback if timestamp parsing fails
    if "hour_of_day" not in df.columns or df["hour_of_day"].isnull().all():
        print("Warning: Could not parse timestamps from filenames. Using start_time offset as fallback.")
        if "start_time" in df.columns:
            df["hour_of_day"] = (df["start_time"] / 3600) % 24
        else:
            print("Error: Cannot determine hour_of_day. No time data available.")
            return

    # Filter out species with fewer than min_detections
    detection_counts = df["Species_NorwegianName"].value_counts()
    species_to_keep = detection_counts[detection_counts >= min_detections].index
    df_filtered = df[df["Species_NorwegianName"].isin(species_to_keep)].copy()

    if df_filtered.empty:
        print(f"No species have >= {min_detections} detections. Cannot create plot.")
        return

    # Transform to noon-to-noon display
    df_filtered["hour_of_day_transformed"] = (df_filtered["hour_of_day"] - 12) % 24

    # Calculate confidence statistics for coloring
    confidence_stats = df_filtered.groupby("Species_NorwegianName")["confidence"].mean()

    # Sort peaks by transformed coordinates
    peak_times = df_filtered.groupby("Species_NorwegianName")["hour_of_day_transformed"].mean().sort_values()
    sorted_species_list = peak_times.index.tolist()

    # Convert to categorical type with desired order
    df_filtered["Species_NorwegianName"] = pd.Categorical(
        df_filtered["Species_NorwegianName"], categories=sorted_species_list, ordered=True
    )
    df_filtered = df_filtered.sort_values("Species_NorwegianName")

    # Setup colormap for confidence-based coloring
    sorted_confidences = [confidence_stats[species] for species in sorted_species_list]
    conf_min, conf_max = min(sorted_confidences), max(sorted_confidences)

    # Avoid division by zero if all confidences are the same
    if conf_max - conf_min < 0.01:
        conf_min -= 0.05
        conf_max += 0.05

    # Create colormap
    norm = plt.Normalize(vmin=conf_min, vmax=conf_max)
    cmap = plt.cm.plasma_r  # Inverted plasma colormap
    colors = [cmap(norm(conf)) for conf in sorted_confidences]

    # Create the joyplot
    fig, ax = joypy.joyplot(
        df_filtered,
        by="Species_NorwegianName",
        column="hour_of_day_transformed",
        figsize=(12, 8),
        x_range=[0, 24],
        linewidth=0.5,
        fade=True,
    )

    # Apply confidence-based colors manually to each subplot
    for i, (species, color) in enumerate(zip(sorted_species_list, colors)):
        if isinstance(ax, list):
            current_ax = ax[i]
        else:
            current_ax = ax

        # Color the patches
        for patch in current_ax.collections:
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

    # Customize the x-axis for noon-to-noon display
    plt.xlabel("Hour of Day", fontsize=12, fontweight="bold")
    plt.xticks(ticks=[0, 6, 12, 18, 24], labels=["12:00", "18:00", "00:00", "06:00", "12:00"])

    # Add title
    plt.suptitle("Bird Detection Patterns by Time of Day (Joypy)", fontsize=14, fontweight="bold")

    # Add colorbar for confidence
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.8, aspect=20)
    cbar.set_label("Average Confidence", rotation=270, labelpad=15, fontweight="bold")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()  # Close to free memory

    print(f"Joypy plot saved to: {output_path}")


# Keep the original script functionality for standalone use
if __name__ == "__main__":
    # Original standalone script code
    df = pd.read_csv(
        pathlib.Path(__file__).parent / "data_output_lyd" / "interim" / "enriched_detections.csv", delimiter=";"
    )

    output_path = pathlib.Path(__file__).parent / "figur" / "joypy_plot.png"
    create_joypy_plot(df, output_path)
