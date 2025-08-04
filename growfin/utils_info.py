from typing import Union
from .api import call_nse_api, api_info



def get_search_id(ticker: str, debug: bool = False) -> Union[dict, str]:
    """
    Fetches stock info from Groww search API and extracts matching NSE symbol info.

    Args:
        ticker (str): NSE ticker symbol (e.g., 'RELIANCE')
        debug (bool): Enable debug logging for API calls and function flow

    Returns:
        dict: If match found, includes nse_scrip_code, bse_scrip_code, search_id, and title.
        dict: If no match, suggests possible similar tickers.
        str : Error message if no content is returned.
    """
    if debug:
        print(f"[DEBUG] get_search_id() called with arguments:")
        print(f"  - ticker: {ticker}")
        print(f"  - debug: {debug}")
    
    # Call API with debug parameter
    response = call_nse_api(ticker, debug=debug)
    
    if debug:
        print(f"[DEBUG] API response received: {type(response)}")
        print(f"[DEBUG] Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        print(f"[DEBUG] Full response structure: {response}")
    
    # FIXED: Correct content extraction for nested structure
    content = None
    
    if isinstance(response, dict):
        # Method 1: Try the nested structure (debug mode)
        # response -> data -> data -> content
        if "data" in response and isinstance(response["data"], dict):
            data_level_1 = response["data"]
            if "data" in data_level_1 and isinstance(data_level_1["data"], dict):
                content = data_level_1["data"].get("content", [])
                if debug:
                    print(f"[DEBUG] Content extracted from response['data']['data']['content']: {len(content) if content else 0} items")
        
        # Method 2: Try direct content access (non-debug mode)
        if not content:
            # response -> data -> content (fallback for non-debug)
            if "data" in response and isinstance(response["data"], dict):
                content = response["data"].get("content", [])
                if debug:
                    print(f"[DEBUG] Content extracted from response['data']['content']: {len(content) if content else 0} items")
        
        # Method 3: Try root level content access
        if not content:
            content = response.get("content", [])
            if debug:
                print(f"[DEBUG] Content extracted from response['content']: {len(content) if content else 0} items")

    if not content:
        if debug:
            print("[DEBUG] No content found in API response after trying all extraction methods")
            print(f"[DEBUG] Full response structure for debugging:")
            print(f"[DEBUG] {response}")
        return "Please type a correct NSE symbol. No matches found."

    ticker = ticker.upper()
    if debug:
        print(f"[DEBUG] Searching for ticker: {ticker}")
        print(f"[DEBUG] Content items to search: {len(content)}")

    for item in content:
        if debug:
            print(f"[DEBUG] Checking item: {item.get('nse_scrip_code', 'N/A')}")
        
        if item.get("nse_scrip_code", "").upper() == ticker:
            result = {
                "nse_scrip_code": item.get("nse_scrip_code"),
                "bse_scrip_code": item.get("bse_scrip_code"),
                "search_id": item.get("search_id"),
                "title": item.get("title")
            }
            if debug:
                print(f"[DEBUG] Exact match found: {result}")
            return result

    # No exact match found — build suggestions
    suggestions = [
        {
            "nse_scrip_code": item.get("nse_scrip_code"),
            "title": item.get("title")
        }
        for item in content
        if item.get("nse_scrip_code")
    ]

    if debug:
        print(f"[DEBUG] No exact match. Built {len(suggestions)} suggestions")

    return {
        "message": "No exact match found. Are you looking for one of these?",
        "suggestions": suggestions
    }


def get_growid(ticker: str, debug: bool = False) -> Union[str, dict, None]:
    """
    Given an NSE ticker, fetch the Groww company ID (e.g., GSTK500325).
    
    Workflow:
    1. Use `get_search_id()` to get the search_id from the ticker.
    2. If suggestions returned instead of exact match, return suggestions dict.
    3. Use `api_info(search_id)` to get company info.
    4. Return `growwCompanyId` from header.

    Args:
        ticker (str): NSE symbol (e.g., 'RELIANCE')
        debug (bool): Enable debug logging for API calls and function flow

    Returns:
        str: Groww company ID (e.g., 'GSTK500325') if exact match found
        dict: Suggestions dictionary if no exact match found
        None: If error occurred or no content found
    """
    if debug:
        print(f"[DEBUG] get_growid() called with arguments:")
        print(f"  - ticker: {ticker}")
        print(f"  - debug: {debug}")
    
    if debug:
        print(f"[DEBUG] Looking up search_id for ticker: {ticker}")
    
    search_result = get_search_id(ticker, debug=debug)

    if debug:
        print(f"[DEBUG] get_search_id returned: {type(search_result)}")
        if isinstance(search_result, dict):
            print(f"[DEBUG] Keys in search_result: {list(search_result.keys())}")
        else:
            print(f"[DEBUG] search_result value: {search_result}")

    # Handle string response (error message)
    if isinstance(search_result, str):
        if debug:
            print(f"[DEBUG] String response received: {search_result}")
        return None

    # If suggestions returned - RETURN SUGGESTIONS INSTEAD OF None
    if isinstance(search_result, dict) and "suggestions" in search_result:
        if debug:
            print("[DEBUG] No exact match found, returning suggestions instead of None")
            print(f"[DEBUG] Suggestions count: {len(search_result['suggestions'])}")
        # FIXED: Return suggestions dict instead of None for professional trading
        return search_result

    # If exact match
    if isinstance(search_result, dict) and "search_id" in search_result:
        search_id = search_result["search_id"]
        if debug:
            print(f"[DEBUG] Exact match found, search_id: {search_id}")

        try:
            if debug:
                print(f"[DEBUG] Calling api_info with search_id: {search_id}")
            
            info = api_info(search_id, debug=debug)
            
            if debug:
                print(f"[DEBUG] api_info response received")
                print(f"[DEBUG] Response type: {type(info)}")
                print(f"[DEBUG] Response keys: {list(info.keys()) if isinstance(info, dict) else 'N/A'}")
                
                # Enhanced debugging for api_info response
                if isinstance(info, dict) and "header" in info:
                    print(f"[DEBUG] Header keys: {list(info['header'].keys()) if isinstance(info['header'], dict) else 'N/A'}")
                else:
                    print(f"[DEBUG] Full info response structure: {info}")
            
            # FIXED: Enhanced error handling for groww_id extraction with correct nested path
            if not isinstance(info, dict):
                if debug:
                    print(f"[DEBUG] api_info did not return a dict: {type(info)}")
                return None
            
            # Handle nested structure: info -> data -> header -> growwCompanyId
            header_data = None
            
            # Method 1: Try nested structure (debug mode) - info["data"]["header"]
            if "data" in info and isinstance(info["data"], dict):
                if "header" in info["data"] and isinstance(info["data"]["header"], dict):
                    header_data = info["data"]["header"]
                    if debug:
                        print(f"[DEBUG] Header found in nested structure: info['data']['header']")
            
            # Method 2: Try direct access (non-debug mode) - info["header"]
            if not header_data and "header" in info and isinstance(info["header"], dict):
                header_data = info["header"]
                if debug:
                    print(f"[DEBUG] Header found in direct structure: info['header']")
            
            if not header_data:
                if debug:
                    print(f"[DEBUG] 'header' key not found in api_info response")
                    print(f"[DEBUG] Available top-level keys: {list(info.keys())}")
                    if "data" in info and isinstance(info["data"], dict):
                        print(f"[DEBUG] Available data-level keys: {list(info['data'].keys())}")
                return None
            
            if "growwCompanyId" not in header_data:
                if debug:
                    print(f"[DEBUG] 'growwCompanyId' not found in header")
                    print(f"[DEBUG] Header keys: {list(header_data.keys())}")
                return None
            
            groww_id = header_data["growwCompanyId"]
            
            if debug:
                print(f"[DEBUG] Successfully extracted groww_id: {groww_id}")
            
            return groww_id
            
        except KeyError as e:
            if debug:
                print(f"[DEBUG] KeyError occurred: {e}")
                print(f"[DEBUG] Available keys in info: {list(info.keys()) if isinstance(info, dict) else 'N/A'}")
            return None
        except Exception as e:
            if debug:
                print(f"[DEBUG] Exception occurred: {e}")
                print(f"[DEBUG] Exception type: {type(e)}")
            return None

    if debug:
        print("[DEBUG] Unexpected error: Invalid response from get_search_id")
        print(f"[DEBUG] Received: {search_result}")
    
    return None


# Test cases
if __name__ == "__main__":
    print("="*60)
    print("TESTING WITH CORRECTED CONTENT EXTRACTION")
    print("="*60)
    
    # Example 1: get exact match with debug false get search id
    print("=== Test 1: RELIANCE without debug ===")
    result1 = get_search_id("RELIANCE")
    print(result1)

    print("\n" + "="*50 + "\n")

    # Example 2: get exact match with debug True get search id
    print("=== Test 2: RELIANCE with debug ===")
    result2 = get_search_id("RELIANCE", debug=True)
    print(result2)

    print("\n" + "="*50 + "\n")

    # Example 3: get approx match with debug False get search id
    print("=== Test 3: adani without debug ===")
    result3 = get_search_id("adani")
    print(result3)

    print("\n" + "="*50 + "\n")

    # Example 4: get approx match with debug True get search id
    print("=== Test 4: adani with debug ===")
    result4 = get_search_id("adani", debug=True)
    print(result4)

    print("\n" + "="*50 + "\n")

    # Example 5: get invalid data with debug false get search id
    print("=== Test 5: abc without debug ===")
    result5 = get_search_id("abc")
    print(result5)

    print("\n" + "="*50 + "\n")

    # Example 6: get invalid data with debug True get search id
    print("=== Test 6: abc with debug ===")
    result6 = get_search_id("abc", debug=True)
    print(result6)

    print("\n" + "="*50 + "\n")

    # Get Grow id tests
    print("=== Groww ID Tests ===")

    # Example 7: get exact match with debug false get grow id
    print("=== Test 7: RELIANCE growid without debug ===")
    result7 = get_growid("RELIANCE")
    print(result7)

    print("\n" + "="*50 + "\n")

    # Example 8: get exact match with debug True get grow id
    print("=== Test 8: RELIANCE growid with debug ===")
    result8 = get_growid("RELIANCE", debug=True)
    print(result8)

    print("\n" + "="*50 + "\n")

    # Example 9: get approx match with debug False get grow id
    print("=== Test 9: adani growid without debug ===")
    result9 = get_growid("adani")
    print(result9)

    print("\n" + "="*50 + "\n")

    # Example 10: get approx match with debug True get grow id
    print("=== Test 10: adani growid with debug ===")
    result10 = get_growid("adani", debug=True)
    print(result10)

    print("\n" + "="*50 + "\n")

    # Example 11: get invalid data with debug false get grow id
    print("=== Test 11: abc growid without debug ===")
    result11 = get_growid("abc")
    print(result11)

    print("\n" + "="*50 + "\n")

    # Example 12: get invalid data with debug True get grow id
    print("=== Test 12: abc growid with debug ===")
    result12 = get_growid("abc", debug=True)
    print(result12)

    print("\n" + "="*60 + "\n")


# Additional diagnostic function to confirm the structure
def diagnose_api_structure():
    """Diagnostic function to understand API response structure differences"""
    print("="*60)
    print("DIAGNOSTIC: API Response Structure Analysis")
    print("="*60)
    
    ticker = "RELIANCE"
    
    print("Without debug:")
    response_no_debug = call_nse_api(ticker, debug=False)
    print(f"Type: {type(response_no_debug)}")
    print(f"Keys: {list(response_no_debug.keys()) if isinstance(response_no_debug, dict) else 'N/A'}")
    if isinstance(response_no_debug, dict) and "data" in response_no_debug:
        print(f"Data keys: {list(response_no_debug['data'].keys()) if isinstance(response_no_debug['data'], dict) else 'N/A'}")
    
    print("\nWith debug:")
    response_with_debug = call_nse_api(ticker, debug=True)
    print(f"Type: {type(response_with_debug)}")
    print(f"Keys: {list(response_with_debug.keys()) if isinstance(response_with_debug, dict) else 'N/A'}")
    if isinstance(response_with_debug, dict) and "data" in response_with_debug:
        data_level_1 = response_with_debug['data']
        print(f"Data level 1 keys: {list(data_level_1.keys()) if isinstance(data_level_1, dict) else 'N/A'}")
        if isinstance(data_level_1, dict) and "data" in data_level_1:
            data_level_2 = data_level_1['data']
            print(f"Data level 2 keys: {list(data_level_2.keys()) if isinstance(data_level_2, dict) else 'N/A'}")
            if isinstance(data_level_2, dict) and "content" in data_level_2:
                content = data_level_2['content']
                print(f"Content items: {len(content) if isinstance(content, list) else 'Not a list'}")
    
    print("="*60)

# Uncomment the line below to run diagnostics
# diagnose_api_structure()