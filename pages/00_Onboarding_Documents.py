import streamlit as st
from ai.analysis_agent import CompanyAnalysisAgent
import os
from datetime import datetime

st.title('Onboarding Agent')
st.subheader('Document Analysis Assistant')

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Add model selection to sidebar
with st.sidebar:
    st.header("Settings")
    model_name = st.selectbox(
        "Select AI Model",
        options=["gpt-4o", "gpt-4o-mini"],
        help="Choose the OpenAI model to use for analysis"
    )

# File upload section with drag and drop
uploaded_file = st.file_uploader(
    "Upload document (PDF, DOCX, or TXT)",
    type=['pdf', 'docx', 'txt'],
    help="Drag and drop your file here or click to browse"
)

# Display file details if uploaded
if uploaded_file and uploaded_file != st.session_state.uploaded_file:
    st.session_state.uploaded_file = uploaded_file
    st.session_state.analysis_complete = False
    
    # Show file details
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.2f} KB",
        "File type": uploaded_file.type
    }
    
    st.write("File Details:")
    for key, value in file_details.items():
        st.write(f"- {key}: {value}")

# Analysis button
if st.session_state.uploaded_file and not st.session_state.analysis_complete:
    if st.button('Analyze Document'):
        with st.spinner('Analyzing document...'):
            try:
                # Pass the uploaded file directly instead of saving it
                analysis_agent = CompanyAnalysisAgent(model_name=model_name)
                extracted_data = analysis_agent.analyze_document(st.session_state.uploaded_file)
                
                st.session_state.extracted_data = extracted_data
                st.session_state.analysis_complete = True
                st.success('Document analyzed successfully!')
                
                # Display analysis results
                st.subheader("Analysis Results")
                st.json(extracted_data)
                
            except Exception as e:
                st.error(f'Error analyzing document: {str(e)}')

# Show previous analysis results
elif st.session_state.analysis_complete:
    st.subheader("Previous Analysis Results")
    st.json(st.session_state.extracted_data) 