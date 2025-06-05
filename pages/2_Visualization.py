import streamlit as st
import os
from PIL import Image

st.set_page_config(
    page_title="Temporal Visualization",
    layout="wide"
)

st.title("Temporal Distribution")
st.divider()

# Check if analysis has been completed
if "output_dir" not in st.session_state or st.session_state.output_dir is None:
    st.warning("No analysis results available. Please run an analysis first.")
    st.stop()

# Look for joyplot image
figur_dir = os.path.join(st.session_state.output_dir, "figur")
joyplot_path = os.path.join(figur_dir, "bird_detection_joypy_plot.png")

if not os.path.exists(joyplot_path):
    st.info("No temporal visualization available. This may be because:")
    st.text("• The analysis is still running")
    st.text("• No temporal data was found in the audio filenames")
    st.text("• There was an error generating the visualization")
else:
    # Display the joyplot
    st.subheader("Bird Detection Activity Over Time")
    
    # Load and display image
    image = Image.open(joyplot_path)
    st.image(image, use_column_width=True)
    
    # Add explanation
    st.divider()
    st.subheader("How to Read This Plot")
    st.text("• Each row represents a different bird species")
    st.text("• The horizontal axis shows the time of day (0-24 hours)")
    st.text("• The height of each curve indicates detection frequency at that time")
    st.text("• Higher peaks mean more detections at that time period")
    st.text("• Species are ordered by total number of detections")