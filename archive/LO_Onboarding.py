import streamlit as st
from ai.analysis_agent import CompanyAnalysisAgent
import yaml
import os
from dotenv import load_dotenv
import pdfkit
import tempfile
from datetime import datetime
from markdown import markdown
import base64
import json

def validate_data(data):
    """Validate that the extracted data contains required fields"""
    if not isinstance(data, dict):
        raise ValueError("Invalid data format - expected dictionary")
    
    required_sections = [
        'basic_information',
        'share_offering_details',
        'company_overview'
    ]
    
    missing_sections = [section for section in required_sections if section not in data]
    if missing_sections:
        raise ValueError(f"Missing required sections: {', '.join(missing_sections)}")
    
    # Validate basic information
    if not data['basic_information'].get('-_company_name'):
        raise ValueError("Company name is required")
    
    return True

def clean_value(value):
    """Clean and format value for markdown"""
    if value is None or value == '':
        return 'Not provided'
    return str(value).strip()

def json_to_markdown(data):
    """Convert JSON data to formatted markdown with validation and cleaning"""
    try:
        validate_data(data)
    except ValueError as e:
        raise ValueError(f"Data validation failed: {str(e)}")
    
    md = "# Company Prospectus\n\n"
    md += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    sections = {
        'basic_information': "Basic Information",
        'share_offering_details': "Share Offering Details", 
        'company_overview': "Company Overview",
        'management_structure': "Management Structure",
        'financial_information': "Financial Information",
        'market_analysis': "Market Analysis",
        'risk_factors': "Risk Factors",
        'future_plans': "Future Plans"
    }
    
    for section_key, section_title in sections.items():
        if section_key in data and isinstance(data[section_key], dict):
            section_data = data[section_key]
            if section_data:  # Only add section if it has data
                md += f"## {section_title}\n\n"
                for key, value in section_data.items():
                    if value:  # Only add field if it has a value
                        clean_key = key.replace('-_', '').replace('_', ' ').title()
                        clean_val = clean_value(value)
                        md += f"**{clean_key}**: {clean_val}\n\n"
    
    if md == f"# Company Prospectus\n\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n":
        raise ValueError("No valid data found to generate prospectus")
        
    return md

def save_json(data, company_name):
    """Save JSON data to data folder"""
    # Create data directory if it doesn't exist
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create filename with timestamp and company name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_company_name = ''.join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_company_name}_{timestamp}.json"
    
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath

def save_markdown(content, company_name):
    """Save markdown content to data folder"""
    # Create data directory if it doesn't exist
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create filename with timestamp and company name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_company_name = ''.join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_company_name}_{timestamp}.md"
    
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

# Load environment variables
load_dotenv()

st.title('IPOGate')
st.subheader('Your Gateway to Public Markets')

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "gpt-4o"
if 'show_editable' not in st.session_state:
    st.session_state.show_editable = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Add model selection to sidebar
with st.sidebar:
    st.header("Settings")
    model_name = st.selectbox(
        "Select AI Model",
        options=["gpt-4o", "gpt-4o-mini"],
        help="Choose the OpenAI model to use for analysis",
        key='selected_model'
    )

# File upload section
uploaded_file = st.file_uploader("Upload company document (PDF, DOCX, or TXT)", 
                               type=['pdf', 'docx', 'txt'])

if uploaded_file and uploaded_file != st.session_state.uploaded_file:
    st.session_state.uploaded_file = uploaded_file
    st.session_state.analysis_complete = False
    st.session_state.show_editable = False

# Analysis button
if st.session_state.uploaded_file and not st.session_state.analysis_complete:
    if st.button('Analyze Document'):
        with st.spinner('Analyzing document...'):
            try:
                analysis_agent = CompanyAnalysisAgent(model_name=st.session_state.selected_model)
                extracted_data, debug_info = analysis_agent.analyze_document(st.session_state.uploaded_file)
                st.session_state.extracted_data = extracted_data
                st.session_state.debug_info = debug_info
                st.session_state.analysis_complete = True
                st.success('Document analyzed successfully!')
            except Exception as e:
                st.error(f'Error analyzing document: {str(e)}')

