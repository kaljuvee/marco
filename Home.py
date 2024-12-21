import streamlit as st

st.title("Marco - Marketplace Lending (Demo)")

st.markdown("""
Welcome to our comprehensive financial calculator suite! This application provides various tools 
to help you understand and analyze different financial instruments.

### Available Tools

#### 📊 Loan Calculators

1. **ABS Calculator** (pages/12_Loan_Calculator_ABS.py)
   - Calculate Asset-Backed Securities parameters
   - Analyze securitized asset pools
   - Model cash flows and payment structures
   - Essential for ABS investors and analysts

#### 🤖 AI-Powered Tools

1. **Onboarding Agent** (pages/00_OnboardingAgent.py)
   - Interactive AI assistant to help navigate the application
   - Get personalized recommendations
   - Learn about different financial instruments
   - Ask questions about calculations and methodologies

### Getting Started

1. Use the sidebar to navigate between tools
2. Start with the Onboarding Agent if you're new to financial calculations
3. Each tool includes detailed instructions and helpful tooltips

""")

# Add a "Quick Start" section with buttons
st.header("Quick Start")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Launch ABS Calculator"):
        st.switch_page("pages/12_Loan_Calculator_ABS.py")
    
    if st.button("🤖 Talk to Onboarding Agent"):
        st.switch_page("pages/00_OnboardingAgent.py")

with col2:    
    if st.button("💰 Launch Consumer Loan Calculator"):
        st.switch_page("pages/11_Loan_Calculator_Consumer.py")

# Add disclaimer
st.caption("""
This suite of financial calculators is designed for educational and analytical purposes. 
Always consult with financial professionals for important financial decisions.
""")

# Add version info
st.sidebar.markdown("---")
st.sidebar.caption("Version 1.0.0")
