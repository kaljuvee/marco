from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
import os
import tempfile
from dotenv import load_dotenv

class CompanyAnalysisAgent:
    def __init__(self, model_name):
        # Load environment variables and initialize OpenAI
        load_dotenv()
        
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0
        )
        
        # Load the analysis agent template
        template_path = os.path.join('prompts', 'analysis_agent.md')
        try:
            with open(template_path, 'r') as file:
                self.template = file.read()
        except FileNotFoundError:
            raise Exception(f"Analysis template not found at {template_path}")
            
        self.prompt = ChatPromptTemplate.from_template(
            """You are an expert financial analyst and due diligence specialist. Your task is to analyze company documents 
            and extract relevant information according to the provided template structure.

            Instructions:
            1. Carefully read and analyze the provided document
            2. Extract all relevant information that matches the template sections
            3. For each piece of information:
               - Ensure accuracy of extracted data
               - Keep numerical values in their original format
               - Maintain proper context
               - Include source context where relevant
            4. Format the response as follows:
               # Section Name
               field_name: extracted value
               
            5. Special handling:
               - For missing information, skip the field rather than leaving it empty
               - For numerical values, maintain original units and formatting
               - For dates, use consistent YYYY-MM-DD format
               - For lists (like Board Members), use comma-separated values
               - For longer text fields, maintain paragraph structure
            
            Template Structure:
            {template}
            
            Document content:
            {content}
            
            Please analyze the document and extract information following the template structure above.
            Be thorough but only include information that is explicitly present in the document.
            """
        )

    def _load_document(self, uploaded_file):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name
            
        try:
            # Choose loader based on file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == 'pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension == 'docx':
                loader = Docx2txtLoader(file_path)
            else:  # txt
                loader = TextLoader(file_path)
                
            documents = loader.load()
            
            # Clean up temporary file
            os.unlink(file_path)
            
            return documents
        except Exception as e:
            if os.path.exists(file_path):
                os.unlink(file_path)
            raise e

    def _split_documents(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
        return text_splitter.split_documents(documents)

    def _parse_markdown_response(self, response_text):
        """Convert markdown formatted response to dictionary with debug info"""
        extracted_data = {}
        debug_info = {
            'raw_response': response_text,
            'parsed_sections': [],
            'skipped_lines': []
        }
        
        current_section = None
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#'):
                current_section = line.lstrip('#').strip().lower().replace(' ', '_')
                extracted_data[current_section] = {}
                debug_info['parsed_sections'].append(current_section)
                continue
                
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                if current_section:
                    extracted_data[current_section][key] = value
                else:
                    extracted_data[key] = value
            else:
                debug_info['skipped_lines'].append(line)
                    
        return extracted_data, debug_info

    def analyze_document(self, uploaded_file):
        documents = self._load_document(uploaded_file)
        splits = self._split_documents(documents)
        content = " ".join([doc.page_content for doc in splits])
        
        messages = self.prompt.format_messages(
            template=self.template,
            content=content
        )
        
        response = self.llm.invoke(messages)
        
        try:
            extracted_data, debug_info = self._parse_markdown_response(response.content)
            return extracted_data, debug_info
        except Exception as e:
            raise Exception(f"Failed to parse response: {str(e)}")
