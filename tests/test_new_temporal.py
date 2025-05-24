#!/usr/bin/env python3
"""
Test the new temporal analysis with real data
"""

import pandas as pd
from functions.temporal_analysis import generate_temporal_summary, print_temporal_analysis


def test_temporal_analysis():
    """Test the new temporal analysis with actual detection data"""

    # Load the real detection data
    csv_path = "data_output_lyd/interim/enriched_detections.csv"
    logger_path = "test_logger.csv"  # Our test logger file

    try:
        # Read the detection data
        df = pd.read_csv(csv_path, sep=";")
        print(f"Loaded {len(df)} detections from {csv_path}")
        print(f"Columns: {list(df.columns)}")
        print(f"Sample filenames: {df['filename'].unique()[:2]}")

        # Run temporal analysis
        print("\nRunning temporal analysis...")
        temporal_results = generate_temporal_summary(df, logger_path)

        # Print results
        print_temporal_analysis(temporal_results)

        # Show some additional details
        print("\nAdditional Analysis Details:")
        if "species_patterns" in temporal_results:
            species_patterns = temporal_results["species_patterns"]
            print(f"Species analyzed: {len(species_patterns)}")

            # Show a few interesting species patterns
            interesting_species = ["vipe", "fiskemåke", "tjeld", "storspove"]
            for species in interesting_species:
                if species in species_patterns:
                    pattern = species_patterns[species]
                    print(
                        f"  {species}: {pattern['detection_count']} detections, "
                        f"peak hour: {pattern['peak_activity_hour']}, "
                        f"dawn active: {pattern['is_dawn_active']}, "
                        f"evening active: {pattern['is_evening_active']}"
                    )

        print("\nTemporal analysis test completed!")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_temporal_analysis()
