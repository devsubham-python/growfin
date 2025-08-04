import pandas as pd
from typing import Optional, Union
from datetime import datetime
import calendar

from .utils import generate_parameters, generate_live_parameters
from .api import call_price_api, api_info, api_news, api_events
from .utils_info import get_search_id, get_growid


class Ticker:
    def __init__(self, symbol: str, debug: bool = False):
        self.symbol = symbol.upper()
        self.debug = debug
        self.suggestions = None
        self.search_id = None
        self.groww_id = None

        try:
            result = get_search_id(self.symbol, debug=debug)
            if isinstance(result, dict) and "suggestions" in result:
                self.suggestions = result["suggestions"]
                if debug:
                    print(f"[DEBUG] Suggestions found for '{self.symbol}': {self.suggestions}")
            else:
                self.search_id = result.get("search_id")
                self.groww_id = get_growid(self.symbol, debug=debug)
                if debug:
                    print(f"[DEBUG] Found search_id: {self.search_id}, groww_id: {self.groww_id}")
        except Exception as e:
            print(f"❌ Error initializing Ticker('{self.symbol}'): {e}")

    def history(
        self,
        interval: int,
        lookback: Optional[int] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        debug: bool = False
) ->     dict:
        """
        Fetches historical OHLCV data for the stock using Groww's candle API.

        This method supports both lookback mode (e.g., last N days) and fixed date range mode.
        It automatically handles batching for large date ranges as per Groww's interval limits.

        Parameters:
        - interval (int): Candle interval in minutes (e.g., 1, 15, 60)
        - lookback (int, optional): Number of days to look back from current date
        - start (str, optional): Start datetime string in format 'YYYY-MM-DD HH:MM'
        - end (str, optional): End datetime string in format 'YYYY-MM-DD HH:MM'
        - debug (bool, optional): If True, includes debug logs per batch

        Returns:
        - dict: {
            "data": {
                "candles": [...]  # List of raw Groww candle arrays
            } or None,
            "debug_info": [...],   # List of debug logs (if debug=True) or None,
            "error": [...],        # List of errors encountered during batch fetch or None
        }
        """

        # If the symbol wasn't matched, suggest alternatives
        if self.suggestions:
            print(f"Suggestions for '{self.symbol}':")
            for s in self.suggestions:
                print(s)
            return {
                "data": None,
                "debug_info": None,
                "error": [f"Invalid symbol '{self.symbol}'"]
            }

        try:
            param_batches = generate_parameters(
                interval=interval,
                lookback=lookback,
                start_date=start,
                end_date=end,
                debug=debug
            )
        except Exception as e:
            return {
                "data": None,
                "debug_info": None,
                "error": [str(e)]
            }

        all_candles = []
        debug_logs = []
        errors = []

        for batch in param_batches:
            result = call_price_api(
                ticker=self.symbol,
                start=batch["start_time"],
                end=batch["end_time"],
                interval=batch["interval"],
                debug=debug
            )

            if result.get("error"):
                errors.extend(result["error"])

            if result.get("debug_info"):
                debug_logs.extend(result["debug_info"])

            if result.get("data") and "candles" in result["data"]:
                all_candles.extend(result["data"]["candles"])

        return {
            "data": {"candles": all_candles} if all_candles else None,
            "debug_info": debug_logs if debug else None,
            "error": errors if errors else None
        }

    def live(
        self,
        interval: int,
        check_trading_day: bool = True,
        debug: bool = False
) ->     dict:
        """
        Fetches intraday live candle data for today from the Groww candle API.
    
        This method calculates today's trading window for the given interval and
        fetches candles for live market hours. It optionally checks if today is a valid
        trading day (Mon–Fri) unless overridden.
    
        Parameters:
        - interval (int): Candle interval in minutes (e.g., 1, 15, 60)
        - check_trading_day (bool): If True, raises an error on weekends
        - debug (bool): If True, returns debug logs for each API call
    
        Returns:
        - dict: {
            "data": {
                "candles": [...]  # List of Groww candle arrays
            } or None,
            "debug_info": [...],   # Debug logs (if debug=True) or None
            "error": [...],        # List of errors if any batch fails, else None
        }
        """
    
        # Check for invalid symbols
        if self.suggestions:
            print(f"Suggestions for '{self.symbol}':")
            for s in self.suggestions:
                print(s)
            return {
                "data": None,
                "debug_info": None,
                "error": [f"Invalid symbol '{self.symbol}'"]
            }
    
        today = datetime.now()
        weekday = today.weekday()
    
        if check_trading_day and weekday >= 5:
            return {
                "data": None,
                "debug_info": None,
                "error": [f"Today is {calendar.day_name[weekday]} — market is closed."]
            }
    
        try:
            param_batch = generate_live_parameters(interval, debug=debug)
        except ValueError as e:
            return {
                "data": None,
                "debug_info": None,
                "error": [f"Failed to generate live parameters: {str(e)}"]
            }
    
        all_candles = []
        debug_logs = []
        errors = []
    
        for batch in param_batch:
            result = call_price_api(
                ticker=self.symbol,
                start=batch["start_time"],
                end=batch["end_time"],
                interval=batch["interval"],
                debug=debug
            )
    
            if result.get("error"):
                errors.extend(result["error"])
    
            if result.get("debug_info"):
                debug_logs.extend(result["debug_info"])
    
            if result.get("data") and "candles" in result["data"]:
                all_candles.extend(result["data"]["candles"])
    
        return {
            "data": {"candles": all_candles} if all_candles else None,
            "debug_info": debug_logs if debug else None,
            "error": errors if errors else None
        }

    def info(self, debug: bool = False):
        if self.suggestions:
            print(f"Suggestions for '{self.symbol}':")
            for s in self.suggestions:
                print(s)
            return

        if not self.search_id:
            print("Search ID not available.")
            return

        try:
            data = api_info(self.search_id, debug=debug)
            print(data)
        except Exception as e:
            print(f"Failed to fetch company details: {e}")

    def events(self, debug: bool = False) -> dict:
        """
        Fetch corporate events for the current symbol with consistent return structure.
        
        Args:
            debug (bool): If True, returns debug information along with data
        
        Returns:
            dict: Consistent JSON response structure:
            {
                "data": {original API response} or None,
                "debug_info": [...] or None,
                "error": [...] or None
            }
        """
        debug_logs = []
        
        if debug:
            debug_logs.append(f"[DEBUG] Function: events")
            debug_logs.append(f"[DEBUG] Symbol: {self.symbol}")
            debug_logs.append(f"[DEBUG] Groww ID: {self.groww_id}")
            debug_logs.append(f"[DEBUG] Has suggestions: {bool(self.suggestions)}")
        
        # Handle case where suggestions exist
        if self.suggestions:
            suggestion_messages = [f"Suggestions for '{self.symbol}':"] + [str(s) for s in self.suggestions]
            
            if debug:
                debug_logs.append(f"[DEBUG] Returning suggestions instead of events")
                debug_logs.extend([f"[DEBUG] {msg}" for msg in suggestion_messages])
            
            return {
                "data": None,
                "debug_info": debug_logs if debug else None,
                "error": suggestion_messages
            }
        
        # Fetch events using api_events
        try:
            if debug:
                debug_logs.append(f"[DEBUG] Using cached Groww ID: {self.groww_id}")
                debug_logs.append(f"[DEBUG] Calling api_events with groww_company_id: {self.groww_id}")
            
            result = api_events(groww_company_id=self.groww_id, debug=debug)
            
            # Merge debug logs if both functions have debug enabled
            if debug and result.get("debug_info"):
                debug_logs.extend(result["debug_info"])
                result["debug_info"] = debug_logs
            elif debug:
                result["debug_info"] = debug_logs
                
            return result
            
        except Exception as e:
            error_msg = f"Failed to fetch events for {self.symbol} ({self.groww_id}): {str(e)}"
            
            if debug:
                debug_logs.append(f"[DEBUG] Exception in events(): {error_msg}")
            
            return {
                "data": None,
                "debug_info": debug_logs if debug else None,
                "error": [error_msg]
            }
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if debug:
                debug_logs.append(f"[DEBUG] Unexpected Exception: {error_msg}")
            
            return {
                "data": None,
                "debug_info": debug_logs if debug else None,
                "error": [error_msg]
            }
    
    
    def news(self, page: int = 0, size: int = 10, debug: bool = False) -> dict:
        """
        Fetch news for the current symbol with consistent return structure.
        
        Args:
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
        """
        debug_logs = []
        
        if debug:
            debug_logs.append(f"[DEBUG] Function: news")
            debug_logs.append(f"[DEBUG] Symbol: {self.symbol}")
            debug_logs.append(f"[DEBUG] Groww ID: {self.groww_id}")
            debug_logs.append(f"[DEBUG] Has suggestions: {bool(self.suggestions)}")
        
        # Handle case where suggestions exist
        if self.suggestions:
            suggestion_messages = [f"Suggestions for '{self.symbol}':"] + [str(s) for s in self.suggestions]
            
            if debug:
                debug_logs.append(f"[DEBUG] Returning suggestions instead of news")
                debug_logs.extend([f"[DEBUG] {msg}" for msg in suggestion_messages])
            
            return {
                "data": None,
                "debug_info": debug_logs if debug else None,
                "error": suggestion_messages
            }
        
        # Fetch news using api_news
        try:
            if debug:
                debug_logs.append(f"[DEBUG] Calling api_news with groww_company_id: {self.groww_id}")
            
            result = api_news(groww_company_id=self.groww_id, page=page, size=size, debug=debug)
            
            # Merge debug logs if both functions have debug enabled
            if debug and result.get("debug_info"):
                debug_logs.extend(result["debug_info"])
                result["debug_info"] = debug_logs
            elif debug:
                result["debug_info"] = debug_logs
                
            return result
            
        except Exception as e:
            error_msg = f"Failed to fetch news for {self.symbol} ({self.groww_id}): {str(e)}"
            
            if debug:
                debug_logs.append(f"[DEBUG] Exception in news(): {error_msg}")
            
            return {
                "data": None,
                "debug_info": debug_logs if debug else None,
                "error": [error_msg]
            }
