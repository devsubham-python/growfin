import requests
from typing import Dict
from .constants import hist_url, nse_url, info_url, news_url, events_url


def call_price_api(
    ticker: str,
    start: int,
    end: int,
    interval: int,
    debug: bool = False
) -> Dict:
    """
    Calls the Groww candle API and returns the raw JSON response in a consistent format.

    Parameters:
    - ticker (str): NSE stock symbol or Groww-compliant identifier (e.g., 'RELIANCE')
    - start (int): Start time in epoch milliseconds (UTC)
    - end (int): End time in epoch milliseconds (UTC)
    - interval (int): Candle interval in minutes (e.g., 1, 15, 60)
    - debug (bool): If True, includes detailed debug logs in the output

    Returns:
    - dict: {
        "data": {...}   # Original API JSON (contains 'candles') if successful, else None
        "debug_info": [...]  # List of debug logs if debug=True, else None
        "error": [...]  # List of error messages if request fails, else None
    }
    """

    debug_logs = []

    if debug:
        debug_logs.append("[DEBUG] Function: call_price_api")
        debug_logs.append(f"[DEBUG] Input Arguments:")
        debug_logs.append(f"  - ticker: {ticker}")
        debug_logs.append(f"  - start: {start}")
        debug_logs.append(f"  - end: {end}")
        debug_logs.append(f"  - interval: {interval}")

    url = f"{hist_url}/{ticker}"  # Ensure `hist_url` is globally defined
    params = {
        "startTimeInMillis": start,
        "endTimeInMillis": end,
        "intervalInMinutes": interval
    }

    try:
        response = requests.get(url, params=params)

        if debug:
            debug_logs.append(f"[DEBUG] Status Code: {response.status_code}")
            debug_logs.append(f"[DEBUG] Request URL: {response.url}")
            debug_logs.append(f"[DEBUG] Response Time: {response.elapsed.total_seconds():.3f}s")

        response.raise_for_status()  # Raises HTTPError for bad responses

        json_data = response.json()

        if debug:
            debug_logs.append(f"[DEBUG] Response JSON Keys: {list(json_data.keys())}")
            if "candles" in json_data:
                debug_logs.append(f"[DEBUG] Candle Count: {len(json_data['candles'])}")
                sample = json_data['candles'][:2] if json_data['candles'] else 'No candles'
                debug_logs.append(f"[DEBUG] Sample Candle Data: {sample}")
            debug_logs.append(f"[DEBUG] API call successful")

        return {
            "data": json_data,
            "debug_info": debug_logs if debug else None,
            "error": None
        }

    except requests.RequestException as e:
        if debug:
            debug_logs.append(f"[DEBUG] Request failed: {str(e)}")
            debug_logs.append(f"[DEBUG] Exception type: {type(e).__name__}")
        return {
            "data": None,
            "debug_info": debug_logs if debug else None,
            "error": [str(e)]
        }
    
    
def call_nse_api(ticker: str, debug: bool = False) -> dict:
    """
    Calls NSE API to search for stock information.

    Parameters:
    - ticker (str): Stock symbol to search for
    - debug (bool): If True, returns debug information along with data

    Returns:
    - dict: JSON response from API (with debug info if debug=True)
    
    Raises:
    - RuntimeError: If API call fails (only when debug=False)
    """
    debug_logs = []
    
    if debug:
        debug_logs.append(f"[DEBUG] Function: call_nse_api")
        debug_logs.append(f"[DEBUG] Input Arguments:")
        debug_logs.append(f"  - ticker: {ticker}")
        debug_logs.append(f"  - debug: {debug}")

    params = {
        "entity_type": "stocks",
        "page": 0,
        "query": ticker,
        "size": 6,
        "web": "false"
    }

    if debug:
        debug_logs.append(f"[DEBUG] API URL: {nse_url}")
        debug_logs.append(f"[DEBUG] Request Parameters: {params}")
        debug_logs.append(f"[DEBUG] Full URL with params: {nse_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}")

    try:
        response = requests.get(nse_url, params=params)
        
        if debug:
            debug_logs.append(f"[DEBUG] Response Status Code: {response.status_code}")
            debug_logs.append(f"[DEBUG] Response URL: {response.url}")
            debug_logs.append(f"[DEBUG] Response Headers: {dict(response.headers)}")
            debug_logs.append(f"[DEBUG] Response Time: {response.elapsed.total_seconds():.3f} seconds")
            debug_logs.append(f"[DEBUG] Response Text (first 500 chars): {response.text[:500]}")
        
        response.raise_for_status()
        json_data = response.json()
        
        if debug:
            debug_logs.append(f"[DEBUG] Response JSON Keys: {list(json_data.keys())}")
            debug_logs.append(f"[DEBUG] API call successful")
            
            return {
                "data": json_data,
                "debug_info": debug_logs
            }
        
        return json_data
        
    except requests.RequestException as e:
        error_msg = f"API call failed: {e}"
        if debug:
            debug_logs.append(f"[DEBUG] Request failed with error: {str(e)}")
            debug_logs.append(f"[DEBUG] Error type: {type(e).__name__}")
            return {
                "data": None,
                "debug_info": debug_logs,
                "error": error_msg
            }
        raise RuntimeError(error_msg)

