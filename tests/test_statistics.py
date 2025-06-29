import unittest
import pandas as pd
from pathlib import Path
import sys
import os
import tempfile
import shutil

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.statistics import calculate_summary_statistics, print_summary_statistics, generate_statistics_report


class TestStatistics(unittest.TestCase):
    """Test suite for the statistics module"""

    def setUp(self):
        """Create sample data for testing"""
        # Create a temp directory for test files
        self.temp_dir = tempfile.mkdtemp()

        # Create a sample DataFrame with bird detections
        self.sample_data = pd.DataFrame(
            {
                "scientific_name": [
                    "Corvus corax",
                    "Corvus corax",
                    "Erithacus rubecula",
                    "Parus major",
                    "Parus major",
                    "Parus major",
                    "Falco peregrinus",
                    "Aquila chrysaetos",
                ],
                "Species_NorwegianName": [
                    "Ravn",
                    "Ravn",
                    "Rødstrupe",
                    "Kjøttmeis",
                    "Kjøttmeis",
                    "Kjøttmeis",
                    "Vandrefalk",
                    "Kongeørn",
                ],
                "Family_ScientificName": [
                    "Corvidae",
                    "Corvidae",
                    "Muscicapidae",
                    "Paridae",
                    "Paridae",
                    "Paridae",
                    "Falconidae",
                    "Accipitridae",
                ],
                "Family_NorwegianName": [
                    "Kråkefugler",
                    "Kråkefugler",
                    "Fluesnappere",
                    "Meiser",
                    "Meiser",
                    "Meiser",
                    "Falker",
                    "Haukefamilien",
                ],
                "Order_ScientificName": [
                    "Passeriformes",
                    "Passeriformes",
                    "Passeriformes",
                    "Passeriformes",
                    "Passeriformes",
                    "Passeriformes",
                    "Falconiformes",
                    "Accipitriformes",
                ],
                "Order_NorwegianName": [
                    "Spurvefugler",
                    "Spurvefugler",
                    "Spurvefugler",
                    "Spurvefugler",
                    "Spurvefugler",
                    "Spurvefugler",
                    "Falkefugler",
                    "Haukefugler",
                ],
                "Redlist_Status": ["LC", "LC", "LC", "LC", "LC", "LC", "VU", "NT"],
                "confidence": [0.85, 0.87, 0.72, 0.65, 0.55, 0.43, 0.88, 0.78],
                "filename": [
                    "rec1_20230101_100000.wav",
                    "rec1_20230101_100000.wav",
                    "rec2_20230101_100500.wav",
                    "rec3_20230102_110000.wav",
                    "rec3_20230102_110000.wav",
                    "rec3_20230102_110000.wav",
                    "rec4_20230103_120000.wav",
                    "rec5_20230103_120500.wav",
                ],
                "start_time": [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0],
                "end_time": [3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0],
            }
        )

        # Create a CSV file from the sample data
        self.csv_path = Path(self.temp_dir) / "test_enriched_detections.csv"
        self.sample_data.to_csv(self.csv_path, sep=";", index=False)

    def tearDown(self):
        """Clean up temp files after tests"""
        shutil.rmtree(self.temp_dir)

    def test_calculate_summary_statistics(self):
        """Test the calculation of summary statistics from DataFrame"""
        stats = calculate_summary_statistics(self.sample_data)

        # Test total observations
        self.assertEqual(stats["total_observations"], 8)

        # Test unique species count
        self.assertEqual(stats["unique_species_count"], 5)  # Fixed from 4 to 5

        # Test observations per species
        self.assertEqual(stats["observations_per_species"]["Kjøttmeis"], 3)
        self.assertEqual(stats["observations_per_species"]["Ravn"], 2)
        self.assertEqual(stats["observations_per_species"]["Rødstrupe"], 1)
        self.assertEqual(stats["observations_per_species"]["Vandrefalk"], 1)
        self.assertEqual(stats["observations_per_species"]["Kongeørn"], 1)

        # Test top species
        self.assertIn("Kjøttmeis", stats["top_species"])
        self.assertEqual(stats["top_species"]["Kjøttmeis"], 3)

        # Test observations per redlist status
        self.assertEqual(stats["observations_per_redlist_status"]["LC"], 6)
        self.assertEqual(stats["observations_per_redlist_status"]["VU"], 1)
        self.assertEqual(stats["observations_per_redlist_status"]["NT"], 1)

        # Test species by redlist status
        self.assertEqual(len(stats["species_by_redlist_status"]["LC"]), 3)  # 3 LC species
        self.assertEqual(len(stats["species_by_redlist_status"]["VU"]), 1)  # 1 VU species
        self.assertEqual(len(stats["species_by_redlist_status"]["NT"]), 1)  # 1 NT species
        self.assertEqual(stats["species_by_redlist_status"]["VU"]["Vandrefalk"], 1)

        # Test observations per order
        self.assertEqual(stats["observations_per_order"]["Spurvefugler"], 6)

        # Test confidence statistics
        self.assertIn("confidence_overall", stats)
        self.assertAlmostEqual(stats["confidence_overall"]["mean"], 0.716, places=3)
        self.assertEqual(stats["confidence_overall"]["min"], 0.43)
        self.assertEqual(stats["confidence_overall"]["max"], 0.88)

        # Test confidence by species
        self.assertIn("confidence_by_species", stats)
        self.assertAlmostEqual(stats["confidence_by_species"]["Kjøttmeis"]["mean"], 0.543, places=3)
        self.assertEqual(stats["confidence_by_species"]["Kjøttmeis"]["count"], 3)

        # Test confidence distribution
        self.assertIn("confidence_distribution", stats)
        self.assertEqual(stats["confidence_distribution"]["very_high"]["count"], 0)
        self.assertEqual(stats["confidence_distribution"]["high"]["count"], 5)
        self.assertEqual(stats["confidence_distribution"]["medium"]["count"], 2)
        self.assertEqual(stats["confidence_distribution"]["low"]["count"], 1)

        # Test high confidence detections (>0.8)
        self.assertIn("high_confidence_detections", stats)
        self.assertEqual(stats["high_confidence_detections"]["count"], 3)

    def test_calculate_summary_statistics_empty_df(self):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame()
        stats = calculate_summary_statistics(empty_df)
        self.assertEqual(stats, {})

        # Also test with None
        stats = calculate_summary_statistics(None)
        self.assertEqual(stats, {})

    def test_print_summary_statistics(self, monkeypatch=None):
        """Test printing of statistics (does not actually test output content)"""
        stats = calculate_summary_statistics(self.sample_data)

        # Just make sure it doesn't error
        print_summary_statistics(stats)

        # Test with empty stats
        print_summary_statistics({})

    def test_generate_statistics_report(self):
        """Test generation of statistics report from CSV"""
        stats = generate_statistics_report(self.csv_path)

        # Verify some key statistics
        self.assertEqual(stats["total_observations"], 8)
        self.assertEqual(stats["unique_species_count"], 5)  # Fixed from 4 to 5

        # Test with non-existent file
        # Use try/except instead of assertRaises as the function logs the error and returns {}
        try:
            stats = generate_statistics_report(Path(self.temp_dir) / "nonexistent.csv")
            self.assertEqual(stats, {})  # Should return empty dict on error
        except Exception:
            self.fail("generate_statistics_report() raised Exception unexpectedly!")


