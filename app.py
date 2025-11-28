import streamlit as st
import io
import zipfile
from pdf_processor import process_pdf_stream

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="M&Y Fitness Report Tool",
    page_icon="💪",
    layout="centered"
)

# --- HEADER SECTION ---
st.title("M&Y Fitness Club")
st.markdown("### Report Generator Tool")
# --- FILE UPLOADER ---
uploaded_files = st.file_uploader(
    "Drag and drop PDF files here", 
    type=["pdf"], 
    accept_multiple_files=True
)

# --- PROCESS LOGIC ---
if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} File(s)"):
        
        # Create a progress bar
        progress_bar = st.progress(0)
        
        processed_files = []
        
        for index, uploaded_file in enumerate(uploaded_files):
            # Process the file using the imported function
            processed_pdf_bytes = process_pdf_stream(uploaded_file)
            
            if processed_pdf_bytes:
                # Keep original name but prepend 'Processed_'
                new_name = f"Processed_{uploaded_file.name}"
                processed_files.append((new_name, processed_pdf_bytes))
            
            # Update progress
            progress_bar.progress((index + 1) / len(uploaded_files))

        # --- DOWNLOAD SECTION ---
        st.success("Processing Complete!")
        
        # Scenario A: Single File (Direct Download)
        if len(processed_files) == 1:
            name, data = processed_files[0]
            st.download_button(
                label="Download Processed PDF",
                data=data,
                file_name=name,
                mime="application/pdf",
                type="primary"
            )
            
        # Scenario B: Multiple Files (ZIP Download)
        elif len(processed_files) > 1:
            # Create a ZIP file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for name, data in processed_files:
                    zf.writestr(name, data)
            
            st.download_button(
                label="Download All as ZIP",
                data=zip_buffer.getvalue(),
                file_name="MY_Fitness_Reports.zip",
                mime="application/zip",
                type="primary"
            )