def api_info(search_id: str, debug: bool = False) -> dict:
    """
    Fetch static company info (like COMPANY_HEADER and STATIC_PRICE) from Groww using search_id.

    Args:
        search_id (str): Unique search ID of the company (e.g., 'reliance-industries-ltd')
        debug (bool): If True, returns debug information along with data

    Returns:
        dict: JSON response from the API (with debug info if debug=True)

    Raises:
        RuntimeError: If the API request fails (only when debug=False)
    """
    debug_logs = []
    
    if debug:
        debug_logs.append(f"[DEBUG] Function: api_info")
        debug_logs.append(f"[DEBUG] Input Arguments:")
        debug_logs.append(f"  - search_id: {search_id}")
        debug_logs.append(f"  - debug: {debug}")

    url = f"{info_url}/{search_id}"
    params = {
        "fields": "COMPANY_HEADER,STATIC_PRICE",
        "page": 1,
        "size": 10
    }

    if debug:
        debug_logs.append(f"[DEBUG] API URL: {url}")
        debug_logs.append(f"[DEBUG] Request Parameters: {params}")
        debug_logs.append(f"[DEBUG] Full URL with params: {url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}")

    try:
        response = requests.get(url, params=params)
        
        if debug:
            debug_logs.append(f"[DEBUG] Response Status Code: {response.status_code}")
            debug_logs.append(f"[DEBUG] Response URL: {response.url}")
            debug_logs.append(f"[DEBUG] Response Headers: {dict(response.headers)}")
            debug_logs.append(f"[DEBUG] Response Time: {response.elapsed.total_seconds():.3f} seconds")
            debug_logs.append(f"[DEBUG] Response Text (first 500 chars): {response.text[:500]}")
        
        response.raise_for_status()
        json_data = response.json()
        
        if debug:
            debug_logs.append(f"[DEBUG] Response JSON Keys: {list(json_data.keys())}")
            debug_logs.append(f"[DEBUG] API call successful")
            
            return {
                "data": json_data,
                "debug_info": debug_logs
            }
        
        return json_data
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch company info: {e}"
        if debug:
            debug_logs.append(f"[DEBUG] Request failed with error: {str(e)}")
            debug_logs.append(f"[DEBUG] Error type: {type(e).__name__}")
            return {
                "data": None,
                "debug_info": debug_logs,
                "error": error_msg
            }
        raise RuntimeError(error_msg)

