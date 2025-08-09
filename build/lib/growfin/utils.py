from .constants import API_LOOKBACK_LIMITS, BATCH_LIMITS, SUPPORTED_INTERVALS, SUPPORTED_LIVE_INTERVALS
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import pytz
import tzlocal



# Configure logging
logger = logging.getLogger(__name__)


class DateTimeValidationError(ValueError):
    """Custom exception for datetime validation errors."""
    pass


class ParameterValidationError(ValueError):
    """Custom exception for parameter validation errors."""
    pass

#start data_to_dataframe with helper function

def data_to_dataframe(data: Dict) -> pd.DataFrame:
    """
    Convert Groww API candle data dictionary into a pandas DataFrame with IST times.
    
    This function processes raw API candle data and converts Unix timestamps to 
    IST timezone-aware datetime objects (naive), ensuring all numeric columns 
    are properly typed.
    
    Args:
        data (Dict): API response dictionary containing 'candles' key with 
                    nested list of [timestamp, open, high, low, close, volume]
    
    Returns:
        pd.DataFrame: DataFrame with columns:
            - unix_timestamp (int): Original Unix timestamp
            - time_ist (datetime): IST timezone datetime (naive)
            - open (float): Opening price
            - high (float): Highest price
            - low (float): Lowest price
            - close (float): Closing price
            - volume (float): Trading volume
    
    Raises:
        TypeError: If data is not a dictionary
        KeyError: If 'candles' key is missing from data
    
    Example:
        >>> api_data = {'candles': [[1640995200, 100.5, 101.0, 99.5, 100.8, 1000]]}
        >>> df = data_to_dataframe(api_data)
        >>> print(df.columns.tolist())
        ['unix_timestamp', 'time_ist', 'open', 'high', 'low', 'close', 'volume']
    """
    # Input validation
    if not isinstance(data, dict):
        logger.error(f"Expected dict, got {type(data).__name__}")
        raise TypeError(f"Data must be a dictionary, got {type(data).__name__}")
    
    if 'candles' not in data:
        logger.error("Missing 'candles' key in data dictionary")
        raise KeyError("Data dictionary must contain 'candles' key")
    
    if not data['candles']:
        logger.warning("Empty candles data provided")
        return _create_empty_dataframe()
    
    # Filter valid candle entries
    valid_candles = _filter_valid_candles(data['candles'])
    
    if not valid_candles:
        logger.warning("No valid candles data after filtering")
        return _create_empty_dataframe()
    
    # Create DataFrame
    df = pd.DataFrame(
        valid_candles, 
        columns=['unix_timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    
    # Convert timestamp to IST and insert as second column
    df.insert(1, 'time_ist', _convert_timestamp_to_ist(df['unix_timestamp']))
    
    # Ensure numeric data types
    df = _ensure_numeric_columns(df)
    
    logger.info(f"Successfully converted {len(df)} candles to DataFrame")
    return df


def _create_empty_dataframe() -> pd.DataFrame:
    """Create empty DataFrame with expected column structure."""
    return pd.DataFrame(
        columns=['unix_timestamp', 'time_ist', 'open', 'high', 'low', 'close', 'volume']
    )


def _filter_valid_candles(candles: List) -> List:
    """Filter candles to only include valid 6-element sequences."""
    return [
        candle for candle in candles 
        if isinstance(candle, (list, tuple)) and len(candle) == 6
    ]


def _convert_timestamp_to_ist(timestamps: pd.Series) -> pd.Series:
    """Convert Unix timestamps to IST naive datetime objects."""
    ist_tz = pytz.timezone('Asia/Kolkata')
    return (
        pd.to_datetime(timestamps, unit='s', utc=True)
        .dt.tz_convert(ist_tz)
        .dt.tz_localize(None)
    )


def _ensure_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert price and volume columns to float type with error handling."""
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    
    for col in numeric_columns:
        original_na_count = df[col].isna().sum()
        df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)
        new_na_count = df[col].isna().sum()
        
        if new_na_count > original_na_count:
            logger.warning(
                f"Column '{col}': {new_na_count - original_na_count} "
                f"values converted to NaN due to invalid data"
            )
    
    return df

# start validate_datetime_format with helper function 


def validate_datetime_format(dt_str: str) -> datetime:
    """
    Validate datetime string in strict 'YYYY-MM-DD' format.
    
    This function ensures the input string matches exactly the expected format
    and represents a valid calendar date.
    
    Args:
        dt_str (str): Date string in 'YYYY-MM-DD' format
    
    Returns:
        datetime: Parsed datetime object (naive)
    
    Raises:
        TypeError: If input is not a string
        DateTimeValidationError: If string format is invalid or date is invalid
    
    Example:
        >>> dt = validate_datetime_format('2023-12-25')
        >>> print(dt.strftime('%Y-%m-%d'))
        2023-12-25
    """
    if not isinstance(dt_str, str):
        logger.error(f"Expected string input, got {type(dt_str).__name__}")
        raise TypeError(f"Input must be a string, got {type(dt_str).__name__}")
    
    # Validate format using regex for additional safety
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not date_pattern.match(dt_str):
        logger.error(f"Invalid date format: '{dt_str}'. Expected 'YYYY-MM-DD'")
        raise DateTimeValidationError(
            f"Invalid date format: '{dt_str}'. Expected 'YYYY-MM-DD'"
        )
    
    try:
        parsed_date = datetime.strptime(dt_str, '%Y-%m-%d')
        logger.debug(f"Successfully validated date: {dt_str}")
        return parsed_date
    except ValueError as e:
        logger.error(f"Invalid date value: '{dt_str}' - {str(e)}")
        raise DateTimeValidationError(
            f"Invalid date value: '{dt_str}'. Please provide a valid calendar date."
        ) from e
# Checked and passed all the test cases 

# start to convert to unixtimestamp

def convert_to_unixtimestamp(
    date_time: str, 
    timezone: Optional[str] = None
) -> int:
    """
    Convert datetime string to Unix timestamp in milliseconds with timezone handling.
    
    This function parses a datetime string and converts it to Unix timestamp,
    applying either the specified timezone or the local system timezone.
    
    Args:
        date_time (str): Datetime string in 'YYYY-MM-DD HH:MM' format
        timezone (str, optional): Target timezone (e.g., 'Asia/Kolkata').
                                 Defaults to local timezone.
    
    Returns:
        int: Unix timestamp in milliseconds
    
    Raises:
        TypeError: If date_time is not a string
        DateTimeValidationError: If datetime format is invalid
        ValueError: If timezone is unknown
    
    Example:
        >>> timestamp = convert_to_unixtimestamp('2023-12-25 10:30', 'Asia/Kolkata')
        >>> isinstance(timestamp, int)
        True
    """
    if not isinstance(date_time, str):
        logger.error(f"Expected string input, got {type(date_time).__name__}")
        raise TypeError(
            f"DateTime input must be a string in 'YYYY-MM-DD HH:MM' format, "
            f"got {type(date_time).__name__}"
        )
    
    # Validate and parse datetime
    try:
        dt = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
        logger.debug(f"Successfully parsed datetime: {date_time}")
    except ValueError as e:
        logger.error(f"Invalid datetime format: '{date_time}'")
        raise DateTimeValidationError(
            f"Invalid datetime format: '{date_time}'. Expected 'YYYY-MM-DD HH:MM'"
        ) from e
    
    # Resolve timezone
    target_tz = _resolve_timezone(timezone)
    
    # Localize naive datetime
    if dt.tzinfo is None:
        localized_dt = target_tz.localize(dt)
    else:
        localized_dt = dt.astimezone(target_tz)
    
    timestamp_ms = int(localized_dt.timestamp() * 1000)
    logger.debug(f"Converted '{date_time}' to timestamp: {timestamp_ms}")
    
    return timestamp_ms


def _resolve_timezone(timezone: Optional[str]) -> pytz.BaseTzInfo:
    """Resolve timezone string to pytz timezone object."""
    if timezone:
        try:
            return pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError as e:
            logger.error(f"Unknown timezone: '{timezone}'")
            raise ValueError(f"Unknown timezone: '{timezone}'") from e
    else:
        local_tz = tzlocal.get_localzone()
        logger.debug(f"Using local timezone: {local_tz}")
        return local_tz


def validate_parameters(
    interval_minutes: int,
    lookback_days: Optional[int] = None,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
    debug: bool = False
) -> None:
    """
    Validate API parameters for time series data requests.
    
    This function performs comprehensive validation of interval constraints,
    date range logic, and API limitations to ensure request parameters 
    are valid before processing.
    
    Args:
        interval_minutes (int): Data interval in minutes
        lookback_days (int, optional): Number of days to look back from now
        start_date_str (str, optional): Start date in 'YYYY-MM-DD' format
        end_date_str (str, optional): End date in 'YYYY-MM-DD' format
        debug (bool): Enable debug output
    
    Raises:
        ParameterValidationError: If any validation rule is violated
        
    Validation Rules:
        1. Interval must be supported
        2. Cannot provide both lookback_days and date range
        3. Must provide either lookback_days or both start/end dates
        4. Lookback period must not exceed API limits
        5. Date range must not exceed API limits
        6. Start date must be before or equal to end date
    
    Example:
        >>> validate_parameters(5, lookback_days=30)  # Valid
        >>> validate_parameters(5, start_date_str='2023-01-01', end_date_str='2023-01-31')  # Valid
    """
    if debug:
        print(f"🔍 [DEBUG] Starting parameter validation...")
        print(f"   - interval_minutes: {interval_minutes}")
        print(f"   - lookback_days: {lookback_days}")
        print(f"   - start_date_str: {start_date_str}")
        print(f"   - end_date_str: {end_date_str}")
    
    logger.debug(
        f"Validating parameters: interval={interval_minutes}, "
        f"lookback={lookback_days}, start={start_date_str}, end={end_date_str}"
    )
    
    # Validate interval support
    if debug:
        print(f"🎯 [DEBUG] Checking interval support...")
    
    if interval_minutes not in SUPPORTED_INTERVALS:
        error_msg = (
            f"Interval {interval_minutes} minutes is not supported. "
            f"Supported intervals: {sorted(SUPPORTED_INTERVALS)}"
        )
        if debug:
            print(f"❌ [DEBUG] Interval validation FAILED: {error_msg}")
        logger.error(error_msg)
        raise ParameterValidationError(error_msg)
    
    if debug:
        print(f"✅ [DEBUG] Interval {interval_minutes} is supported")
    
    # Validate parameter combination logic
    has_lookback = lookback_days is not None
    has_date_range = start_date_str is not None or end_date_str is not None
    
    if debug:
        print(f"🎯 [DEBUG] Checking parameter combination logic...")
        print(f"   - has_lookback: {has_lookback}")
        print(f"   - has_date_range: {has_date_range}")
    
    if has_lookback and has_date_range:
        error_msg = (
            "Cannot specify both lookback_days and date range. "
            "Provide either lookback_days or both start_date and end_date."
        )
        if debug:
            print(f"❌ [DEBUG] Parameter combination FAILED: {error_msg}")
        logger.error(error_msg)
        raise ParameterValidationError(error_msg)
    
    if not has_lookback and not (start_date_str and end_date_str):
        error_msg = (
            "Must provide either lookback_days or both start_date and end_date."
        )
        if debug:
            print(f"❌ [DEBUG] Parameter combination FAILED: {error_msg}")
        logger.error(error_msg)
        raise ParameterValidationError(error_msg)
    
    if debug:
        print(f"✅ [DEBUG] Parameter combination is valid")
    
    # Validate lookback constraints
    if has_lookback:
        if debug:
            print(f"🎯 [DEBUG] Validating lookback constraints...")
        _validate_lookback_constraints(interval_minutes, lookback_days, debug)
    
    # Validate date range constraints
    if start_date_str and end_date_str:
        if debug:
            print(f"🎯 [DEBUG] Validating date range constraints...")
        _validate_date_range_constraints(interval_minutes, start_date_str, end_date_str, debug)
    
    if debug:
        print(f"✅ [DEBUG] All parameter validations PASSED")
    
    logger.info("Parameter validation successful")


def _validate_lookback_constraints(interval_minutes: int, lookback_days: int, debug: bool = False) -> None:
    """Validate lookback period against API limits."""
    max_days = API_LOOKBACK_LIMITS[interval_minutes]
    
    if debug:
        print(f"   - lookback_days: {lookback_days}")
        print(f"   - max_allowed_days: {max_days}")
    
    if lookback_days > max_days:
        error_msg = (
            f"Lookback period {lookback_days} days exceeds maximum allowed "
            f"{max_days} days for {interval_minutes}-minute interval"
        )
        if debug:
            print(f"❌ [DEBUG] Lookback validation FAILED: {error_msg}")
        logger.error(error_msg)
        raise ParameterValidationError(error_msg)
    
    if debug:
        print(f"✅ [DEBUG] Lookback constraint validation PASSED")


def _validate_date_range_constraints(
    interval_minutes: int, 
    start_date_str: str, 
    end_date_str: str,
    debug: bool = False
) -> None:
    """Validate date range against API limits and logical constraints."""
    if debug:
        print(f"   - Parsing start_date: {start_date_str}")
        print(f"   - Parsing end_date: {end_date_str}")
    
    try:
        start_dt = validate_datetime_format(start_date_str)
        end_dt = validate_datetime_format(end_date_str)
        if debug:
            print(f"   - Parsed start_dt: {start_dt}")
            print(f"   - Parsed end_dt: {end_dt}")
    except DateTimeValidationError as e:
        if debug:
            print(f"❌ [DEBUG] Date parsing FAILED: {str(e)}")
        raise ParameterValidationError(f"Date validation failed: {str(e)}") from e
    
    # Validate date order
    if start_dt > end_dt:
        error_msg = f"Start date {start_date_str} must be before or equal to end date {end_date_str}"
        if debug:
            print(f"❌ [DEBUG] Date order validation FAILED: {error_msg}")
        logger.error(error_msg)
        raise ParameterValidationError(error_msg)
    
    if debug:
        print(f"✅ [DEBUG] Date order is valid")
    
    # Validate against API limits
    max_days = API_LOOKBACK_LIMITS[interval_minutes]
    now = datetime.now()
    
    start_age_days = (now - start_dt).days
    end_age_days = (now - end_dt).days
    
    if debug:
        print(f"   - max_allowed_days: {max_days}")
        print(f"   - start_age_days: {start_age_days}")
        print(f"   - end_age_days: {end_age_days}")
    
    if start_age_days > max_days or end_age_days > max_days:
        error_msg = (
            f"Date range extends beyond {max_days} days limit for "
            f"{interval_minutes}-minute interval. Start: {start_age_days} days ago, "
            f"End: {end_age_days} days ago"
        )
        if debug:
            print(f"❌ [DEBUG] Date range validation FAILED: {error_msg}")
        logger.error(error_msg)
        raise ParameterValidationError(error_msg)
    
    if debug:
        print(f"✅ [DEBUG] Date range constraint validation PASSED")


def create_batches(
    interval_minutes: int,
    lookback_days: Optional[int] = None,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
    debug: bool = False
) -> List[Dict[str, str]]:
    """
    Create time-based batches for API requests based on interval constraints.
    
    This function splits a date range into smaller batches that respect API
    limitations for different time intervals. Each batch represents a time
    window that can be safely requested from the API.
    
    Args:
        interval_minutes (int): Data interval in minutes
        lookback_days (int, optional): Days to look back from current time
        start_date_str (str, optional): Start date in 'YYYY-MM-DD' format  
        end_date_str (str, optional): End date in 'YYYY-MM-DD' format
        debug (bool): Enable debug output
    
    Returns:
        List[Dict[str, str]]: List of batch dictionaries with 'start' and 'end' keys
                             in 'YYYY-MM-DD HH:MM' format. Returns empty list if 
                             validation fails.
    
    Raises:
        ParameterValidationError: If parameter validation fails
    
    Example:
        >>> batches = create_batches(5, lookback_days=60)
        >>> print(len(batches))  # Number of batches created
        >>> print(batches[0])    # {'start': '2023-11-01 00:01', 'end': '2023-11-30 23:59'}
    """
    if debug:
        print(f"🔧 [DEBUG] Starting batch creation...")
    
    try:
        validate_parameters(interval_minutes, lookback_days, start_date_str, end_date_str, debug)
    except ParameterValidationError as e:
        if debug:
            print(f"❌ [DEBUG] Batch creation FAILED due to validation error: {str(e)}")
        logger.error(f"Batch creation failed due to validation error: {str(e)}")
        return []
    
    if debug:
        print(f"✅ [DEBUG] Parameter validation PASSED, proceeding with batch creation...")
    
    # Determine overall date range
    start_date, end_date = _determine_date_range(lookback_days, start_date_str, end_date_str, debug)
    
    # Get batching configuration
    batch_config = BATCH_LIMITS[interval_minutes]
    max_days_per_batch = batch_config['max_days_per_request']
    
    if debug:
        print(f"🔧 [DEBUG] Batch configuration:")
        print(f"   - max_days_per_batch: {max_days_per_batch}")
        print(f"   - overall_start_date: {start_date}")
        print(f"   - overall_end_date: {end_date}")
    
    # Generate batches
    batches = _generate_batch_list(start_date, end_date, max_days_per_batch, debug)
    
    if debug:
        print(f"✅ [DEBUG] Created {len(batches)} batches successfully")
    
    logger.info(f"Created {len(batches)} batches for {interval_minutes}-minute interval")
    return batches


def _determine_date_range(
    lookback_days: Optional[int],
    start_date_str: Optional[str], 
    end_date_str: Optional[str],
    debug: bool = False
) -> Tuple[datetime, datetime]:
    """Determine the overall start and end dates for batch creation."""
    if lookback_days is not None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        if debug:
            print(f"🗓️ [DEBUG] Using lookback: {lookback_days} days from {end_date}")
        logger.debug(f"Using lookback: {lookback_days} days from {end_date}")
    else:
        start_date = validate_datetime_format(start_date_str)
        end_date = validate_datetime_format(end_date_str)
        if debug:
            print(f"🗓️ [DEBUG] Using date range: {start_date} to {end_date}")
        logger.debug(f"Using date range: {start_date} to {end_date}")
    
    return start_date, end_date

def _generate_batch_list(
    start_date: datetime, 
    end_date: datetime, 
    max_days_per_batch: int,
    debug: bool = False
) -> List[Dict[str, str]]:
    """Generate list of batch dictionaries covering the date range."""
    batches = []
    current_start = start_date

    if debug:
        print(f"🔧 [DEBUG] Generating batches...")

    while current_start <= end_date:
        # Batch start always at 00:01
        batch_start = current_start.replace(hour=0, minute=1, second=0, microsecond=0)

        # Calculate batch_end: max allowed or final day at 23:59
        next_day = batch_start + timedelta(days=max_days_per_batch - 1)
        batch_end = min(
            next_day.replace(hour=23, minute=59, second=0, microsecond=0),
            end_date.replace(hour=23, minute=59, second=0, microsecond=0)
        )

        batch_dict = {
            'start': batch_start.strftime("%Y-%m-%d %H:%M"),
            'end': batch_end.strftime("%Y-%m-%d %H:%M")
        }
        
        batches.append(batch_dict)

        if debug:
            print(f"   - Batch {len(batches)}: {batch_dict}")
        
        logger.debug(f"Created batch: {batch_start} to {batch_end}")
        current_start = batch_end + timedelta(minutes=1)  # avoid overlap

    return batches

def generate_parameters(
    interval: int, 
    lookback: Optional[int], 
    start_date: Optional[str], 
    end_date: Optional[str],
    debug: bool = False
) -> List[Dict[str, int]]:
    """
    Generate API request parameters with Unix timestamp conversion.
    
    This function combines parameter validation, batch creation, and timestamp
    conversion to produce a list of API-ready parameter dictionaries with
    Unix timestamps in milliseconds.
    
    Args:
        interval (int): Data interval in minutes
        lookback (int, optional): Days to look back from current time
        start_date (str, optional): Start date in 'YYYY-MM-DD' format
        end_date (str, optional): End date in 'YYYY-MM-DD' format
        debug (bool): Enable debug output
    
    Returns:
        List[Dict[str, int]]: List of parameter dictionaries with:
            - interval (int): Original interval value
            - start_time (int): Start Unix timestamp in milliseconds
            - end_time (int): End Unix timestamp in milliseconds
    
    Raises:
        ParameterValidationError: If parameter validation fails
        ValueError: If batch creation or timestamp conversion fails
    
    Example:
        >>> params = generate_parameters(5, lookback=30, start_date=None, end_date=None)
        >>> print(params[0]['interval'])  # 5
        >>> print(type(params[0]['start_time']))  # <class 'int'>
        >>> print(params[0]['start_time'])  # 1640995200000 (example timestamp)
    """
    if debug:
        print(f"🚀 [DEBUG] Starting parameter generation...")
        print(f"   - interval: {interval}")
        print(f"   - lookback: {lookback}")
        print(f"   - start_date: {start_date}")
        print(f"   - end_date: {end_date}")
    
    logger.info(f"Generating parameters for interval={interval}, lookback={lookback}")
    
    # Validate parameters
    try:
        validate_parameters(interval, lookback, start_date, end_date, debug)
    except ParameterValidationError as e:
        if debug:
            print(f"❌ [DEBUG] Parameter generation FAILED: {str(e)}")
            print(f"🛑 [DEBUG] Breaking execution - validation failed")
        logger.error(f"Parameter generation failed: {str(e)}")
        raise ValueError(f"Parameter validation failed: {str(e)}") from e
    
    if debug:
        print(f"✅ [DEBUG] Validation PASSED, proceeding to batch creation...")
    
    # Create batches
    batches = create_batches(interval, lookback, start_date, end_date, debug)
    
    if not batches:
        if debug:
            print(f"❌ [DEBUG] No batches created, returning empty parameter list")
        logger.warning("No batches created, returning empty parameter list")
        return []
    
    if debug:
        print(f"🔧 [DEBUG] Converting batches to Unix timestamps...")
    
    # Convert datetime strings to Unix timestamps and format result parameters
    result = []
    for i, batch in enumerate(batches):
        try:
            start_timestamp = convert_to_unixtimestamp(batch['start'], 'Asia/Kolkata')
            end_timestamp = convert_to_unixtimestamp(batch['end'], 'Asia/Kolkata')
            
            param_dict = {
                'interval': interval,
                'start_time': start_timestamp,
                'end_time': end_timestamp
            }
            
            result.append(param_dict)
            
            if debug:
                print(f"   - Batch {i+1}: {batch['start']} -> {start_timestamp}")
                print(f"   - Batch {i+1}: {batch['end']} -> {end_timestamp}")
            
            logger.debug(f"Converted batch: {batch['start']} -> {start_timestamp}, {batch['end']} -> {end_timestamp}")
            
        except (DateTimeValidationError, ValueError) as e:
            error_msg = f"Timestamp conversion failed for batch {batch}: {str(e)}"
            if debug:
                print(f"❌ [DEBUG] {error_msg}")
            logger.error(f"Failed to convert timestamps for batch {batch}: {str(e)}")
            raise ValueError(error_msg) from e
    
    if debug:
        print(f"✅ [DEBUG] Successfully generated {len(result)} parameter sets with Unix timestamps")
    
    logger.info(f"Generated {len(result)} parameter sets with Unix timestamps")
    return result

def generate_live_parameters(interval: int, debug: bool = False):
    """
    Generate parameters for live intervals using today's date and a fixed time window.

    Args:
        interval (int): Candle interval in minutes.
        debug (bool): Enable debug output

    Returns:
        dict: Parameters dictionary from generate_parameters function.

    Raises:
        ValueError: If interval is not supported.
    """
    if debug:
        print(f"📡 [DEBUG] Generating live parameters for interval: {interval}")
    
    if interval not in SUPPORTED_LIVE_INTERVALS:
        error_msg = f"Unsupported interval: {interval}. Supported intervals are: {SUPPORTED_LIVE_INTERVALS}"
        if debug:
            print(f"❌ [DEBUG] {error_msg}")
        raise ValueError(error_msg)
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    start_date_str = f"{today_str}"
    end_date_str = f"{today_str}"
    
    if debug:
        print(f"📡 [DEBUG] Using today's date: {today_str}")
        print(f"📡 [DEBUG] Calling generate_parameters with live parameters...")

    return generate_parameters(
        interval=interval,
        lookback=None,
        start_date=start_date_str,
        end_date=end_date_str,
        debug=debug
    )

