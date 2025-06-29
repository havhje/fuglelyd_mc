# Bird Species Detection and Analysis Tool
Created by: Håvard Hjermstad-Sollerud

This tool analyzes audio recordings to detect bird species using BirdNET, enriches detections with taxonomic information from Artskart (Norwegian Biodiversity Information Centre API), and can split audio files into smaller clips based on the detections.

## Table of Contents
- [Quick Start Guide](#quick-start-guide)
- [Features](#features)
- [Installation Guide for Windows Users](#installation-guide-for-windows-users)
  - [Part 1: Required Software](#part-1-required-software-done-only-once)
  - [Part 2: Setting Up the Project Environment](#part-2-setting-up-the-project-environment-done-only-once-in-the-project-folder)
  - [Part 3: Running the Program](#part-3-running-the-bird-analysis-program-each-time-you-want-to-use-it)
- [Audio File Naming for Temporal Analysis](#audio-file-naming-for-temporal-analysis)
- [Finding Your Latitude and Longitude](#finding-your-latitude-and-longitude)
- [Command Reference](#command-reference)
- [Real-World Examples](#real-world-examples)
- [Output Files](#output-files)
- [Important Notes](#important-notes)

## Quick Start Guide

**Already have Python 3.11 and want to jump in?**

1. Download this project and extract it to `C:\BirdAnalysis`
2. Download FFmpeg files and place them in `C:\BirdAnalysis\ffmpeg_win_bin\`
3. Open Command Prompt, navigate to the folder, and run:
   ```cmd
   cd C:\BirdAnalysis
   python -m venv tf_venv
   tf_venv\Scripts\activate
   python -m pip install pandas tqdm pygwalker streamlit requests pydub tensorflow ffmpeg birdnetlib pyaudio librosa "resampy>=0.4.3" "seaborn>=0.13.2" "joypy>=0.2.6" "scipy>=1.15.3"
   ```
4. Run your first analysis:
   ```cmd
   python analyser_lyd_main.py --input_dir "C:\MyAudioFiles" --output_dir "C:\Results" --lat 59.91 --lon 10.75 --date 2024-05-20
   ```

**Need detailed setup instructions?** Continue to the [Installation Guide](#installation-guide-for-windows-users) below.

## Features

*   Detect bird species in audio recordings using BirdNET.
*   Fetch taxonomic data (Norwegian common names, scientific names, family, order, red list status) from Artskart.
*   Save enriched detection data to a CSV file (a spreadsheet-like format).
*   Split audio files into segments by species and save them into dedicated folders.

## Installation Guide for Windows Users

This guide is designed to be as simple as possible, even if you don't have extensive computer or programming experience. Please follow the steps carefully.

### Part 1: Required Software (Done Only Once)

Before you can use the bird analysis tool, you need to install some basic software on your computer.

#### Step 1.1: Install Python 3.11

Python is the programming language this tool is written in. We need a specific version (3.11) for everything to work correctly.

1.  **Open your web browser** (e.g., Edge, Chrome, Firefox) and go to Python's official download page for Windows:
    [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

2.  **Scroll down the page** until you see the heading "Looking for a specific release?". Find **Python 3.11.x** in the list (for example, "Python 3.11.9" - the highest number after 3.11 is usually best).
    *   *Avoid newer versions like 3.12 or 3.13, as they may not yet be compatible with this program.*

3.  Click on the link for the Python 3.11.x version you've chosen. This will take you to a page specific to that version.

4.  **Scroll down this new page** until you find a table of files ("Files").
    *   Look for a link named **"Windows installer (64-bit)"**. Most modern computers are 64-bit. Click this link to download the installer file. It will typically be named something like `python-3.11.9-amd64.exe`.

5.  **Run the installer file:**
    *   Once the file is downloaded, find it in your Downloads folder and double-click it to start the installation.
    *   **VERY IMPORTANT!** In the first window that appears, look at the bottom and **check the box next to "Add python.exe to PATH"** (or "Add Python 3.11 to PATH"). This is crucial for the program to work.
        ![Python PATH example](https://i.stack.imgur.com/2yL4q.png) *(Illustrative image – text may vary slightly)*
    *   Then, click on **"Install Now"** to start the default installation.
    *   Follow the on-screen instructions. If Windows asks if you want to allow the app to make changes, click "Yes".
    *   When the installation is complete, you can close the installation window.

#### Step 1.2: Download and Prepare FFmpeg (for audio processing)

FFmpeg is a tool needed for working with audio files (especially for splitting them into smaller clips). **This method does NOT require administrator access.**

1.  **Open your web browser** and go to the FFmpeg builds page by Gyan.dev:
    [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

2.  **Find the correct version:** Look for the "release builds" section.
    *   Download the file named **`ffmpeg-git-full.7z`**. This is a compressed file (archive).

3.  **Extract FFmpeg:**
    *   `.7z` is an archive format, similar to `.zip`. You'll need a program to extract `.7z` files. If you don't have one, [7-Zip](https://www.7-zip.org/) is a free and good option. Download and install 7-Zip if you need it.
    *   Once 7-Zip is installed (or if you already have a program that can open .7z files), right-click on the downloaded `ffmpeg-git-full.7z` file.
    *   Select "7-Zip" (or the name of your extraction program) from the menu, and then choose something like "Extract Here" or "Extract to ffmpeg-git-full\". This will create a new folder with the same name as the file.
    *   **Example:** If you downloaded the file to `C:\Downloads`, you'll get a folder named `C:\Downloads\ffmpeg-git-full`.

4.  **Locate `ffmpeg.exe` and `ffprobe.exe`:**
    *   Open the folder you just extracted (e.g., `ffmpeg-git-full`).
    *   Inside this, there will be another folder, often with a longer name including a version number (e.g., `ffmpeg-2024-05-20-git-abc123xyz-full_build`). Open this folder.
    *   Inside that, you will find a folder named **`bin`**. Open the `bin` folder.
    *   Inside the `bin` folder, you will find the files `ffmpeg.exe` and `ffprobe.exe`. These are the two files we need.

5.  **Copy FFmpeg executables to the project (This step is done AFTER downloading the bird analysis project in Step 1.3):**
    *   For now, just remember where you found `ffmpeg.exe` and `ffprobe.exe`. We will copy them in a later step.

#### Step 1.3: Download This Bird Analysis Project

1.  **Go to the project's page on GitHub** (you will be provided with a link to this page).
2.  Look for a green button, usually labeled **"<> Code"**. Click on it.
3.  In the menu that appears, select **"Download ZIP"**.
4.  Save the ZIP file somewhere you can easily find it, like your Desktop or Documents folder.
5.  **Extract the ZIP file:**
    *   Right-click on the downloaded ZIP file.
    *   Select "Extract All...".
    *   Choose where you want to save the extracted files. It's a good idea to create a dedicated folder for the project, for example, `C:\BirdAnalysis`. Let's call this your **"project folder"**.

#### Step 1.4: Place FFmpeg Files into the Project

Now, we'll copy the FFmpeg files you located in Step 1.2 into the bird analysis project folder.

1.  Open your **project folder** (e.g., `C:\BirdAnalysis` - the one you created in Step 1.3).
2.  Inside this project folder, create a **new folder** and name it exactly: `ffmpeg_win_bin`
3.  Go back to the FFmpeg `bin` folder you located in Step 1.2.4 (the one containing `ffmpeg.exe` and `ffprobe.exe`).
4.  **Copy** the `ffmpeg.exe` file and the `ffprobe.exe` file.
5.  **Paste** these two files into the `ffmpeg_win_bin` folder you just created inside your project folder.
    Your project folder structure should now look something like this:
    ```
    C:\BirdAnalysis\
    ├── ffmpeg_win_bin\
    │   ├── ffmpeg.exe
    │   └── ffprobe.exe
    ├── analyser_lyd_main.py  (and other .py files)
    └── (other project files and folders)
    ```
    This program is designed to automatically find FFmpeg in this specific location, so you don't need administrator rights to change system settings.

### Part 2: Setting Up the Project Environment (Done Only Once in the project folder)

Each time you start a new Python project, it's good practice to create a "virtual environment." This isolates your project and its dependencies from other Python projects on your machine.

1.  **Open Command Prompt:**
    *   Press the **Windows key + R** simultaneously.
    *   A small window called "Run" will appear. Type `cmd` in the box and press Enter (or click "OK").
    *   A black window (Command Prompt) will open.

2.  **Navigate to your project folder in Command Prompt:**
    *   In Command Prompt, type `cd` (which stands for "change directory"), followed by a space, and then the path to your **project folder** (the one you created in Step 1.3, e.g., `C:\BirdAnalysis`).
        ```cmd
        cd C:\BirdAnalysis
        ```
    *   Press Enter. You should now see that the path in Command Prompt changes to your project folder.

3.  **Create a virtual environment:**
    *   Type the following command in Command Prompt (make sure you are still in your project folder):
        ```cmd
        python -m venv tf_venv
        ```
    *   Press Enter. This will create a new folder named `tf_venv` inside your project folder. This folder contains an isolated Python installation for the project.

4.  **Activate the virtual environment:**
    *   Type the following command:
        ```cmd
        tf_venv\Scripts\activate
        ```
    *   Press Enter. You will now see `(tf_venv)` at the very beginning of the line in Command Prompt. This means the virtual environment is active.
        *(Whenever you want to work with this project in the future and open a new Command Prompt window, you'll need to repeat step 2 (navigate to the folder) and this step 4 (activate the environment) before you can run the program.)*

5.  **Upgrade Pip (Python's package installer):**
    *   It's good practice to have the latest version of Pip. Type:
        ```cmd
        python -m pip install --upgrade pip
        ```
    *   Press Enter.

6.  **Install required Python packages:**
    *   Now, we'll install all the additional libraries (software packages) that the bird analysis program needs. Copy and paste (or type carefully) the following long command into Command Prompt:
        ```cmd
        python -m pip install pandas tqdm pygwalker streamlit requests pydub tensorflow ffmpeg birdnetlib pyaudio librosa "resampy>=0.4.3" "seaborn>=0.13.2" "joypy>=0.2.6" "scipy>=1.15.3"
        ```
    *   Press Enter. This might take several minutes, as many files are downloaded and installed. You'll see a lot of text scrolling on the screen. Wait until it's finished and you see the `(tf_venv)` prompt again.
        *   *If you get error messages here, double-check that you installed Python 3.11 (not a different version) and that you activated the virtual environment `(tf_venv)` correctly.*

You have now completed the one-time setup!

### Part 3: Running the Bird Analysis Program (Each Time You Want to Use It)

1.  **Make sure you have audio files ready:**
    *   Place the audio files you want to analyze (e.g., `.wav` or `.mp3` files) in a dedicated folder. For example, create a folder `C:\MyAudioRecordings`.
    *   **IMPORTANT for Temporal Analysis:** For the program to perform detailed temporal analysis (showing when species are active throughout the day), your audio filenames must contain timestamps. See the "Audio File Naming for Temporal Analysis" section below for details.

2.  **Open Command Prompt:**
    *   Press **Windows key + R**, type `cmd`, press Enter.

3.  **Navigate to your project folder:**
    *   (Remember to replace `C:\BirdAnalysis` with the actual path to your project folder)
        ```cmd
        cd C:\BirdAnalysis
        ```
    *   Press Enter.

4.  **Activate the virtual environment:**
    *   (This needs to be done once per Command Prompt session)
        ```cmd
        tf_venv\Scripts\activate
        ```
    *   Press Enter. You should see `(tf_venv)` at the start of the line.

5.  **Run the analysis program:**
    Now you'll type the command to start the analysis. You need to replace the parts in quotes with your own paths and values.
    The basic command structure is:
    ```cmd
    python analyser_lyd_main.py --input_dir "PATH_TO_YOUR_AUDIO_FOLDER" --output_dir "PATH_TO_WHERE_RESULTS_SHOULD_BE_SAVED" --lat LATITUDE --lon LONGITUDE --date YYYY-MM-DD [OPTIONAL_ARGUMENTS]
    ```
    *   **Explanation of the required parts:**
        *   `python analyser_lyd_main.py`: This starts the program itself.
        *   `--input_dir "PATH_TO_YOUR_AUDIO_FOLDER"`: Replace `"PATH_TO_YOUR_AUDIO_FOLDER"` with the actual path to the folder where your audio files are located (e.g., `"C:\MyAudioRecordings"`). **Remember the quotes if the path contains spaces.**
        *   `--output_dir "PATH_TO_WHERE_RESULTS_SHOULD_BE_SAVED"`: Replace `"PATH_TO_WHERE_RESULTS_SHOULD_BE_SAVED"` with the path to a folder where you want the program to save the result files (CSV file and audio clips). The program will create subfolders here. E.g., `"C:\BirdAnalysisResults"`.
        *   `--lat LATITUDE`: Replace `LATITUDE` with the latitude of the location where the audio recordings were made (e.g., `59.91` for Oslo).
        *   `--lon LONGITUDE`: Replace `LONGITUDE` with the longitude of the location (e.g., `10.75` for Oslo).
        *   `--date YYYY-MM-DD`: Replace `YYYY-MM-DD` with the date the recordings were made, in the format year-month-day (e.g., `2024-05-20`).

    *   **See "Command Reference" and "Real-World Examples" below for more detailed examples and optional arguments.**

    *   Press Enter to start the analysis. This can take time, depending on how many and how long your audio files are. You will see progress information in the Command Prompt window.
    *   BirdNET will download model files the first time it's run with new settings, so internet access is required then.

6.  **When you're finished:**
    *   You can simply close the Command Prompt window.
    *   Or, if you want to deactivate the virtual environment but keep using Command Prompt, type:
        ```cmd
        deactivate
        ```
    *   The `(tf_venv)` will then disappear from the start of the line.

## Audio File Naming for Temporal Analysis

The program includes advanced temporal analysis features that show when different bird species are most active throughout the day. **For this to work, your audio filenames must contain timestamp information.**

### Supported Timestamp Formats

The program automatically detects timestamps in various filename formats:

#### **Format 1: YYYYMMDD_HHMMSS (Recommended)**
```
recorder_20240521_190002.wav
2MA06968_20240521_190002.wav
birdsong_20240521_190002_extra_info.wav
```
- **YYYYMMDD**: Year, month, day (e.g., `20240521` = May 21, 2024)
- **HHMMSS**: Hour, minute, second in 24-hour format (e.g., `190002` = 19:00:02 = 7:00:02 PM)

#### **Format 2: YYYY-MM-DD_HH-MM-SS**
```
recording_2024-05-21_19-00-02.wav
fieldwork_2024-05-21_07-30-00.wav
```

#### **Format 3: ISO-like Format (YYYYMMDDTHHMMSS)**
```
audio_20240521T190002.wav
sound_20240521T073000.wav
```

#### **Format 4: Underscore Separated (YYYY_MM_DD_HH_MM_SS)**
```
bird_2024_05_21_19_00_02.wav
sound_2024_05_21_07_30_00.wav
```

#### **Format 5: All Dashes (YYYY-MM-DD-HH-MM-SS)**
```
recording-2024-05-21-19-00-02.wav
```

#### **Format 6: Unix Timestamp (10 digits)**
```
recording_1716310802.wav
audio_1716310802_session1.wav
```

### Temporal Analysis Output

When timestamps are successfully parsed from filenames, the program will show:

- **Recording Sessions Overview**: How many recording sessions and time span covered
- **Species Temporal Profiles**: For each species detected:
  - **Peak activity window**: The 1-hour period with most detections (e.g., "05:00-06:00 (89 detections)")
  - **Active period**: From first to last detection with total duration (e.g., "04:30-07:45 (3h 15m)")
  - **Call pattern**: Calling behavior analysis (e.g., "Clustered (avg 2.3 min gaps, range: 0.5-8.2 min, std: 1.4 min)")
- **Hourly Activity Distribution**: Visual bar chart showing bird activity by hour

### Important Notes

- **Timestamp must be in the filename**: The program extracts timestamps from the audio filename, not from file metadata
- **24-hour format required**: Use 24-hour time format (e.g., `190002` for 7:00:02 PM)
- **Consistent naming**: Use the same timestamp format for all files in a session
- **No temporal analysis without timestamps**: If filenames don't contain recognizable timestamps, the program will still detect species but won't show temporal patterns

### Example Output

```
SPECIES TEMPORAL PROFILES:

tjeld:
  Peak activity: 05:00-06:00 (89 detections)
  Active period: 04:30-07:45 (3h 15m)
  Call pattern: Clustered (avg 2.3 min gaps, range: 0.5-8.2 min, std: 1.4 min)

fiskemåke:
  Peak activity: 19:00-20:00 (12 detections)  
  Active period: 19:36-20:15 (39m)
  Call pattern: Regular (avg 8.2 min gaps, range: 2.1-15.3 min, std: 4.7 min)
```

## Finding Your Latitude and Longitude

For the best results, you should use the accurate latitude and longitude for the location where your audio recordings were made:

1.  Go to [Google Maps](https://www.google.com/maps).
2.  Find the location on the map.
3.  Right-click on the exact spot on the map.
4.  A small information box will appear at the bottom of the screen, or in the menu that pops up, showing the coordinates (two numbers, e.g., `59.912345, 10.756789`).
5.  The first number is the latitude (`--lat`), and the second is the longitude (`--lon`).

## Command Reference

### Required Arguments
| Argument | Description | Example |
|----------|-------------|---------|
| `--input_dir` | Folder containing audio files | `"C:\MyRecordings"` |
| `--output_dir` | Where to save results | `"C:\Results"` |

### Analysis Mode (Choose One)

#### Location-Based Analysis (Default)
| Argument | Description | Example |
|----------|-------------|---------|
| `--lat` | Latitude of recording location | `59.91` (Oslo) |
| `--lon` | Longitude of recording location | `10.75` (Oslo) |
| `--date` | Date of recordings (YYYY-MM-DD) | `2024-05-20` |

#### Custom Species List Analysis
| Argument | Description | Example |
|----------|-------------|---------|
| `--use_default_species_list` | Use built-in Norwegian species list | *(no value needed)* |
| `--custom_species_list` | Path to your own species list file | `"C:\MyLists\birds.txt"` |

### Optional Settings
| Argument | Default | Description | Example |
|----------|---------|-------------|---------|
| `--min_conf` | `0.5` | Detection confidence (0.0-1.0) | `0.75` (higher confidence) |
| `--max_segments` | `10` | Max audio clips saved per species | `5` (fewer clips) |
| `--no_split` | Off | Skip audio splitting (CSV only) | *(no value needed)* |
| `--log_level` | `INFO` | Logging detail level | `DEBUG` or `WARNING` |
| `--logger_file` | None | Path to logger CSV file | `"C:\logs\analysis.csv"` |

### Quick Command Templates

**Basic Analysis:**
```cmd
python analyser_lyd_main.py --input_dir "INPUT_FOLDER" --output_dir "OUTPUT_FOLDER" --lat LATITUDE --lon LONGITUDE --date YYYY-MM-DD
```

**Fast Analysis (No Audio Clips):**
```cmd
python analyser_lyd_main.py --input_dir "INPUT_FOLDER" --output_dir "OUTPUT_FOLDER" --lat LATITUDE --lon LONGITUDE --date YYYY-MM-DD --no_split
```

**High Confidence Analysis:**
```cmd
python analyser_lyd_main.py --input_dir "INPUT_FOLDER" --output_dir "OUTPUT_FOLDER" --lat LATITUDE --lon LONGITUDE --date YYYY-MM-DD --min_conf 0.75
```

**Using Default Species List:**
```cmd
python analyser_lyd_main.py --input_dir "INPUT_FOLDER" --output_dir "OUTPUT_FOLDER" --use_default_species_list
```

## Real-World Examples

**Example 1: Morning Bird Survey in Oslo**
You recorded birds in Oslo's Frogner Park on May 15, 2024:
```cmd
python analyser_lyd_main.py --input_dir "C:\BirdRecordings\FrognerPark" --output_dir "C:\Analysis\FrognerPark_May15" --lat 59.9139 --lon 10.7522 --date 2024-05-15
```
*Expected runtime: 2-5 minutes per hour of audio*
*Output: CSV file + audio clips + activity visualization*

**Example 2: Bergen Coastal Recording**
Recordings from Bergen, Norway coast on June 10, 2024:
```cmd
python analyser_lyd_main.py --input_dir "C:\FieldRecordings\Bergen_Coast" --output_dir "C:\BirdAnalysis_Results\Bergen" --lat 60.39 --lon 5.32 --date 2024-06-10
```
*Expected: Seabird species detection with temporal patterns*

**Example 3: Quick Species Check (No Audio Splitting)**
Fast analysis for species identification only:
```cmd
python analyser_lyd_main.py --input_dir "C:\QuickCheck" --output_dir "C:\Results\Quick" --lat 59.91 --lon 10.75 --date 2024-05-15 --no_split --min_conf 0.7
```
*Faster processing, CSV results only, higher confidence threshold*

**Example 4: High-Confidence Analysis with Fewer Clips**
For cleaner results with only the most confident detections:
```cmd
python analyser_lyd_main.py --input_dir "C:\FieldRecordings\June2024" --output_dir "C:\BirdAnalysis_Results" --lat 60.39 --lon 5.32 --date 2024-06-15 --min_conf 0.75 --max_segments 3
```
*Only saves 3 audio clips per species, minimum 75% confidence*

**Example 5: Using Project's Default Species List**
Analyzes based on the built-in Norwegian species list:
```cmd
python analyser_lyd_main.py --input_dir "C:\FieldRecordings\June2024" --output_dir "C:\BirdAnalysis_Results" --use_default_species_list
```
*Uses predefined species list, ignores location/date parameters*

**Example 6: Custom Species List for Specific Research**
Using your own target species list:
```cmd
python analyser_lyd_main.py --input_dir "C:\FieldRecordings\June2024" --output_dir "C:\BirdAnalysis_Results" --custom_species_list "C:\MyProject\BirdLists\target_birds.txt"
```
*Only detects species from your custom list*

**Example 7: Low Confidence for Rare Species Detection**
Catching weaker signals that might be rare species:
```cmd
python analyser_lyd_main.py --input_dir "C:\RareSpecies\Recording" --output_dir "C:\Results\RareSpecies" --use_default_species_list --min_conf 0.1 --no_split
```
*Very low confidence threshold, no audio splitting for faster processing*

### Using a Custom Species List (Further Details)

As shown in the examples, you have two ways to use custom species lists:

*   **`--use_default_species_list`**: This flag tells the program to use the predefined `data_input_artsliste/arter.txt` file located within the project structure. This is the simplest way if that list meets your needs.
    ```cmd
    python analyser_lyd_main.py --input_dir ... --output_dir ... --use_default_species_list
    ```

*   **`--custom_species_list "PATH_TO_YOUR_FILE.txt"`**: Use this if you have your own separate species list file. Provide the full path to your `.txt` file.
    ```cmd
    python analyser_lyd_main.py --input_dir ... --output_dir ... --custom_species_list "C:\Path\To\My\CustomList.txt"
    ```

When either of these custom list options is used, the `--lat`, `--lon`, and `--date` parameters are ignored, as BirdNET's location-based filtering is bypassed in favor of the provided list.

**Format for custom species list files:**

1.  Create a plain text file (e.g., `my_species.txt`).
2.  Each line in the file should contain **one species name** in the exact format that BirdNET expects: `Scientific name_Common English Name`.
    *   **Example:**
        ```
        Bubo bubo_Eurasian Eagle-Owl
        Erithacus rubecula_European Robin
        Turdus merula_Common Blackbird
        ```
    *   You can find the correct names by looking at the output of a previous analysis or BirdNET documentation.
    *   The `data_input_artsliste/arter.txt` file in the project is an example.

## Output Files

The program will create the following in the folder you specified for `--output_dir`:

1.  **Enriched Detections CSV:**
    *   Path: `YOUR_OUTPUT_FOLDER\interim\enriched_detections.csv`
    *   Description: A semicolon-separated CSV file (can be opened in Excel, LibreOffice Calc, etc.) containing detailed information for each bird sound detection. Includes scientific names, common names (English and Norwegian for species, family, order), start/end times of detection, confidence scores, red list status, and file paths.

2.  **Split Audio Segments:**
    *   Path: `YOUR_OUTPUT_FOLDER\lydfiler\`
    *   Description: This directory will contain subfolders for each detected species (named with the Norwegian common name, e.g., "European Robin" if the species is "Erithacus rubecula" and a Norwegian name is found). Inside each species folder, you'll find the individual audio segments (.wav files) corresponding to the detections for that species. File names for segments will typically include the original audio file name, start/end times, and the species name for easy identification.

3.  **Joy Division Activity Plot (PNG Image):**
    *   Path: `YOUR_OUTPUT_FOLDER\figur\bird_detection_joy_division_plot.png`
    *   Description: A PNG image visualizing the daily activity patterns of detected bird species in a **Joy Division style ridgeline plot**. Each species is represented by a "ridge" (a density plot) showing its detection frequency throughout a 24-hour cycle. The ridges are sorted by their earliest peak activity time. The fill color of each ridge indicates the average detection confidence for that species (typically, darker/more purple means higher confidence, and lighter/yellower means lower confidence, with a color bar provided for reference). The plot title and annotations provide further details, including a note about the minimum number of detections required for a species to be included (default is 5).

## Important Notes

*   **Internet:** BirdNET will download model files the first time it is run (or if you significantly change latitude/longitude). Ensure you have internet access then.
*   **FFmpeg:** Audio splitting depends on `ffmpeg.exe` and `ffprobe.exe` being in the `ffmpeg_win_bin` folder within your project directory, as described in Step 1.4. If audio splitting fails, ensure these files are correctly placed.
*   **Paths with Spaces:** If any file or folder paths in your commands contain spaces (e.g., "My Documents" or "Field Recordings"), you must always enclose the entire path in double quotes (`"`) in the Command Prompt. For example: `"--input_dir C:\My Recordings\Audio"` should be `"--input_dir "C:\My Recordings\Audio""`.
*   **Audio Formats:** The program should handle common audio formats like WAV and MP3. If you have issues with a specific format, ensure FFmpeg is set up correctly, as it handles the audio decoding.
*   **No Detections?** If the program runs but finds no detections:
    *   Double-check your `--input_dir` path to ensure it points to a folder with audio files.
    *   Listen to your audio files to confirm there are audible bird sounds.
    *   Try lowering the `--min_conf` value (e.g., `--min_conf 0.25`) to catch weaker signals.
    *   Ensure the `--lat`, `--lon`, and `--date` parameters are reasonably accurate for your recordings.

Happy bird sound analyzing!