def api_news(groww_company_id: str, page: int = 0, size: int = 10, debug: bool = False) -> dict:
    """
    Fetch recent news articles for a company using its Groww ID.

    Args:
        groww_company_id (str): Groww company ID (e.g., 'GSTK500180')
        page (int): Page number for pagination
        size (int): Number of results per page
        debug (bool): If True, returns debug information along with data

    Returns:
        dict: Consistent JSON response structure:
        {
            "data": {original API response} or None,
            "debug_info": [...] or None,
            "error": [...] or None
        }

    Raises:
        Never raises exceptions - errors are returned in the response structure
    """
    debug_logs = []
    
    if debug:
        debug_logs.append(f"[DEBUG] Function: api_news")
        debug_logs.append(f"[DEBUG] Input Arguments:")
        debug_logs.append(f"  - groww_company_id: {groww_company_id}")
        debug_logs.append(f"  - page: {page}")
        debug_logs.append(f"  - size: {size}")
        debug_logs.append(f"  - debug: {debug}")

    url = f"{news_url}/{groww_company_id}"
    params = {
        "page": page,
        "size": size
    }

    if debug:
        debug_logs.append(f"[DEBUG] API URL: {url}")
        debug_logs.append(f"[DEBUG] Request Parameters: {params}")
        debug_logs.append(f"[DEBUG] Full URL with params: {url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}")

    try:
        response = requests.get(url, params=params)
        
        if debug:
            debug_logs.append(f"[DEBUG] Response Status Code: {response.status_code}")
            debug_logs.append(f"[DEBUG] Response URL: {response.url}")
            debug_logs.append(f"[DEBUG] Response Headers: {dict(response.headers)}")
            debug_logs.append(f"[DEBUG] Response Time: {response.elapsed.total_seconds():.3f} seconds")
            debug_logs.append(f"[DEBUG] Response Text (first 500 chars): {response.text[:500]}")
        
        response.raise_for_status()
        json_data = response.json()
        
        if debug:
            debug_logs.append(f"[DEBUG] Response JSON Keys: {list(json_data.keys())}")
            if 'content' in json_data and isinstance(json_data['content'], list):
                debug_logs.append(f"[DEBUG] Number of news items: {len(json_data['content'])}")
            debug_logs.append(f"[DEBUG] API call successful")
        
        # The API already returns data in {"results": [...]} format
        # Just wrap it in our consistent structure
        return {
            "data": json_data,  # API response already has "results" key
            "debug_info": debug_logs if debug else None,
            "error": None
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        if debug:
            debug_logs.append(f"[DEBUG] Request Exception: {error_msg}")
        
        return {
            "data": None,
            "debug_info": debug_logs if debug else None,
            "error": [error_msg]
        }


def api_events(groww_company_id: str, debug: bool = False) -> dict:
    """
    Fetch corporate action event details for a company using its Groww ID (GSIN).

    Args:
        groww_company_id (str): Groww company ID (e.g., 'GSTK532720')
        debug (bool): If True, returns debug information along with data

    Returns:
        dict: Consistent JSON response structure:
        {
            "data": {original API response},
            "debug_info": [...] or None,
            "error": [...] or None
        }

    Raises:
        Never raises exceptions - errors are returned in the response structure
    """
    debug_logs = []
    
    if debug:
        debug_logs.append(f"[DEBUG] Function: api_events")
        debug_logs.append(f"[DEBUG] Input Arguments:")
        debug_logs.append(f"  - groww_company_id: {groww_company_id}")
        debug_logs.append(f"  - debug: {debug}")

    url = f"{events_url}?gsin={groww_company_id}"

    if debug:
        debug_logs.append(f"[DEBUG] API URL: {events_url}")
        debug_logs.append(f"[DEBUG] Request Parameters: gsin={groww_company_id}")
        debug_logs.append(f"[DEBUG] Full URL: {url}")

    try:
        response = requests.get(url)
        
        if debug:
            debug_logs.append(f"[DEBUG] Response Status Code: {response.status_code}")
            debug_logs.append(f"[DEBUG] Response URL: {response.url}")
            debug_logs.append(f"[DEBUG] Response Headers: {dict(response.headers)}")
            debug_logs.append(f"[DEBUG] Response Time: {response.elapsed.total_seconds():.3f} seconds")
            debug_logs.append(f"[DEBUG] Response Text (first 500 chars): {response.text[:500]}")
        
        response.raise_for_status()
        json_data = response.json()
        
        if debug:
            debug_logs.append(f"[DEBUG] JSON parsed successfully")
            debug_logs.append(f"[DEBUG] Response JSON Keys: {list(json_data.keys())}")
            if 'events' in json_data and isinstance(json_data['events'], list):
                debug_logs.append(f"[DEBUG] Number of events: {len(json_data['events'])}")
            debug_logs.append(f"[DEBUG] API call successful")
        
        # API returns the full response, keep it as is
        return {
            "data": json_data,
            "debug_info": debug_logs if debug else None,
            "error": None
        }
        
    except requests.exceptions.RequestException as req_err:
        error_msg = f"HTTP Request failed: {str(req_err)}"
        if debug:
            debug_logs.append(f"[DEBUG] HTTP Request failed: {str(req_err)}")
            debug_logs.append(f"[DEBUG] Error type: {type(req_err).__name__}")
        
        return {
            "data": None,
            "debug_info": debug_logs if debug else None,
            "error": [error_msg]
        }
    
    except ValueError as val_err:
        error_msg = f"Failed to decode JSON: {str(val_err)}"
        if debug:
            debug_logs.append(f"[DEBUG] JSON decode failed: {str(val_err)}")
            debug_logs.append(f"[DEBUG] Error type: {type(val_err).__name__}")
        
        return {
            "data": None,
            "debug_info": debug_logs if debug else None,
            "error": [error_msg]
        }
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if debug:
            debug_logs.append(f"[DEBUG] Unexpected error: {str(e)}")
            debug_logs.append(f"[DEBUG] Error type: {type(e).__name__}")
        
        return {
            "data": None,
            "debug_info": debug_logs if debug else None,
            "error": [error_msg]
        }
