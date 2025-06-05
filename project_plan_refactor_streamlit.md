# Project Plan: Refactoring Bird Sound Analysis Tool to Streamlit

## Executive Summary

This document outlines the plan for refactoring the existing command-line bird sound analysis tool into a multi-page Streamlit web application. The app will provide an intuitive UI for analyzing bird sounds while maintaining all existing functionality.

## Project Goals

1. Create a user-friendly web interface for the bird sound analysis tool
2. Maintain all existing functionality without adding new features
3. Enable real-time progress tracking and cancellation
4. Provide interactive audio playback capabilities
5. Allow dynamic parameter adjustment through UI controls
6. Organize functionality across multiple pages for better UX

## Technical Architecture

### Core Components to Refactor

1. **Main Application Structure**
   - Convert `analyser_lyd_main.py` to Streamlit app structure
   - Implement multi-page navigation
   - Create session state management for analysis workflow

2. **Background Processing**
   - Implement threading/async processing for long-running operations
   - Add progress tracking with Streamlit progress bars
   - Enable cancellation through session state flags

3. **File Management**
   - Replace command-line arguments with UI-based file browser
   - Implement directory selection widget
   - Maintain local file system integration

4. **Data Display**
   - Convert console output to Streamlit UI components
   - Display results in interactive dataframes
   - Embed visualizations directly in the UI

5. **Audio Playback**
   - Implement browser-based audio player for split segments
   - Create audio file listing with playback controls

## Page Structure

### 1. **Home/Analysis Page** (`pages/1_Analysis.py`)
- **Purpose**: Main analysis configuration and execution
- **Components**:
  - Directory browser for input audio files
  - Analysis mode selector (Location-based vs Species list)
  - Parameter inputs:
    - Location inputs (lat/lon/date) - shown for location mode
    - Species list editor - shown for species list mode
    - Confidence threshold slider (0.0-1.0)
    - Audio splitting toggle
    - Max segments per species input
  - Start Analysis button
  - Progress indicator with cancel button
  - Real-time log display

### 2. **Results Page** (`pages/2_Results.py`)
- **Purpose**: Display analysis results and statistics
- **Components**:
  - Summary statistics cards
  - Interactive dataframe of detections
  - Filters for species, confidence, time
  - Export options for CSV
  - Joypy plot display
  - Download buttons for results

### 3. **Audio Explorer Page** (`pages/3_Audio_Explorer.py`)
- **Purpose**: Browse and play split audio segments
- **Components**:
  - Species selector dropdown
  - Audio file list with metadata
  - Embedded audio player
  - Confidence score display
  - Detection timestamp info

### 4. **Settings Page** (`pages/4_Settings.py`)
- **Purpose**: Configure analysis parameters and paths
- **Components**:
  - Output directory configuration
  - Logger file path setting
  - Species list management:
    - Edit default species list
    - Upload custom species list
    - Preview current list
  - FFmpeg path verification
  - API endpoint configuration (if needed)

### 5. **About Page** (`pages/5_About.py`)
- **Purpose**: Documentation and help
- **Components**:
  - Project description
  - Usage instructions
  - API attributions (BirdNET, Artskart)
  - Troubleshooting guide

## Implementation Details

### Session State Management

```python
# Key session state variables
st.session_state.analysis_running = False
st.session_state.analysis_progress = 0.0
st.session_state.analysis_status = ""
st.session_state.cancel_requested = False
st.session_state.current_results_df = None
st.session_state.analysis_complete = False
st.session_state.output_directory = None
st.session_state.analysis_params = {}
```

### Threading Strategy

```python
# Background task execution
import threading
from concurrent.futures import ThreadPoolExecutor

class AnalysisThread(threading.Thread):
    def __init__(self, params, progress_callback, status_callback):
        super().__init__()
        self.params = params
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self._stop_event = threading.Event()
    
    def stop(self):
        self._stop_event.set()
    
    def run(self):
        # Execute analysis with periodic checks for stop event
        pass
```

### Progress Tracking Integration

```python
# Modify existing functions to accept progress callbacks
def run_birdnet_analysis(..., progress_callback=None):
    total_files = count_audio_files(input_dir)
    processed = 0
    
    for file in audio_files:
        if check_cancellation():
            break
        
        # Process file
        processed += 1
        if progress_callback:
            progress_callback(processed / total_files)
```

### UI Component Mapping

| Current CLI Feature | Streamlit Component |
|-------------------|-------------------|
| `--input_dir` | `st.selectbox()` with directory browser |
| `--output_dir` | `st.text_input()` with folder picker |
| `--lat/--lon` | `st.number_input()` with map widget |
| `--date` | `st.date_input()` |
| `--min_conf` | `st.slider()` |
| `--no_split` | `st.checkbox()` |
| `--max_segments` | `st.number_input()` |
| Progress output | `st.progress()` + `st.status()` |
| Log messages | `st.expander()` with `st.text()` |
| Results CSV | `st.dataframe()` |
| Statistics | `st.metric()` cards |

## Technical Challenges and Solutions

