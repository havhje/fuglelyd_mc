# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a bird sound analysis tool that uses BirdNET for species detection in audio recordings. The system enriches detections with Norwegian taxonomic data from Artskart API and provides temporal analysis capabilities.

**NEW**: The project now includes a Streamlit web interface (`app.py`) in addition to the command-line interface (`analyser_lyd_main.py`).

## Development Commands

### Environment Setup
```bash
python -m venv tf_venv
tf_venv/Scripts/activate    # Windows
source tf_venv/bin/activate # macOS/Linux
python -m pip install --upgrade pip
python -m pip install pandas tqdm pygwalker streamlit>=1.28.0 streamlit-folium>=0.15.0 streamlit-aggrid>=0.3.4 requests pydub tensorflow ffmpeg birdnetlib pyaudio librosa "resampy>=0.4.3" "seaborn>=0.13.2" "joypy>=0.2.6" "scipy>=1.15.3" matplotlib
```

### Running Tests
```bash
# Run all tests
python tests/run_tests.py

# Run specific test
python tests/run_tests.py statistics

# Generate test data
python tests/run_tests.py --generate-data
```

### Running Analysis

#### Web Interface (Streamlit)
```bash
# Start the Streamlit web app
streamlit run app.py

# The app will open at http://localhost:8501
```

#### Command Line Interface
```bash
# Basic location-based analysis
python analyser_lyd_main.py --input_dir "path/to/audio" --output_dir "path/to/results" --lat 59.91 --lon 10.75 --date 2024-05-20

# Using custom species list
python analyser_lyd_main.py --input_dir "path/to/audio" --output_dir "path/to/results" --use_default_species_list

# CSV analysis only (no audio splitting)
python analyser_lyd_main.py --input_dir "path/to/audio" --output_dir "path/to/results" --lat 59.91 --lon 10.75 --date 2024-05-20 --no_split
```

## Architecture

### Core Components

#### Streamlit Web Interface (NEW)
**app.py**: Main Streamlit application entry point
**pages/**: Multi-page Streamlit application:
- `1_🎵_Analysis.py`: Configure and run analysis with real-time progress
- `2_📊_Results.py`: View and export analysis results
- `3_🔊_Audio_Explorer.py`: Browse and play detected bird sounds
- `4_⚙️_Settings.py`: Configure application settings
- `5_ℹ️_About.py`: Documentation and help

**streamlit_utils/**: Helper modules for Streamlit:
- `session_state.py`: Session state management
- `file_browser.py`: Directory selection widget
- `progress_tracker.py`: Background task progress tracking
- `audio_player.py`: Audio playback utilities

#### Command Line Interface
**analyser_lyd_main.py**: Main CLI entry point that orchestrates the analysis pipeline:
- Argument parsing and validation
- Directory management
- Pipeline coordination

#### Analysis Functions
**functions/birdnetlib_api.py**: BirdNET integration for species detection (now with progress callbacks)
**functions/artskart_api.py**: Norwegian taxonomic data enrichment via Artskart API  
**functions/splitter_lydfilen.py**: Audio file segmentation based on detections
**functions/statistics.py**: Summary statistics and temporal analysis
**functions/joy2_tester.py**: Visualization generation (Joy Division style plots)
**functions/temporal_analysis.py**: Detailed temporal pattern analysis

### Data Flow

1. Audio files → BirdNET analysis → Raw detections
2. Raw detections → Artskart API → Taxonomic enrichment
3. Enriched data → CSV export + Statistical analysis
4. Optional: Audio splitting into species-specific segments
5. Visualization generation (temporal plots)

### Key Features

- **Dual Analysis Modes**: Location-based (lat/lon/date) or custom species lists
- **Temporal Analysis**: Extracts timestamps from filenames for activity pattern analysis
- **Norwegian Taxonomic Data**: Enriches with Norwegian names, family/order info, red list status
- **Audio Segmentation**: Splits recordings into species-specific clips
- **Platform Support**: Cross-platform FFmpeg integration (Windows/macOS binaries included)
- **Web Interface**: Modern Streamlit UI with real-time progress tracking
- **In-Browser Audio Playback**: Listen to detected bird sounds directly in the web interface
- **Interactive Results**: Filter, sort, and export detection data
- **Settings Management**: Configure defaults and edit species lists through UI

### Dependencies

- **BirdNET**: Core ML model for bird sound detection
- **TensorFlow**: Required by BirdNET
- **Pandas**: Data manipulation and CSV handling
- **Requests**: API communication with Artskart
- **Pydub/FFmpeg**: Audio processing and segmentation
- **Matplotlib/Seaborn/Joypy**: Visualization libraries
- **Streamlit**: Web application framework
- **Streamlit-folium**: Map widget for location selection
- **Streamlit-aggrid**: Advanced data grid component

### Output Structure
```
output_dir/
├── interim/
│   └── enriched_detections.csv    # Main results with taxonomic data
├── lydfiler/
│   └── [species_folders]/         # Audio segments by species
└── figur/
    └── bird_detection_joypy_plot.png  # Temporal activity visualization
```

### FFmpeg Configuration

The system automatically detects platform-specific FFmpeg binaries:
- **Windows**: `ffmpeg_win_bin/` directory
- **macOS**: `ffmpeg_macos_bin/` directory

### Testing Strategy

- Unit tests for core functions (statistics, temporal analysis)
- Integration tests for analysis workflow
- Sample data generation for testing
- Test data isolation in `tests/test_data/`