import streamlit as st
from GoogleNews import GoogleNews
import pandas as pd
from datetime import datetime, timedelta

# --- Helper: Load list of F&O Stocks (you can update this list)
FNO_STOCKS = [
    "Reliance Industries", "HDFC Bank", "ICICI Bank", "Infosys", "TCS", 
    "Axis Bank", "State Bank of India", "Bharti Airtel", "HCL Tech", 
    "ITC", "Kotak Mahindra Bank", "Larsen & Toubro", "Maruti Suzuki",
    "Bajaj Finance", "Adani Enterprises", "NTPC", "Power Grid", "Hindustan Unilever",
    "Tata Motors", "Tata Steel", "UltraTech Cement", "JSW Steel", "Tech Mahindra",
    "Sun Pharma", "Wipro", "Asian Paints", "SBI Life Insurance"
]

# --- App Title
st.title("📈 Google News for All F&O Stocks")

# --- Select timeframe
timeframe = st.selectbox(
    "Select Time Period:",
    ["1 Week", "1 Month", "3 Months", "6 Months"]
)

# --- Calculate dates
today = datetime.today()
if timeframe == "1 Week":
    start_date = today - timedelta(weeks=1)
elif timeframe == "1 Month":
    start_date = today - timedelta(days=30)
elif timeframe == "3 Months":
    start_date = today - timedelta(days=90)
else:
    start_date = today - timedelta(days=180)

start_str = start_date.strftime("%m/%d/%Y")
end_str = today.strftime("%m/%d/%Y")

# --- Button to Fetch News
if st.button("Fetch News for All F&O Stocks"):
    st.info(f"Fetching news from Google between {start_str} and {end_str}... ⏳")
    news_list = []

    googlenews = GoogleNews(lang='en')
    googlenews.set_time_range(start_str, end_str)

    # --- Fetch news for each F&O stock
    for stock in FNO_STOCKS:
        googlenews.search(stock + " stock India")
        results = googlenews.result()
        for item in results:
            news_list.append({
                "Stock": stock,
                "Title": item.get("title"),
                "Date": item.get("date"),
                "Media": item.get("media"),
                "Link": item.get("link")
            })
        googlenews.clear()

    # --- Display results
    if len(news_list) > 0:
        df = pd.DataFrame(news_list)
        st.success(f"Found {len(df)} news articles ✅")
        st.dataframe(df)
    else:
        st.warning("No news articles found for the selected period.")

    # --- Option to download results
    if news_list:
        csv = pd.DataFrame(news_list).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"fno_news_{timeframe.replace(' ', '_').lower()}.csv",
            mime="text/csv"
        )

# --- Footer
st.caption("Powered by Google News (unofficial API) | Built with ❤️ in Streamlit")
