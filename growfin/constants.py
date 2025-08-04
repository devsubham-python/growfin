hist_url="https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH"
live_url="https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH"
news_url="https://groww.in/v1/api/groww-news/v2/stocks/news"
events_url="https://groww.in/v1/api/stocks_data/equity_feature/v2/company/corporate_action/event"
nse_url="https://groww.in/v1/api/search/v3/query/global/st_p_query"
info_url = "https://groww.in/v1/api/stocks_data/v1/company/search_id"

# Default headers for HTTP requests
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
}

# Supported candle intervals in minutes
SUPPORTED_INTERVALS = [1, 5, 10, 15, 30, 60, 240, 1440]
SUPPORTED_LIVE_INTERVALS = [1, 5, 10, 15, 30, 60, 240]
# API lookback limitations in days from the current date, based on interval
API_LOOKBACK_LIMITS = {
    1: 80,      # 1min: 80 days max
    5: 80,      # 5min: 80 days max
    10: 80,     # 10min: 80 days max
    15: 80,     # 15min: 80 days max
    30: 80,     # 30min: 80 days max
    60: 80,     # 60min: 80 days max
    240: 80,    # 4hour: 80 days max
    1440: 3650   # Daily: ~1 year max
}

# Batching limits per API request to avoid overwhelming the API
BATCH_LIMITS = {
    1: {'max_days_per_request': 7},
    5: {'max_days_per_request': 15},
    10: {'max_days_per_request': 30},
    15: {'max_days_per_request': 30},
    30: {'max_days_per_request': 30},
    60: {'max_days_per_request': 30},
    240: {'max_days_per_request': 60},
    1440: {'max_days_per_request': 1000}
}
