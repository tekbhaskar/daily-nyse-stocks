import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="NYSE Gainers & Losers", layout="wide")

st.title("📊 NYSE - Top Gainers & Losers")

# Manual refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()

@st.cache_data
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url)[0]
    return df[['Symbol', 'Security']]

def fetch_price_changes(tickers):
    data = yf.download(tickers, period="3d", interval="1d", group_by='ticker', progress=False)
    changes = []
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    for ticker in tickers:
        try:
            df = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data
            df = df.dropna(subset=['Close'])
            dates = df.index.date

            if today in dates and yesterday in dates:
                today_close = df.loc[df.index.date == today, 'Close'].values[0]
                yesterday_close = df.loc[df.index.date == yesterday, 'Close'].values[0]
                pct_change = ((today_close - yesterday_close) / yesterday_close) * 100

                changes.append({
                    'Ticker': ticker,
                    'Company': df_sp500.loc[df_sp500['Symbol'] == ticker, 'Security'].values[0],
                    'Yesterday Close': round(yesterday_close, 2),
                    'Today Close': round(today_close, 2),
                    '% Change': round(pct_change, 2)
                })
        except Exception:
            continue

    return pd.DataFrame(changes)

def color_change(val):
    if val < 0:
        return 'color: red'
    elif val > 0:
        return 'color: green'
    return 'color: black'

# Load tickers
df_sp500 = get_sp500_tickers()
tickers = df_sp500['Symbol'].tolist()

# Tabbed interface
tab1, tab2 = st.tabs(["📈 Top Gainers", "📉 Top Losers"])
top_n = st.slider("Number of stocks to display", min_value=5, max_value=50, value=10)

with st.spinner("Fetching data..."):
    changes_df = fetch_price_changes(tickers)

with tab1:
    gainers = changes_df[changes_df['% Change'] > 0].sort_values(by='% Change', ascending=False).head(top_n)
    st.subheader(f"📈 Top {top_n} Gainers in S&P 500 Today vs Yesterday")
    styled = gainers.style.applymap(color_change, subset=['% Change'])
    st.dataframe(styled, use_container_width=True)

with tab2:
    losers = changes_df[changes_df['% Change'] < 0].sort_values(by='% Change').head(top_n)
    st.subheader(f"📉 Top {top_n} Losers in S&P 500 Today vs Yesterday")
    styled = losers.style.applymap(color_change, subset=['% Change'])
    st.dataframe(styled, use_container_width=True)


  #auto-refresh every 60 seconds
countdown = st.empty()
for i in range(60, 0, -1):
    countdown.markdown(f"⏳ Auto-refreshing in `{i}` seconds... or click 🔄 above")
    time.sleep(1)
st.rerun()  