# Show analysis results
if st.session_state.analysis_complete and not st.session_state.show_editable:
    st.subheader("Analysis Results")
    st.json(st.session_state.extracted_data)
    
    if st.button('Proceed to Edit Information'):
        st.session_state.show_editable = True

# Edit form
if st.session_state.show_editable:
    with st.form("edit_form"):
        st.subheader("Company Details")
        st.write("Please review and edit the extracted information:")
        
        data = st.session_state.extracted_data
        
        # Basic Information
        with st.expander("Basic Information", expanded=True):
            basic_info = data.get('basic_information', {})
            company_name = st.text_input(
                "Company Name", 
                value=basic_info.get('-_company_name', '')
            )
            company_type = st.text_input(
                "Company Type", 
                value=basic_info.get('-_company_type', '')
            )
            jurisdiction = st.text_input(
                "Jurisdiction", 
                value=basic_info.get('-_jurisdiction', '')
            )
            
        # Share Offering Details
        with st.expander("Share Offering Details"):
            share_info = data.get('share_offering_details', {})
            num_shares = st.text_input(
                "Number of Shares", 
                value=share_info.get('-_number_of_shares', '')
            )
            nominal_value = st.text_input(
                "Nominal Value per Share", 
                value=share_info.get('-_nominal_value_per_share', '')
            )
            
        # Company Overview
        with st.expander("Company Overview"):
            overview = data.get('company_overview', {})
            founding_story = st.text_area(
                "Founding Story", 
                value=overview.get('-_founding_story', '')
            )
            core_business = st.text_area(
                "Core Business", 
                value=overview.get('-_core_business_description', '')
            )
            
        # Form submit button
        if st.form_submit_button('Save Changes'):
            # Update the stored data with edited values
            if 'basic_information' not in data:
                data['basic_information'] = {}
            data['basic_information'].update({
                '-_company_name': company_name,
                '-_company_type': company_type,
                '-_jurisdiction': jurisdiction
            })
            
            # Get company name for filename
            company_name = data['basic_information'].get('-_company_name', 'company')
            
            # Save JSON file
            json_path = save_json(data, company_name)
            
            st.success(f'Changes saved successfully! Data written to: {json_path}')

    # Debug information expander
    with st.expander("Debug Information", expanded=False):
        st.subheader("Raw LLM Response")
        st.code(st.session_state.debug_info['raw_response'], language='markdown')
        
        st.subheader("Parsed Sections")
        st.json(st.session_state.debug_info['parsed_sections'])
        
        if st.session_state.debug_info['skipped_lines']:
            st.subheader("Skipped Lines")
            st.json(st.session_state.debug_info['skipped_lines'])
        
        st.subheader("Structured Data")
        st.json(st.session_state.extracted_data)

    if st.button('Generate Prospectus'):
        try:
            if not st.session_state.extracted_data:
                st.error("No data available. Please analyze a document first.")
                st.stop()
            
            # Convert JSON to markdown
            with st.spinner('Generating prospectus...'):
                markdown_content = json_to_markdown(st.session_state.extracted_data)
                
                if not markdown_content.strip():
                    st.error("Generated prospectus is empty. Please check the extracted data.")
                    st.stop()
                
                # Get company name for filename
                company_name = st.session_state.extracted_data.get('basic_information', {}).get('-_company_name', 'company')
                
                # Save markdown file
                markdown_path = save_markdown(markdown_content, company_name)
                
                # Show preview of markdown
                st.subheader("Generated Prospectus Content")
                st.markdown(markdown_content)
                
                # Create download button for markdown
                st.download_button(
                    label="Download Prospectus (Markdown)",
                    data=markdown_content,
                    file_name=f"{company_name}_prospectus.md",
                    mime="text/markdown"
                )
                
                # Show file location
                st.success(f'Prospectus content generated and saved to: {markdown_path}')
                
                # Add info about PDF generation
                st.info('To generate PDF from command line, run:\n' +
                       f'`python utils/pdf_generator.py {markdown_path}`')
                
        except ValueError as e:
            st.error(f'Validation error: {str(e)}')
        except Exception as e:
            st.error(f'Error generating prospectus content: {str(e)}')
            st.error("Please ensure the document analysis completed successfully and try again.")
