import streamlit as st

st.title("Marco - Marketplace Lending (Demo)")

st.markdown("""
Welcome to our comprehensive financial calculator suite! This application provides various tools 
to help you understand and analyze different financial instruments.

### Available Tools

#### 📊 Loan Calculators

1. **MBS Calculator** (pages/10_Loan_Calculator_MBS.py)
   - Calculate Mortgage-Backed Securities parameters
   - Visualize payment schedules and amortization
   - Analyze principal and interest breakdowns
   - Ideal for financial professionals and analysts

2. **Consumer Loan Calculator** (pages/11_Loan_Calculator_Consumer.py)
   - Simple interface for personal loan calculations
   - Compare different loan scenarios
   - Understand monthly payments and total interest
   - Perfect for individuals planning personal loans

#### 🤖 AI-Powered Tools

1. **Onboarding Agent** (pages/00_OnboardingAgent.py)
   - Interactive AI assistant to help navigate the application
   - Get personalized recommendations
   - Learn about different financial instruments
   - Ask questions about calculations and methodologies

### Getting Started

1. Use the sidebar to navigate between different calculators
2. Start with the Onboarding Agent if you're new to financial calculations
3. Each calculator includes detailed instructions and helpful tooltips

""")

# Add a "Quick Start" section with buttons
st.header("Quick Start")

col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Launch MBS Calculator"):
        st.switch_page("pages/10_Loan_Calculator_MBS.py")
    
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
