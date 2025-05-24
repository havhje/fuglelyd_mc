#!/usr/bin/env python3
"""
Test runner for fuglelyd_MC project.
Executes all tests in the tests directory.
"""

import unittest
import sys
import os
import logging
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Disable excessive logging during tests
logging.basicConfig(level=logging.ERROR)

def run_all_tests():
    """Discover and run all tests in the tests directory"""
    # Get the directory containing this script
    test_dir = Path(__file__).parent
    
    # Discover all tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_name):
    """Run a specific test module"""
    if not test_name.startswith('test_'):
        test_name = f'test_{test_name}'
    if not test_name.endswith('.py'):
        test_name = f'{test_name}.py'
    
    test_dir = Path(__file__).parent
    test_path = test_dir / test_name
    
    if not test_path.exists():
        print(f"Error: Test file {test_path} not found")
        return 1
    
    # Import the test module
    sys.path.insert(0, str(test_dir))
    module_name = test_name[:-3]  # Remove .py extension
    __import__(module_name)
    
    # Run the tests in the module
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(module_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def generate_test_data():
    """Generate sample test data"""
    from test_data_generator import generate_sample_detections_csv
    
    # Get the test data directory
    test_dir = Path(__file__).parent
    test_data_dir = test_dir / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    # Generate the sample data
    output_path = test_data_dir / "sample_enriched_detections.csv"
    stats = generate_sample_detections_csv(output_path)
    
    return 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for fuglelyd_MC project")
    parser.add_argument('test', nargs='?', help="Specific test to run (without test_ prefix)")
    parser.add_argument('--generate-data', action='store_true', help="Generate sample test data")
    
    args = parser.parse_args()
    
    if args.generate_data:
        sys.exit(generate_test_data())
    elif args.test:
        sys.exit(run_specific_test(args.test))
    else:
        sys.exit(run_all_tests())