import sys
import os
from pathlib import Path
import logging
from pydub import AudioSegment

def resource_path(relative_path_str: str) -> Path:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        # Not bundled, running in development
        # Assuming this function is in analyser_lyd_main.py or utils.py at project root level
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path_str


def setup_ffmpeg():
    """Configure pydub to use bundled ffmpeg executables"""
    # Define executable names based on platform
    ffmpeg_exe_name = 'ffmpeg.exe' if sys.platform == "win32" else 'ffmpeg'
    ffprobe_exe_name = 'ffprobe.exe' if sys.platform == "win32" else 'ffprobe'
    
    # Determine the bin directory based on platform
    bin_dir = 'ffmpeg_win_bin' if sys.platform == "win32" else 'ffmpeg_macos_bin'
    
    # Get paths to ffmpeg executables
    ffmpeg_path = resource_path(f'{bin_dir}/{ffmpeg_exe_name}')
    ffprobe_path = resource_path(f'{bin_dir}/{ffprobe_exe_name}')
    
    # Fall back to the original macos path if win_bin doesn't exist
    if not ffmpeg_path.exists() and sys.platform == "win32":
        ffmpeg_path = resource_path(f'ffmpeg_macos_bin/{ffmpeg_exe_name}')
        ffprobe_path = resource_path(f'ffmpeg_macos_bin/{ffprobe_exe_name}')

    # Check if executables exist
    if not ffmpeg_path.exists():
        logging.error(f"FFmpeg executable not found at {ffmpeg_path}")
        logging.error("Audio splitting will fail. Ensure ffmpeg is in the correct location.")
        return False

    if not ffprobe_path.exists():
        logging.error(f"FFprobe executable not found at {ffprobe_path}")
        logging.error("Audio splitting will fail. Ensure ffprobe is in the correct location.")
        return False

    # Configure pydub to use our bundled ffmpeg and ffprobe
    AudioSegment.converter = str(ffmpeg_path)
    AudioSegment.ffprobe = str(ffprobe_path)
    
    logging.info(f"FFmpeg configured: {ffmpeg_path}")
    logging.info(f"FFprobe configured: {ffprobe_path}")
    return True