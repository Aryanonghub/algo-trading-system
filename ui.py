"""
ui.py

Streamlit dashboard for the Algo-Trading System.

This app allows users to:
- Select stocks
- Choose a date range
- Backtest SMA crossover strategy
- Train ML model on historical data
- Visualize price + indicators
- View BUY/SELL signals on chart
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Import project modules
from strategy import add_indicators, generate_signals
from ml_model import train_ml_model, create_features


# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

# Configure Streamlit page settings
st.set_page_config(
    page_title="Algo-Trading System Dashboard",
    page_icon="📈",
    layout="wide"
)

# Main Title
st.title("📈 Algorithmic Trading Strategy Dashboard")

# Short description below title
st.markdown(
    "An interactive dashboard to backtest a trading strategy based on Moving Average Crossover."
)


# ---------------------------------------------------
# SIDEBAR CONFIGURATION PANEL
# ---------------------------------------------------

with st.sidebar:

    st.header("⚙️ Configuration")

    # Dictionary mapping company names to Yahoo Finance tickers
    nifty50_tickers = {
        "Reliance Industries": "RELIANCE.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Infosys": "INFY.NS",
        "Maruti Suzuki": "MARUTI.NS",
        "Tata Consultancy Services": "TCS.NS",
        "ICICI Bank": "ICICIBANK.NS"
    }

    # Multi-select for choosing stocks
    selected_stocks_names = st.multiselect(
        "Select NIFTY 50 Stocks to Analyze",
        options=list(nifty50_tickers.keys()),
        default=["Reliance Industries"]
    )

    # Default backtest period: Last 365 days (1 year)
    end_date = datetime.now()
    start_date_default = end_date - timedelta(days=365)

    # Date range selector
    date_range = st.date_input(
        "Select Date Range for Backtest",
        value=(start_date_default, end_date),
        min_value=datetime(2015, 1, 1),
        max_value=end_date
    )

    start_date, end_date = date_range

    # Run button triggers full analysis
    run_button = st.button("🚀 Run Analysis", use_container_width=True)


# ---------------------------------------------------
# MAIN ANALYSIS SECTION
# ---------------------------------------------------

# Only run analysis if user clicks button AND selects at least one stock
if run_button and selected_stocks_names:

    # Convert selected company names to ticker symbols
    selected_tickers = [
        nifty50_tickers[name]
        for name in selected_stocks_names
    ]

    # Containers for storing results
    all_signals = []
    all_data_for_ml = []
    processed_data_for_charts = {}

    # Loading spinner while processing
    with st.spinner(
        "Running analysis... Fetching data, backtesting strategy, and training ML model..."
    ):

        # Process each selected ticker individually
        for ticker in selected_tickers:

            # ---------------------------------------------------
            # DATA DOWNLOAD
            # ---------------------------------------------------

            # Download historical price data from Yahoo Finance
            df = yf.download(ticker, start=start_date, end=end_date)

            if df.empty:
                st.warning(
                    f"No data available for {ticker} in the selected range. Skipping."
                )
                continue

            # Flatten MultiIndex columns if returned by yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.dropna(inplace=True)

            # Add ticker column (used by ML + signals)
            df["Ticker"] = ticker

            # ---------------------------------------------------
            # INDICATOR CALCULATION
            # ---------------------------------------------------

            df_with_indicators = add_indicators(df)

            # Save copy for chart plotting
            processed_data_for_charts[ticker] = df_with_indicators.copy()

            # ---------------------------------------------------
            # FEATURE ENGINEERING FOR ML
            # ---------------------------------------------------

            df_with_ml_features = create_features(df_with_indicators)
            all_data_for_ml.append(df_with_ml_features)

            # ---------------------------------------------------
            # GENERATE BUY / SELL SIGNALS
            # ---------------------------------------------------

            signals = generate_signals(df_with_indicators)

            if not signals.empty:
                all_signals.append(signals)

    # Analysis finished
    st.success("Analysis Complete!")


    # ---------------------------------------------------
    # MACHINE LEARNING RESULTS SECTION
    # ---------------------------------------------------

    st.header("🧠 Machine Learning Model Results")

    if all_data_for_ml:

        # Combine all stock data into single dataframe
        full_ml_data = pd.concat(all_data_for_ml)

        if not full_ml_data.empty:

            # Train model & compute accuracy
            accuracy = train_ml_model(full_ml_data)

            st.metric(
                label="ML Model Prediction Accuracy",
                value=f"{accuracy:.2f}%",
                help="Accuracy of RandomForest predicting next-day movement."
            )
        else:
            st.warning("Not enough data to train ML model.")


    # ---------------------------------------------------
    # SIGNALS DISPLAY SECTION
    # ---------------------------------------------------

    st.header("📜 Backtest & Trade Signals")

    if all_signals:

        final_signals_df = pd.concat(all_signals, ignore_index=True)

        st.info(
            f"Found a total of **{len(final_signals_df)}** trade signals."
        )

        # Display signal table
        st.dataframe(final_signals_df)

    else:
        st.info("No trade signals generated for selected range.")


    # ---------------------------------------------------
    # PRICE + INDICATOR CHART SECTION
    # ---------------------------------------------------

    st.header("📊 Stock Price Charts with Indicators")

    for ticker in selected_tickers:

        if ticker in processed_data_for_charts:

            df_chart = processed_data_for_charts[ticker]

            fig = go.Figure()

            # ---------------------------
            # Close Price Line
            # ---------------------------
            fig.add_trace(go.Scatter(
                x=df_chart.index,
                y=df_chart['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='blue')
            ))

            # ---------------------------
            # 20-Day Moving Average
            # ---------------------------
            fig.add_trace(go.Scatter(
                x=df_chart.index,
                y=df_chart['SMA20'],
                mode='lines',
                name='20-Day SMA',
                line=dict(color='orange', dash='dot')
            ))

            # ---------------------------
            # 50-Day Moving Average
            # ---------------------------
            fig.add_trace(go.Scatter(
                x=df_chart.index,
                y=df_chart['SMA50'],
                mode='lines',
                name='50-Day SMA',
                line=dict(color='green', dash='dash')
            ))

            # ---------------------------
            # BUY / SELL MARKERS
            # ---------------------------

            if all_signals:

                stock_signals = final_signals_df[
                    final_signals_df['Ticker'] == ticker
                ]

                buy_signals = stock_signals[
                    stock_signals['Signal'] == "BUY"
                ]

                sell_signals = stock_signals[
                    stock_signals['Signal'] == "SELL"
                ]

                # Plot BUY markers
                if not buy_signals.empty:
                    fig.add_trace(go.Scatter(
                        x=buy_signals['Date'],
                        y=buy_signals['Price'],
                        mode='markers',
                        name='BUY',
                        marker=dict(
                            color='green',
                            size=12,
                            symbol='triangle-up'
                        )
                    ))

                # Plot SELL markers
                if not sell_signals.empty:
                    fig.add_trace(go.Scatter(
                        x=sell_signals['Date'],
                        y=sell_signals['Price'],
                        mode='markers',
                        name='SELL',
                        marker=dict(
                            color='red',
                            size=12,
                            symbol='triangle-down'
                        )
                    ))

            # Layout formatting
            fig.update_layout(
                title=f'Price and Moving Averages for {ticker}',
                xaxis_title='Date',
                yaxis_title='Price (INR)',
                legend_title='Indicator',
                template='plotly_white'
            )

            # Render chart
            st.plotly_chart(fig, use_container_width=True)


# If button pressed but no stocks selected
elif run_button:
    st.warning("Please select at least one stock to analyze.")