class TestRedlistOrdering(unittest.TestCase):
    """Test suite specifically for redlist status ordering"""

    def setUp(self):
        """Create sample data with all redlist statuses"""
        # Create sample data with all redlist statuses in random order
        self.sample_data = pd.DataFrame(
            {
                "scientific_name": [
                    "Species1",
                    "Species2",
                    "Species3",
                    "Species4",
                    "Species5",
                    "Species6",
                    "Species7",
                    "Species8",
                    "Species9",
                    "Species10",
                    "Species11",
                    "Species11",
                    "Species8",
                    "Species8",
                ],
                "Species_NorwegianName": [
                    "Art1",
                    "Art2",
                    "Art3",
                    "Art4",
                    "Art5",
                    "Art6",
                    "Art7",
                    "Art8",
                    "Art9",
                    "Art10",
                    "Art11",
                    "Art11",
                    "Art8",
                    "Art8",
                ],
                "Redlist_Status": ["LC", "NT", "VU", "EN", "CR", "DD", "NA", "NE", "LC", "NT", "CR", "CR", "NE", "NE"],
                # Add missing Order_NorwegianName column
                "Order_NorwegianName": [
                    "Order1",
                    "Order2",
                    "Order3",
                    "Order4",
                    "Order5",
                    "Order6",
                    "Order7",
                    "Order8",
                    "Order9",
                    "Order10",
                    "Order11",
                    "Order11",
                    "Order8",
                    "Order8",
                ],
                "confidence": [0.91, 0.82, 0.73, 0.64, 0.95, 0.56, 0.77, 0.88, 0.49, 0.70, 0.92, 0.89, 0.75, 0.68],
                "filename": [
                    "f1_20230101_000000.wav",
                    "f2_20230101_010000.wav",
                    "f3_20230101_020000.wav",
                    "f4_20230101_030000.wav",
                    "f5_20230101_040000.wav",
                    "f6_20230101_050000.wav",
                    "f7_20230101_060000.wav",
                    "f8_20230101_070000.wav",
                    "f9_20230101_080000.wav",
                    "f10_20230101_090000.wav",
                    "f11_20230101_100000.wav",
                    "f11_20230101_100000.wav",
                    "f8_20230101_070000.wav",
                    "f8_20230101_070000.wav",
                ],
                "start_time": [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0, 27.0, 30.0, 33.0, 36.0, 39.0],
                "end_time": [3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0, 27.0, 30.0, 33.0, 36.0, 39.0, 42.0],
            }
        )

    def test_redlist_status_ordering(self):
        """Test that redlist statuses are properly ordered"""
        stats = calculate_summary_statistics(self.sample_data)

        # Test that species_by_redlist_status has expected keys
        redlist_statuses = list(stats["species_by_redlist_status"].keys())

        # Check that CR, EN, VU, NT, LC are all present
        self.assertIn("CR", redlist_statuses)
        self.assertIn("EN", redlist_statuses)
        self.assertIn("VU", redlist_statuses)
        self.assertIn("NT", redlist_statuses)
        self.assertIn("LC", redlist_statuses)

        # Verify species counts within each redlist status
        species_by_status = stats["species_by_redlist_status"]

        # Verify unique species within CR status based on the sample data
        self.assertEqual(set(species_by_status["CR"].keys()), {"Art5", "Art11"})
        # Check the observation counts for these CR species
        self.assertEqual(species_by_status["CR"]["Art5"], 1)
        self.assertEqual(species_by_status["CR"]["Art11"], 2)

        # Verify unique species within NE status
        self.assertEqual(set(species_by_status["NE"].keys()), {"Art8"})
        # Check the observation count for this NE species
        self.assertEqual(species_by_status["NE"]["Art8"], 3)