### 1. **Long-Running Processes**
- **Challenge**: BirdNET analysis can take minutes to hours
- **Solution**: 
  - Use threading to prevent UI blocking
  - Implement chunked processing with progress updates
  - Add session persistence for long analyses

### 2. **File System Access**
- **Challenge**: Browser security limits file system access
- **Solution**:
  - Use Streamlit's local file system integration
  - Implement server-side file browsing
  - Maintain current directory-based approach

### 3. **Audio Playback**
- **Challenge**: Playing local audio files in browser
- **Solution**:
  - Use `st.audio()` with file paths
  - Implement audio file serving through Streamlit
  - Consider file size limitations

### 4. **Real-time Updates**
- **Challenge**: Updating UI during analysis
- **Solution**:
  - Use `st.empty()` containers for dynamic content
  - Implement polling mechanism for progress
  - Use Streamlit's experimental rerun for updates

### 5. **Session Management**
- **Challenge**: Maintaining state across page navigation
- **Solution**:
  - Extensive use of `st.session_state`
  - Implement state persistence patterns
  - Clear state management for new analyses

### 6. **Species List Editing**
- **Challenge**: Interactive text editor for species lists
- **Solution**:
  - Use `st.text_area()` with validation
  - Implement add/remove UI with `st.form()`
  - Provide import/export functionality

## Refactoring Steps

### Phase 1: Project Setup
1. Create Streamlit app structure
2. Set up multi-page navigation
3. Implement basic session state management
4. Create UI layouts for each page

### Phase 2: Core Functionality Migration
1. Refactor `run_full_analysis()` for async execution
2. Add progress callbacks to all processing functions
3. Implement cancellation checks throughout pipeline
4. Create UI wrappers for existing functions

### Phase 3: UI Implementation
1. Build Analysis page with all input controls
2. Implement Results page with data display
3. Create Audio Explorer with playback
4. Add Settings page functionality
5. Complete About page documentation

### Phase 4: Integration
1. Connect all pages through session state
2. Implement proper error handling
3. Add input validation
4. Test complete workflow

### Phase 5: Polish
1. Optimize performance
2. Improve UI responsiveness
3. Add helpful tooltips and instructions
4. Implement proper logging display

## File Structure

```
fuglelyd_streamlit/
├── app.py                          # Main Streamlit app
├── pages/
│   ├── 1_Analysis.py              # Analysis configuration
│   ├── 2_Results.py               # Results display
│   ├── 3_Audio_Explorer.py        # Audio playback
│   ├── 4_Settings.py              # Settings management
│   └── 5_About.py                 # Documentation
├── streamlit_utils/
│   ├── __init__.py
│   ├── session_state.py           # Session state helpers
│   ├── file_browser.py            # Directory selection
│   ├── progress_tracker.py        # Progress management
│   └── audio_player.py            # Audio playback utils
├── functions/                      # Existing functions (modified)
│   ├── birdnetlib_api.py         # Add progress callbacks
│   ├── artskart_api.py           # Add progress callbacks
│   ├── splitter_lydfilen.py      # Add progress callbacks
│   ├── statistics.py             # Modify for UI display
│   ├── temporal_analysis.py      # Keep as is
│   └── joy2_tester.py            # Keep as is
└── .streamlit/
    └── config.toml               # Streamlit configuration
```

## Dependencies Update

Add to existing requirements:
```
streamlit>=1.28.0
streamlit-folium>=0.15.0  # For map display
streamlit-aggrid>=0.3.4   # For interactive dataframes
```

## Testing Strategy

1. **Unit Tests**: Maintain existing tests, add UI component tests
2. **Integration Tests**: Test complete workflows through UI
3. **User Acceptance**: Verify all CLI functionality available in UI
4. **Performance Tests**: Ensure UI responsiveness during long analyses

## Migration Checklist

- [ ] Create Streamlit app structure
- [ ] Implement session state management
- [ ] Create all page layouts
- [ ] Add progress tracking to core functions
- [ ] Implement threading for long operations
- [ ] Create file browser component
- [ ] Build analysis configuration UI
- [ ] Implement results display
- [ ] Add audio playback functionality
- [ ] Create species list editor
- [ ] Add settings management
- [ ] Implement error handling
- [ ] Add progress indicators
- [ ] Create cancellation mechanism
- [ ] Test complete workflow
- [ ] Update documentation
- [ ] Optimize performance

## Success Criteria

1. All CLI functionality accessible through UI
2. Analysis can be cancelled mid-process
3. Progress visible during long operations
4. Audio files playable in browser
5. Results immediately visible after analysis
6. Parameters adjustable through UI controls
7. Species list editable within app
8. No new features added (only UI)

## Risk Mitigation

1. **Performance**: Profile and optimize heavy operations
2. **Memory**: Implement data pagination for large results
3. **Compatibility**: Test on multiple browsers
4. **Usability**: Gather feedback early and iterate
5. **Reliability**: Implement comprehensive error handling

## Next Steps

1. Review and approve this plan
2. Set up development environment
3. Create initial Streamlit app structure
4. Begin Phase 1 implementation
5. Iterate based on feedback

This plan ensures a smooth transition from CLI to web UI while maintaining all existing functionality and improving user experience through interactive controls and real-time feedback.