import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 12 / 100
    num_payments = years * 12
    return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

st.title("Asset-Backed Securities Loan Calculator")

# Asset class selection
asset_class = st.sidebar.selectbox(
    "Asset Class",
    ["Personal Loan", "Auto Loan", "Invoice Finance"],
    index=0
)

# Dynamic parameters based on asset class
st.sidebar.header("Loan Parameters")

# Set default values and limits based on asset class
if asset_class == "Personal Loan":
    default_amount = 25000.0
    max_amount = 100000.0
    default_rate = 7.5
    max_term = 7
    default_term = 5
elif asset_class == "Auto Loan":
    default_amount = 35000.0
    max_amount = 150000.0
    default_rate = 5.5
    max_term = 7
    default_term = 5
else:  # Invoice Finance
    default_amount = 50000.0
    max_amount = 500000.0
    default_rate = 4.5
    max_term = 1
    default_term = 1

loan_amount = st.sidebar.number_input(
    "Loan Amount (€)", 
    min_value=1000.0, 
    max_value=max_amount, 
    value=default_amount,
    step=1000.0,
    key="loan_amount"
)

interest_rate = st.sidebar.number_input(
    "Annual Interest Rate (%)",
    min_value=0.1,
    max_value=30.0,
    value=default_rate,
    step=0.1,
    key="interest_rate"
)

loan_term = st.sidebar.number_input(
    "Loan Term (years)",
    min_value=1,
    max_value=max_term,
    value=default_term,
    step=1,
    key="loan_term"
)

# Asset-specific additional parameters
if asset_class == "Auto Loan":
    vehicle_type = st.sidebar.selectbox(
        "Vehicle Type",
        ["New", "Used"],
        index=0
    )
    if vehicle_type == "Used":
        vehicle_age = st.sidebar.slider(
            "Vehicle Age (years)",
            min_value=0,
            max_value=10,
            value=3
        )
elif asset_class == "Invoice Finance":
    payment_terms = st.sidebar.selectbox(
        "Payment Terms",
        ["30 days", "60 days", "90 days"],
        index=0
    )
    advance_rate = st.sidebar.slider(
        "Advance Rate (%)",
        min_value=70,
        max_value=95,
        value=80
    )

# Add recalculate button
if st.sidebar.button("Recalculate"):
    st.rerun()

# Calculate monthly payment
monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, loan_term)

# Display results
st.header("Loan Summary")
col1, col2 = st.columns(2)

with col1:
    st.metric("Monthly Payment", f"€{monthly_payment:,.2f}")
    st.metric("Annual Payment", f"€{monthly_payment * 12:,.2f}")

with col2:
    st.metric("Total Interest", f"€{(monthly_payment * 12 * loan_term - loan_amount):,.2f}")
    st.metric("Total Payment", f"€{monthly_payment * 12 * loan_term:,.2f}")

# Additional information
st.header("Amortization Schedule")
years = list(range(1, loan_term + 1))
remaining_balance = []
interest_paid = []
principal_paid = []

balance = loan_amount
for year in years:
    yearly_payment = monthly_payment * 12
    yearly_interest = balance * (interest_rate / 100)
    yearly_principal = yearly_payment - yearly_interest
    balance = max(0, balance - yearly_principal)
    
    remaining_balance.append(balance)
    interest_paid.append(yearly_interest)
    principal_paid.append(yearly_principal)

# Create payment visualization
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add area traces for principal and interest
fig.add_trace(
    go.Scatter(
        x=years,
        y=principal_paid,
        name="Principal",
        fill='tonexty',
        mode='lines',
        line=dict(width=0.5, color='rgb(73, 163, 156)'),
        stackgroup='one'
    )
)

fig.add_trace(
    go.Scatter(
        x=years,
        y=interest_paid,
        name="Interest",
        fill='tonexty',
        mode='lines',
        line=dict(width=0.5, color='rgb(255, 144, 144)'),
        stackgroup='one'
    )
)

# Add remaining balance line
fig.add_trace(
    go.Scatter(
        x=years,
        y=remaining_balance,
        name="Remaining Balance",
        mode='lines',
        line=dict(color='rgb(50, 50, 50)', width=2, dash='dot'),
    ),
    secondary_y=True,
)

# Update layout
fig.update_layout(
    title="Payment Breakdown by Year",
    xaxis_title="Year",
    yaxis_title="Annual Payment (€)",
    yaxis2_title="Remaining Balance (€)",
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

# Display the plot
st.plotly_chart(fig, use_container_width=True)

# Create a table with payment schedule
schedule_data = {
    "Year": years,
    "Remaining Balance": [f"€{b:,.2f}" for b in remaining_balance],
    "Interest Paid": [f"€{i:,.2f}" for i in interest_paid],
    "Principal Paid": [f"€{p:,.2f}" for p in principal_paid]
}

st.dataframe(schedule_data)

# Update disclaimer based on asset class
if asset_class == "Personal Loan":
    disclaimer = """
    This calculator provides estimates for personal loans. 
    Actual loan terms and rates may vary based on factors such as credit score, 
    income, debt-to-income ratio, and lender requirements.
    """
elif asset_class == "Auto Loan":
    disclaimer = """
    This calculator provides estimates for auto loans. 
    Final terms depend on factors including credit score, vehicle age, 
    down payment, and lender requirements. Additional costs like insurance
    are not included in these calculations.
    """
else:
    disclaimer = """
    This calculator provides estimates for invoice finance facilities. 
    Actual terms depend on factors such as customer creditworthiness,
    invoice quality, and business track record. Additional fees may apply.
    """

st.caption(disclaimer)
