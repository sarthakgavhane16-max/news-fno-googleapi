# fno_news_app.py
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import time
import traceback

# Defensive import for GoogleNews
try:
    from GoogleNews import GoogleNews
except Exception as e:
    st.error(
        "GoogleNews package is not installed or failed to import. "
        "Run `pip install GoogleNews` in your environment and restart Streamlit."
    )
    st.stop()

# ---- CONFIG: update this list as you like ----
FNO_STOCKS = [
    "Reliance Industries", "HDFC Bank", "ICICI Bank", "Infosys", "TCS",
    "Axis Bank", "State Bank of India", "Bharti Airtel", "HCL Tech",
    "ITC", "Kotak Mahindra Bank", "Larsen & Toubro", "Maruti Suzuki",
    "Bajaj Finance", "Adani Enterprises", "NTPC", "Power Grid", "Hindustan Unilever",
    "Tata Motors", "Tata Steel", "UltraTech Cement", "JSW Steel", "Tech Mahindra",
    "Sun Pharma", "Wipro", "Asian Paints", "SBI Life Insurance"
]

st.set_page_config(page_title="F&O Stocks — Google News", layout="wide")
st.title("📡 Google News for F&O Stocks (robust Streamlit version)")

# Timeframe selector
timeframe = st.selectbox("Select time period:", ["1 Week", "1 Month", "3 Months", "6 Months"])

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

st.markdown(f"**Searching Google News** from **{start_str}** to **{end_str}** for {len(FNO_STOCKS)} stocks.")

# controls
col1, col2 = st.columns([1, 3])
with col1:
    fetch_btn = st.button("🔁 Fetch News")
    per_stock_delay = st.number_input(
        "Delay between stock queries (seconds, to avoid rate limits)",
        min_value=0.0, max_value=10.0, value=0.8, step=0.1
    )
with col2:
    st.caption("Tip: increase delay if you see network / rate limit errors.")

# caching: avoid refetch on small UI interactions
@st.cache_data(ttl=3600)
def fetch_news_for_stocks(stocks, start_str, end_str, delay):
    googlenews = GoogleNews(lang='en')
    # Some GoogleNews versions require set_time_range before search; set it every time to be safe
    news_rows = []
    errors = []
    for i, stock in enumerate(stocks, 1):
        try:
            # Compose query (make it specific enough)
            query = f"{stock} stock India"
            # Some versions of GoogleNews expect mm/dd/yyyy strings
            try:
                googlenews.set_time_range(start_str, end_str)
            except TypeError:
                # fallback if signature differs
                try:
                    googlenews.set_time_range(start_str, end_str, when=None)
                except Exception:
                    pass
            googlenews.search(query)
            results = googlenews.result() or []
            # If result returns strings or dicts, handle both:
            for item in results:
                if isinstance(item, dict):
                    title = item.get("title")
                    date = item.get("date")
                    media = item.get("media")
                    link = item.get("link")
                else:
                    # fallback: place raw value
                    title = str(item)
                    date = None
                    media = None
                    link = None
                news_rows.append({
                    "Stock": stock,
                    "Query": query,
                    "Title": title,
                    "Date": date,
                    "Media": media,
                    "Link": link
                })
            # clear to avoid stale results between queries
            try:
                googlenews.clear()
            except Exception:
                pass
            time.sleep(delay)
        except Exception as e:
            errors.append({"stock": stock, "error": repr(e), "trace": traceback.format_exc()})
    return news_rows, errors

if fetch_btn:
    with st.spinner("Fetching... this may take a while for many stocks"):
        news_rows, errors = fetch_news_for_stocks(FNO_STOCKS, start_str, end_str, per_stock_delay)

    if news_rows:
        df = pd.DataFrame(news_rows)
        # try normalizing date column when possible
        def parse_maybe_date(x):
            try:
                return pd.to_datetime(x, errors='coerce')
            except Exception:
                return pd.NaT
        df["ParsedDate"] = df["Date"].apply(parse_maybe_date)
        st.success(f"Found {len(df)} news items (rows).")
        st.dataframe(df[["Stock", "Title", "Date", "ParsedDate", "Media", "Link"]], use_container_width=True)

        # download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, file_name=f"fno_news_{timeframe.replace(' ', '_')}.csv", mime="text/csv")
    else:
        st.warning("No news items found for the selected period.")

    if errors:
        st.error(f"Errors occurred for {len(errors)} stocks. Expand to view details.")
        for e in errors:
            with st.expander(f"Error — {e['stock']}"):
                st.write("Exception:")
                st.code(e["error"])
                st.write("Traceback:")
                st.text(e["trace"])
else:
    st.info("Click **Fetch News** to start querying Google News for the F&O stock list.")
