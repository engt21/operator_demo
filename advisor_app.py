import streamlit as st

# Initialize session state for authentication and client data
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'advisor_username' not in st.session_state:
        st.session_state.advisor_username = ''

    if 'clients' not in st.session_state:
        # Sample clients: Each client has a name, an investment account with balance, and shares
        st.session_state.clients = {
            'Client A': {
                'Investment': 500.0,
                'Shares': {
                    'Microsoft': 0,
                    'Nvidia': 0,
                    'Morgan Stanley': 0
                }
            },
            'Client B': {
                'Investment': 8000.0,
                'Shares': {
                    'Microsoft': 10,
                    'Nvidia': 5,
                    'Morgan Stanley': 15
                }
            },
            'Client C': {
                'Investment': 12000.0,
                'Shares': {
                    'Microsoft': 8,
                    'Nvidia': 3,
                    'Morgan Stanley': 20
                }
            }
        }

    if 'tickers' not in st.session_state:
        # Mock ticker prices for equities
        st.session_state.tickers = {
            'Microsoft': 350.00,
            'Nvidia': 280.00,
            'Morgan Stanley': 100.00
        }

    if 'page' not in st.session_state:
        st.session_state.page = "Clients Overview"

    if 'investment_message' not in st.session_state:
        st.session_state.investment_message = None

# Function to handle login
def login(username, password):
    # For simplicity, credentials are hardcoded
    advisor_credentials = {
        'johnsmith': 'securepassword123'
    }

    if username.lower() in advisor_credentials and password == advisor_credentials[username.lower()]:
        st.session_state.logged_in = True
        st.session_state.advisor_username = username.lower()
        st.session_state.page = "Clients Overview"
        st.success("Logged in successfully!")
        st.rerun()  # Redirect immediately after login
    else:
        st.error("Invalid username or password")

# Function to handle logout
def logout():
    st.session_state.logged_in = False
    st.session_state.advisor_username = ''
    st.session_state.page = "Login"
    st.success("Logged out successfully!")
    st.rerun()

# Login Page
def login_page():
    st.title("Financial Advisor Login")
    st.write("Please enter your credentials to access the system.")

    # Use Streamlit forms for better handling of inputs and submission
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        submit_button = st.form_submit_button(label='Login')

    if submit_button:
        login(username, password)

# Clients Overview Page
def clients_overview():
    st.title("Clients Overview")
    st.write("Manage your clients' investments seamlessly.")

    st.markdown("### Current Ticker Prices")
    ticker_data = {
        'Equity': list(st.session_state.tickers.keys()),
        'Current Price ($)': [f"${price:,.2f}" for price in st.session_state.tickers.values()]
    }
    st.table(ticker_data)

    st.markdown("---")

    # Display all clients and their accounts
    for client, data in st.session_state.clients.items():
        st.subheader(f"{client}")

        # Display Investment Account Balance
        st.write(f"**Investment Account Balance:** ${data['Investment']:,.2f}")

        # Display Shares Owned
        shares = data.get('Shares', {})
        shares_data = {
            'Equity': [],
            'Shares Owned': [],
            'Current Price ($)': [],
            'Total Value ($)': []
        }
        total_investment = 0.0
        for equity, num_shares in shares.items():
            current_price = st.session_state.tickers.get(equity, 0)
            total_value = num_shares * current_price
            shares_data['Equity'].append(equity)
            shares_data['Shares Owned'].append(num_shares)
            shares_data['Current Price ($)'].append(f"${current_price:,.2f}")
            shares_data['Total Value ($)'].append(f"${total_value:,.2f}")
            total_investment += total_value

        st.markdown("**Portfolio:**")
        if any(shares.values()):
            st.table(shares_data)
            st.write(f"**Total Investment Value:** ${total_investment:,.2f}")
        else:
            st.write("No shares owned.")

        st.markdown("---")

# Investment Section
def investment_section():
    st.title("Manage Investments")

    clients = list(st.session_state.clients.keys())
    if not clients:
        st.warning("No clients available.")
        return

    selected_client = st.selectbox("Select Client", clients)
    client_data = st.session_state.clients[selected_client]

    # Transaction Type: Buy or Sell
    transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell"])

    # Select Equity
    equities = list(st.session_state.tickers.keys())
    selected_equity = st.selectbox("Select Equity", equities)

    # Current Price Display
    current_price = st.session_state.tickers[selected_equity]
    st.write(f"**Current Price of {selected_equity}: ${current_price:,.2f}**")

    # Number of Shares
    num_shares = st.number_input("Number of Shares", min_value=1, step=1, format="%d")

    # Execute Transaction
    if st.button("Execute"):
        total_cost = num_shares * current_price

        if transaction_type == "Buy":
            if client_data['Investment'] >= total_cost:
                # Perform Buy
                client_data['Investment'] -= total_cost
                client_data['Shares'][selected_equity] += num_shares
                st.session_state.investment_message = {
                    "type": "success",
                    "content": (
                        f"Successfully bought **{num_shares}** shares of **{selected_equity}** for **{selected_client}** "
                        f"at **${current_price:,.2f}** per share.\n\n"
                        f"**Updated Investment Balance:** ${client_data['Investment']:,.2f}\n"
                        f"**Shares Owned:** {client_data['Shares'][selected_equity]} shares of {selected_equity}."
                    )
                }
            else:
                st.session_state.investment_message = {
                    "type": "error",
                    "content": "Insufficient funds to complete the purchase."
                }
        elif transaction_type == "Sell":
            if client_data['Shares'][selected_equity] >= num_shares:
                # Perform Sell
                client_data['Shares'][selected_equity] -= num_shares
                client_data['Investment'] += total_cost
                st.session_state.investment_message = {
                    "type": "success",
                    "content": (
                        f"Successfully sold **{num_shares}** shares of **{selected_equity}** for **{selected_client}** "
                        f"at **${current_price:,.2f}** per share.\n\n"
                        f"**Updated Investment Balance:** ${client_data['Investment']:,.2f}\n"
                        f"**Shares Owned:** {client_data['Shares'][selected_equity]} shares of {selected_equity}."
                    )
                }
            else:
                st.session_state.investment_message = {
                    "type": "error",
                    "content": "Insufficient shares to complete the sale."
                }

    # Display Message if Exists
    if st.session_state.investment_message:
        msg = st.session_state.investment_message
        if msg["type"] == "success":
            st.success(msg["content"])
        elif msg["type"] == "error":
            st.error(msg["content"])
        # Clear the message after displaying
        st.session_state.investment_message = None

# Main Application
def main_app():
    st.header("Financial Advisor Dashboard")

    # Create navigation buttons on top
    cols = st.columns(3)
    with cols[0]:
        if st.button("Clients Overview"):
            st.session_state.page = "Clients Overview"
    with cols[1]:
        if st.button("Manage Investments"):
            st.session_state.page = "Manage Investments"
    with cols[2]:
        if st.button("Logout"):
            logout()

    st.markdown("---")

    # Display the selected page
    if st.session_state.page == "Clients Overview":
        clients_overview()
    elif st.session_state.page == "Manage Investments":
        investment_section()

# Initialize session state
init_session_state()

# App Layout
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
