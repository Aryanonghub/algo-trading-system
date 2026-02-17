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

st.set_page_config(
    page_title="Algo-Trading System Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Algorithmic Trading Strategy Dashboard")
st.markdown(
    "An interactive dashboard to backtest a trading strategy based on Moving Average Crossover."
)


# ---------------------------------------------------
# SIDEBAR CONFIGURATION
# ---------------------------------------------------

with st.sidebar:

    st.header("⚙️ Configuration")

    nifty50_tickers = {
        "Reliance Industries": "RELIANCE.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Infosys": "INFY.NS",
        "Maruti Suzuki": "MARUTI.NS",
        "Tata Consultancy Services": "TCS.NS",
        "ICICI Bank": "ICICIBANK.NS"
    }

    selected_stocks_names = st.multiselect(
        "Select NIFTY 50 Stocks to Analyze",
        options=list(nifty50_tickers.keys()),
        default=["Reliance Industries"]
    )

    # Default to 1 Year
    end_date = datetime.now()
    start_date_default = end_date - timedelta(days=365)

    date_range = st.date_input(
        "Select Date Range for Backtest",
        value=(start_date_default, end_date),
        min_value=datetime(2015, 1, 1),
        max_value=end_date
    )

    start_date, end_date = date_range
    # ---------------------------------------------------
# DATA EXPLANATION NOTE (For Transparency)
# ---------------------------------------------------

    st.caption(
    f"""
ℹ️ **How data is handled:**

• You selected data from **{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}**

• To correctly compute moving averages (SMA20 & SMA50),
  the system internally fetches ~60 extra days of historical data.

• Only the selected date range is shown in charts and signals.
"""
)


    run_button = st.button("🚀 Run Analysis", use_container_width=True)


# ---------------------------------------------------
# MAIN ANALYSIS
# ---------------------------------------------------

if run_button and selected_stocks_names:

    selected_tickers = [
        nifty50_tickers[name]
        for name in selected_stocks_names
    ]

    all_signals = []
    all_data_for_ml = []
    processed_data_for_charts = {}

    with st.spinner(
        "Running analysis... Fetching data, backtesting strategy, and training ML model..."
    ):

        for ticker in selected_tickers:

            # ---------------------------------------------------
            # DATA DOWNLOAD WITH WARM-UP BUFFER
            # ---------------------------------------------------

            BUFFER_DAYS = 60
            buffer_start_date = start_date - timedelta(days=BUFFER_DAYS)

            df = yf.download(
                ticker,
                start=buffer_start_date,
                end=end_date
            )

            if df.empty:
                st.warning(
                    f"No data available for {ticker} in the selected range. Skipping."
                )
                continue

            # Fix MultiIndex columns if needed
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.dropna(inplace=True)
            df["Ticker"] = ticker

            # ---------------------------------------------------
            # INDICATOR CALCULATION
            # ---------------------------------------------------

            df_with_indicators = add_indicators(df)

            # ---------------------------------------------------
            # TRIM TO USER-SELECTED DATE RANGE
            # ---------------------------------------------------

            df_with_indicators = df_with_indicators[
                (df_with_indicators.index >= pd.to_datetime(start_date)) &
                (df_with_indicators.index <= pd.to_datetime(end_date))
            ]

            processed_data_for_charts[ticker] = df_with_indicators.copy()

            # ---------------------------------------------------
            # ML FEATURE ENGINEERING
            # ---------------------------------------------------

            df_with_ml_features = create_features(df_with_indicators)
            all_data_for_ml.append(df_with_ml_features)

            # ---------------------------------------------------
            # GENERATE SIGNALS
            # ---------------------------------------------------

            signals = generate_signals(df_with_indicators)

            if not signals.empty:
                all_signals.append(signals)

    st.success("Analysis Complete!")


    # ---------------------------------------------------
    # MACHINE LEARNING SECTION
    # ---------------------------------------------------

    st.header("🧠 Machine Learning Model Results")

    if all_data_for_ml:
        full_ml_data = pd.concat(all_data_for_ml)

        if not full_ml_data.empty:
            accuracy = train_ml_model(full_ml_data)

            st.metric(
                label="ML Model Prediction Accuracy",
                value=f"{accuracy:.2f}%",
                help="Accuracy of RandomForest predicting next-day movement."
            )
        else:
            st.warning("Not enough data to train ML model.")


    # ---------------------------------------------------
    # SIGNALS SECTION
    # ---------------------------------------------------

    st.header("📜 Backtest & Trade Signals")

    if all_signals:
        final_signals_df = pd.concat(all_signals, ignore_index=True)

        st.info(
            f"Found a total of **{len(final_signals_df)}** trade signals."
        )

        st.dataframe(final_signals_df)
    else:
        st.info("No trade signals generated for selected range.")


    # ---------------------------------------------------
    # CHART SECTION
    # ---------------------------------------------------

    st.header("📊 Stock Price Charts with Indicators")

    for ticker in selected_tickers:

        if ticker in processed_data_for_charts:

            df_chart = processed_data_for_charts[ticker]

            fig = go.Figure()

            # Close Price
            fig.add_trace(go.Scatter(
                x=df_chart.index,
                y=df_chart['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='blue')
            ))

            # SMA20
            fig.add_trace(go.Scatter(
                x=df_chart.index,
                y=df_chart['SMA20'],
                mode='lines',
                name='20-Day SMA',
                line=dict(color='orange', dash='dot')
            ))

            # SMA50
            fig.add_trace(go.Scatter(
                x=df_chart.index,
                y=df_chart['SMA50'],
                mode='lines',
                name='50-Day SMA',
                line=dict(color='green', dash='dash')
            ))

            # Plot BUY / SELL markers
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

            fig.update_layout(
                title=f'Price and Moving Averages for {ticker}',
                xaxis_title='Date',
                yaxis_title='Price (INR)',
                legend_title='Indicator',
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

elif run_button:
    st.warning("Please select at least one stock to analyze.")
