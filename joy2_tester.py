import pathlib
import joypy
import pandas as pd
from matplotlib import pyplot as plt
from functions.temporal_analysis import add_real_timestamps

# ---------------------------------------
# Laster inn data
# ---------------------------------------

df = pd.read_csv(
    pathlib.Path(__file__).parent / "data_output_lyd" / "interim" / "enriched_detections.csv", delimiter=";"
)

# ---------------------------------------
# Beregner tidspunkt fra filnavn (ekte tidspunkt)
# ---------------------------------------

# Use add_real_timestamps to get actual hour_of_day from filenames
df = add_real_timestamps(df)

# Fallback if timestamp parsing fails
if "hour_of_day" not in df.columns or df["hour_of_day"].isnull().all():
    print("Warning: Could not parse timestamps from filenames. Using start_time offset as fallback.")
    df["hour_of_day"] = (df["start_time"] / 3600) % 24


# ---------------------------------------
# Filtrer ut arter med færre enn min_detections
# ---------------------------------------

min_detections = 5
detection_counts = df["Species_NorwegianName"].value_counts()
species_to_keep = detection_counts[detection_counts >= min_detections].index
df_filtered = df[df["Species_NorwegianName"].isin(species_to_keep)].copy()


# ---------------------------------------
# Transform to noon-to-noon display (like joy_division_plot)
# ---------------------------------------

# Transform hours: 12 PM (noon) -> 0, midnight -> 12, etc.
df_filtered["hour_of_day_transformed"] = (df_filtered["hour_of_day"] - 12) % 24

# ---------------------------------------
# Sorter peaks etter tidspunkt (using transformed coordinates)
# ---------------------------------------

peak_times = df_filtered.groupby("Species_NorwegianName")["hour_of_day_transformed"].mean().sort_values()
sorted_species_list = peak_times.index.tolist()

# ---------------------------------------
# Convert 'Species_NorwegianName' to a categorical type with the desired order
# ---------------------------------------

df_filtered["Species_NorwegianName"] = pd.Categorical(
    df_filtered["Species_NorwegianName"], categories=sorted_species_list, ordered=True
)
df_filtered = df_filtered.sort_values("Species_NorwegianName")

# ---------------------------------------
# Plotter (using transformed coordinates)
# ---------------------------------------

fig, ax = joypy.joyplot(
    df_filtered,  # Use the filtered DataFrame
    by="Species_NorwegianName",
    column="hour_of_day_transformed",  # Use transformed coordinates
    figsize=(10, 5),
    x_range=[0, 24],
    linewidth=0.5,
    fade=True,
)

# Customize the x-axis for noon-to-noon display
plt.xlabel("Hour of Day")
plt.xticks(ticks=[0, 6, 12, 18, 24], labels=["12:00", "18:00", "00:00", "06:00", "12:00"])

plt.show()
