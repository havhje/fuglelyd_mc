# Bird Sound Analysis Tool - Streamlit App

This is the Streamlit web interface for the Bird Sound Analysis Tool.

## Installation

1. Install dependencies:
```bash
# Using uv (recommended)
uv pip install -r pyproject.toml

# Or using pip
pip install -e .
```

2. Ensure FFmpeg is available in the appropriate directory:
   - macOS: `ffmpeg_macos_bin/`
   - Windows: `ffmpeg_win_bin/`

## Running the App

To start the Streamlit app, run:

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Features

### 🎵 Analysis Page
- Select input directory with audio files
- Choose output directory for results
- Configure analysis mode (location-based or species list)
- Set detection parameters
- Monitor real-time progress
- Cancel analysis if needed

### 📊 Results Page
- View all detections in an interactive table
- Filter by species, confidence, and other parameters
- See summary statistics
- Export results as CSV
- View temporal activity visualizations

### 🔊 Audio Explorer
- Browse detected bird sounds by species
- Play audio clips directly in browser
- Filter by confidence level
- View metadata for each clip

### ⚙️ Settings Page
- Configure default directories
- Edit species lists
- Manage system settings
- Customize display preferences

### ℹ️ About Page
- Documentation and usage guide
- Troubleshooting tips
- API attributions

## Tips

1. **File Naming**: For best temporal analysis, name your audio files with timestamps:
   - Format: `YYYYMMDD_HHMMSS`
   - Example: `recording_20240520_063000.wav`

2. **Performance**: 
   - Process smaller batches for faster results
   - Use confidence threshold of 0.5 for balanced results
   - Disable audio splitting for quick overview analysis

3. **Species Lists**:
   - Use scientific names (Latin)
   - One species per line
   - Save as plain text file

## Troubleshooting

- **No audio playback**: Ensure your browser supports HTML5 audio
- **Slow analysis**: Try processing fewer files at once
- **Missing Norwegian names**: Check internet connection for Artskart API

## Command Line Alternative

To use the original command-line interface:

```bash
python analyser_lyd_main.py --input_dir "path/to/audio" --output_dir "path/to/results" --lat 59.91 --lon 10.75 --date 2024-05-20
```