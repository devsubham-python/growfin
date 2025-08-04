import os 
import sys
# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from api import (
    call_price_api,
    call_nse_api,
    api_info,
    api_news,
    api_events,
)

# Sample values
sample_ticker = "TCS"
sample_search_id = "tata-consultancy-services-ltd"
sample_groww_id = "GSTK532540"
sample_start = int(datetime(2024, 1, 1, 9, 0).timestamp() * 1000)
sample_end = int(datetime(2024, 1, 2, 15, 30).timestamp() * 1000)
sample_interval = 1440

print("\n" + "="*50 + "\n")

# --- call_price_api ---
result1 = call_price_api(ticker=sample_ticker, start=sample_start, end=sample_end, interval=sample_interval, debug=True)
print(result1)

print("\n" + "="*50 + "\n")

result2 = call_price_api(ticker=sample_ticker, start=sample_start, end=sample_end, interval=sample_interval)
print(result2)

print("\n" + "="*50 + "\n")
# --- call_nse_api ---
result3 = call_nse_api(ticker=sample_ticker, debug=True)
print(result3)
print("\n" + "="*50 + "\n")

result4 = call_nse_api(ticker=sample_ticker)
print(result4)
print("\n" + "="*50 + "\n")

# --- api_info ---
result5 = api_info(search_id=sample_search_id, debug=True)
print(result5)
print("\n" + "="*50 + "\n")

result6 = api_info(search_id=sample_search_id)
print(result6)
print("\n" + "="*50 + "\n")
# --- api_news ---
result7 = api_news(groww_company_id=sample_groww_id, page=0, size=5, debug=True)
print(result7)
print("\n" + "="*50 + "\n")

result8 = api_news(groww_company_id=sample_groww_id, page=0, size=5)
print(result8)
print("\n" + "="*50 + "\n")
# --- api_events ---
result9 = api_events(groww_company_id=sample_groww_id, debug=True)
print(result9)
print("\n" + "="*50 + "\n")
result10 = api_events(groww_company_id=sample_groww_id)
print(result10)
print("\n" + "="*50 + "\n")