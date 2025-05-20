# Bird Species Detection and Analysis Tool

This tool analyzes audio recordings to detect bird species using BirdNET, enriches detections with taxonomic information from Artskart, and splits audio files based on the detections.

## Features

- Detect bird species in audio recordings using BirdNET
- Fetch taxonomic data (Norwegian common names, scientific names, family, order, red list status)
- Save enriched detection data to CSV
- Split audio files into segments by species

## Installation Guide for Windows Users

If you're starting with a fresh Windows installation, follow these steps to set up and use the program:

### First-Time Setup (Done Only Once)

1. **Install Python**:
   - Download the latest Python installer from [python.org](https://www.python.org/downloads/windows/)
   - Run the installer
   - **IMPORTANT**: Check "Add Python to PATH" during installation
   - Complete the installation

2. **Download this project**:
   - Download the ZIP file from GitHub (green "Code" button → "Download ZIP")
   - Extract the ZIP file to a location of your choice (e.g., `C:\BirdAnalysis`)

3. **Open Command Prompt**:
   - Press `Win + R`, type `cmd`, and press Enter
   - Navigate to the project folder:
     ```
     cd C:\path\to\extracted\folder
     ```

4. **Create a virtual environment**:
   ```
   python -m venv venv
   ```

5. **Activate the virtual environment**:
   ```
   venv\Scripts\activate
   ```
   - You'll notice the command prompt now shows `(venv)` at the beginning

6. **Install required packages**:
   ```
   pip install pandas birdnetlib requests tqdm pydub tensorflow librosa
   ```
   - This may take several minutes to complete

7. **Ensure FFmpeg is available**:
   - Download FFmpeg for Windows from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (download a "release build")
   - Extract the ZIP file
   - Create a folder named `ffmpeg_win_bin` in your project directory
   - Copy `ffmpeg.exe` and `ffprobe.exe` from the extracted FFmpeg's `bin` folder to your `ffmpeg_win_bin` folder

### Running the Program (Each Time You Want to Use It)

1. **Open Command Prompt**:
   - Press `Win + R`, type `cmd`, and press Enter
   - Navigate to your project folder:
     ```
     cd C:\path\to\project\folder
     ```

2. **Activate the virtual environment** (only once per Command Prompt session):
   ```
   venv\Scripts\activate
   ```
   - You'll see `(venv)` appear at the beginning of the command line
   - You only need to do this once after opening the Command Prompt, not before each command

3. **Run the program with your desired parameters**:
   ```
   python analyser_lyd_main.py --input_dir "C:\path\to\audio\files" --output_dir "C:\path\for\output" --lat 59.91 --lon 10.75 --date 2025-05-20
   ```
   - Replace the paths and coordinates with your own values
   - You can run this command multiple times with different parameters without reactivating the environment

4. **When you're finished**:
   - You can simply close the Command Prompt window
   - Or if you want to deactivate the virtual environment but keep using the Command Prompt, type:
     ```
     deactivate
     ```

## Command-Line Interface Options

### Required Arguments

- `--input_dir`: Path to the directory containing input audio files
- `--output_dir`: Path to the base directory for outputs (CSV and audio segments)
- `--lat`: Latitude for BirdNET analysis (e.g., 59.91 for Oslo, Norway)
- `--lon`: Longitude for BirdNET analysis (e.g., 10.75 for Oslo, Norway)
- `--date`: Date for BirdNET analysis in YYYY-MM-DD format

### Optional Arguments

- `--min_conf`: Minimum confidence threshold for BirdNET detections (default: 0.5)
- `--no_split`: Disable audio splitting (only generate CSV output)
- `--max_segments`: Maximum audio clips per species (default: 10)
- `--log_level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Examples

```
# Basic usage with default settings
python analyser_lyd_main.py --input_dir "C:\bird_recordings" --output_dir "C:\bird_analysis" --lat 59.91 --lon 10.75 --date 2025-05-20

# Higher confidence threshold and more clips per species
python analyser_lyd_main.py --input_dir "C:\bird_recordings" --output_dir "C:\bird_analysis" --lat 59.91 --lon 10.75 --date 2025-05-20 --min_conf 0.7 --max_segments 20

# Skip audio splitting, only produce CSV output
python analyser_lyd_main.py --input_dir "C:\bird_recordings" --output_dir "C:\bird_analysis" --lat 59.91 --lon 10.75 --date 2025-05-20 --no_split

# More detailed logging
python analyser_lyd_main.py --input_dir "C:\bird_recordings" --output_dir "C:\bird_analysis" --lat 59.91 --lon 10.75 --date 2025-05-20 --log_level DEBUG
```

## Finding Your Latitude and Longitude

To get accurate bird species detections, you should use the latitude and longitude of where your audio recordings were made:

1. Go to [Google Maps](https://www.google.com/maps)
2. Right-click on the location where you recorded the audio
3. Select "What's here?"
4. The coordinates will appear at the bottom of the screen
5. Use these numbers in the `--lat` and `--lon` arguments

## Output Files

1. **Enriched Detections CSV:**
   - File: `output_dir\interim\enriched_detections.csv`
   - Semicolon-separated CSV file containing detailed information for each detection
   - Includes scientific names, common names, timestamps, confidence scores, etc.

2. **Split Audio Segments:**
   - Location: `output_dir\lydfiler\`
   - Subfolders for each detected species (using Norwegian common names)
   - Audio segments (.wav files) corresponding to detections
   - Up to `max_segments` clips per species

## Notes

- BirdNET will download its model files on first run, so internet access is required initially
- The application uses the system's date if no date is specified
- For best results, provide the correct latitude, longitude, and date for your recordings
- Audio splitting relies on FFmpeg, which you set up during installation
- Supported audio formats include WAV, MP3, FLAC, and other formats supported by FFmpeg