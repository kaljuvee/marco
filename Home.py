import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 12 / 100
    num_payments = years * 12
    return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

st.title("Mortgage-Backed Securities Calculator")

# Input parameters
st.sidebar.header("MBS Parameters")

loan_amount = st.sidebar.number_input(
    "Total Loan Amount ($)", 
    min_value=100000.0, 
    max_value=10000000.0, 
    value=500000.0,
    step=50000.0,
    key="loan_amount"
)

wac = st.sidebar.number_input(
    "Weighted Average Coupon (WAC) %",
    min_value=0.1,
    max_value=15.0,
    value=6.0,
    step=0.1,
    key="wac"
)

wam = st.sidebar.number_input(
    "Weighted Average Maturity (WAM) in years",
    min_value=1,
    max_value=30,
    value=30,
    step=1,
    key="wam"
)

# Add recalculate button
if st.sidebar.button("Recalculate"):
    st.rerun()

# Calculate monthly payment
monthly_payment = calculate_monthly_payment(loan_amount, wac, wam)

# Display results
st.header("MBS Details")
col1, col2 = st.columns(2)

with col1:
    st.metric("Monthly Payment", f"${monthly_payment:,.2f}")
    st.metric("Annual Payment", f"${monthly_payment * 12:,.2f}")

with col2:
    st.metric("Total Interest", f"${(monthly_payment * 12 * wam - loan_amount):,.2f}")
    st.metric("Total Payment", f"${monthly_payment * 12 * wam:,.2f}")

# Additional information
st.header("Payment Schedule")
years = list(range(1, wam + 1))
remaining_balance = []
interest_paid = []
principal_paid = []

balance = loan_amount
for year in years:
    yearly_payment = monthly_payment * 12
    yearly_interest = balance * (wac / 100)
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
    yaxis_title="Annual Payment ($)",
    yaxis2_title="Remaining Balance ($)",
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
    "Remaining Balance": [f"${b:,.2f}" for b in remaining_balance],
    "Interest Paid": [f"${i:,.2f}" for i in interest_paid],
    "Principal Paid": [f"${p:,.2f}" for p in principal_paid]
}

st.dataframe(schedule_data)

# Add disclaimer
st.caption("""
This is a simplified MBS calculator for educational purposes. 
Actual MBS valuations involve additional factors such as prepayment risk, 
default risk, and market conditions.
""")