class TestMainIntegration(unittest.TestCase):
    """Integration test for the main analysis workflow"""

    def setUp(self):
        """Set up test environment with mock data files"""
        # Create a temp directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create interim directory for CSV output
        self.interim_dir = self.output_dir / "interim"
        self.interim_dir.mkdir(parents=True, exist_ok=True)

        # Create sample CSV
        self.csv_path = self.interim_dir / "enriched_detections.csv"

        # Create sample data
        sample_data = pd.DataFrame(
            {
                "scientific_name": ["Corvus corax", "Aquila chrysaetos", "Falco peregrinus"],
                "Species_NorwegianName": ["Ravn", "Kongeørn", "Vandrefalk"],
                "Order_NorwegianName": ["Spurvefugler", "Haukefugler", "Falkefugler"],
                "Redlist_Status": ["LC", "NT", "VU"],
                "confidence": [0.85, 0.67, 0.92],
                "filename": ["integ_20230201_100000.wav", "integ_20230201_110000.wav", "integ_20230201_120000.wav"],
                "start_time": [0.0, 3.0, 6.0],
                "end_time": [3.0, 6.0, 9.0],
            }
        )

        sample_data.to_csv(self.csv_path, sep=";", index=False)

    def tearDown(self):
        """Clean up temp files"""
        shutil.rmtree(self.temp_dir)

    def test_statistics_integration(self):
        """Test that statistics are generated correctly as part of workflow"""
        # Get statistics from our sample file
        stats = generate_statistics_report(self.csv_path)

        # Verify core statistics
        self.assertEqual(stats["total_observations"], 3)
        self.assertEqual(stats["unique_species_count"], 3)

        # Verify redlist statuses are included
        self.assertIn("LC", stats["observations_per_redlist_status"])
        self.assertIn("NT", stats["observations_per_redlist_status"])
        self.assertIn("VU", stats["observations_per_redlist_status"])

        # Verify species are correctly associated with redlist status
        self.assertEqual(stats["species_by_redlist_status"]["LC"]["Ravn"], 1)
        self.assertEqual(stats["species_by_redlist_status"]["NT"]["Kongeørn"], 1)
        self.assertEqual(stats["species_by_redlist_status"]["VU"]["Vandrefalk"], 1)


if __name__ == "__main__":
    unittest.main()
