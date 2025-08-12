import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Import project modules
from utils import setup_logging
from strategy import add_indicators, generate_signals
from ml_model import train_ml_model, create_features

# --- Page Configuration ---
st.set_page_config(
    page_title="Algo-Trading System Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Main Title ---
st.title("📈 Algorithmic Trading Strategy Dashboard")
st.markdown("An interactive dashboard to backtest a trading strategy based on Moving Average Crossover.")

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Stock Selection
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
        default=["Reliance Industries", "HDFC Bank", "Infosys"]
    )
    
    # Date Range Selection
    end_date = datetime.now()
    start_date_default = end_date - timedelta(days=730) # Default to 2 years
    date_range = st.date_input(
        "Select Date Range for Backtest",
        value=(start_date_default, end_date),
        min_value=datetime(2015, 1, 1),
        max_value=end_date
    )
    start_date, end_date = date_range

    # Run Button
    run_button = st.button("🚀 Run Analysis", use_container_width=True)

# --- Main Content Area ---
if run_button and selected_stocks_names:
    selected_tickers = [nifty50_tickers[name] for name in selected_stocks_names]
    
    with st.spinner("Running analysis... Fetching data, backtesting strategy, and training ML model..."):
        # --- 1. Data Ingestion ---
        try:
            data = yf.download(selected_tickers, start=start_date, end=end_date, group_by='ticker')
            if data.empty:
                st.error("Could not download stock data for the selected range. Please try a different date range.")
                st.stop()
        except Exception as e:
            st.error(f"An error occurred during data download: {e}")
            st.stop()

        all_signals = []
        all_data_for_ml = []
        processed_data_for_charts = {}

        # --- 2. Strategy & Feature Calculation (Per Ticker) ---
        for ticker in selected_tickers:
            if ticker not in data.columns.levels[0] or data[ticker].dropna().empty:
                st.warning(f"No data available for {ticker} in the selected range. Skipping.")
                continue

            df = data[ticker].copy()
            df.dropna(inplace=True)
            df['Ticker'] = ticker
            
            df_with_indicators = add_indicators(df)
            processed_data_for_charts[ticker] = df_with_indicators.copy() # Save for charting
            
            df_with_ml_features = create_features(df_with_indicators)
            all_data_for_ml.append(df_with_ml_features)
            
            # Using the original, strict strategy
            signals = generate_signals(df_with_indicators)
            if not signals.empty:
                all_signals.append(signals)

        # --- 3. Display Results ---
        st.success("Analysis Complete!")

        # --- ML Model Results ---
        st.header("🧠 Machine Learning Model Results")
        if all_data_for_ml:
            full_ml_data = pd.concat(all_data_for_ml)
            if not full_ml_data.empty:
                accuracy = train_ml_model(full_ml_data)
                st.metric(label="ML Model Prediction Accuracy", value=f"{accuracy:.2f}%",
                          help="Accuracy of a RandomForest model predicting if the next day's price will go up or down.")
            else:
                st.warning("Not enough data to train the ML model.")
        
        # --- Backtest Results ---
        st.header("📜 Backtest & Trade Signals")
        if all_signals:
            final_signals_df = pd.concat(all_signals, ignore_index=True)
            st.info(f"Found a total of **{len(final_signals_df)}** trade signals based on the strategy.")
            st.dataframe(final_signals_df)
        else:
            st.info("No trade signals were generated for the selected stocks and date range with the current strategy.")

        # --- Stock Charts ---
        st.header("📊 Stock Price Charts with Indicators")
        for ticker in selected_tickers:
            if ticker in processed_data_for_charts:
                df_chart = processed_data_for_charts[ticker]
                
                fig = go.Figure()
                # Add Price Line
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
                # Add Moving Averages
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['SMA20'], mode='lines', name='20-Day SMA', line=dict(color='orange', dash='dot')))
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['SMA50'], mode='lines', name='50-Day SMA', line=dict(color='green', dash='dash')))
                
                # Add Buy Signals from this stock to the chart
                stock_signals = final_signals_df[final_signals_df['Ticker'] == ticker] if all_signals else pd.DataFrame()
                if not stock_signals.empty:
                    fig.add_trace(go.Scatter(x=stock_signals['Date'], y=stock_signals['Price'], mode='markers', name='Buy Signal',
                                             marker=dict(color='red', size=12, symbol='triangle-up')))

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