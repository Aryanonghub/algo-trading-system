import pandas as pd
import pandas_ta as ta


def add_indicators(df):
    """
    Calculates and adds technical indicators (RSI, SMA20, SMA50) to the DataFrame.
    """
    # Calculate RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)

    # Calculate 20-day and 50-day SMAs
    df['SMA20'] = ta.sma(df['Close'], length=20)
    df['SMA50'] = ta.sma(df['Close'], length=50)

    df.dropna(inplace=True)  # Remove rows with NaN values after calculation
    return df


def generate_signals(df):
    """
    Implements the trading strategy to generate buy signals.
    - Buy Signal: RSI < 30
    - Confirmation: 20-DMA crosses above 50-DMA
    """
    signals = []

    # Use iloc to iterate safely, starting from the second row for previous day comparison
    for i in range(1, len(df)):
        current_row = df.iloc[i]
        prev_row = df.iloc[i-1]

        # Buy condition 1: 20-SMA crosses above 50-SMA
        crossover_condition = (prev_row['SMA20'] < prev_row['SMA50']) and \
                              (current_row['SMA20'] > current_row['SMA50'])

        if crossover_condition:
            trade_info = {
                'Date': current_row.name,  # .name holds the index (Date)
                'Ticker': current_row['Ticker'],
                'Signal': 'BUY',
                'Price': current_row['Close']
            }
            signals.append(trade_info)

    return pd.DataFrame(signals)
