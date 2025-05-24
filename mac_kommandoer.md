    *   **Explanation of key arguments:**
        *   `uv run -- python analyser_lyd_main.py` (or `uv run analyser_lyd_main.py`): Executes the script.
        *   `--input_dir "data_input_lyd"`: **Required.** Folder with your audio files.
        *   `--output_dir "data_output_lyd"`: **Required.** Folder where results will be saved.
        *   `--lat LATITUDE`: Optional. Latitude. Defaults to `68.5968` if not provided.
        *   `--lon LONGITUDE`: Optional. Longitude. Defaults to `15.4244` if not provided.
        *   `--date YYYY-MM-DD`: Optional. Recording date. Defaults to the current date if not provided.

### Examples

The input and output directories are `data_input_lyd` and `data_output_lyd` respectively, located within your project folder.
1.  **Analysis with a specific location and date, higher confidence, fewer clips:**
    ```bash
    uv run -- python analyser_lyd_main.py --input_dir "data_input_lyd" --output_dir "data_output_lyd" --lat 59.91 --lon 10.75 --date 2024-07-10 --min_conf 0.5 --max_segments 5
    ```

2.  **Analysis using default location, specific date, low confidence, no audio splitting:**
    ```bash
    uv run -- python analyser_lyd_main.py --input_dir "data_input_lyd" --output_dir "data_output_lyd" --date 2024-05-20 --min_conf 0.1 --no_split
    ```

3.  **Analysis with detailed logging (uses default location and current date if not specified):**
    ```bash
    uv run -- python analyser_lyd_main.py --input_dir "data_input_lyd" --output_dir "data_output_lyd" --log_level DEBUG
    ```
    To specify date and location with debug logging:
    ```bash
    uv run -- python analyser_lyd_main.py --input_dir "data_input_lyd" --output_dir "data_output_lyd" --lat 68.5968 --lon 15.4244 --date 2024-05-20 --log_level DEBUG
    ```

## Output Files

The program will create outputs in the `data_output_lyd` folder (or the folder you specify with `--output_dir`) as described in the main `README.md`:
1.  `interim/enriched_detections.csv`
2.  `lydfiler/` (containing subfolders for each species with audio segments)

## Important Notes

*   **Internet:** BirdNET may download model files the first time it is run or if location settings change significantly.
*   **FFmpeg:** Audio processing and splitting depend on FFmpeg being installed and accessible in your system\'s PATH (which `brew install ffmpeg` should handle).
*   **Paths:** The example commands use relative paths for input and output directories (`"data_input_lyd"`, `"data_output_lyd"`). These are assumed to be directly inside your project folder where you run the `uv run` command. You can also use absolute paths if needed (e.g., `"/Users/your_username/Desktop/MyAudioFiles"`).

Happy bird sound analyzing on your Mac!
