import os 
import sys
# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import (
    data_to_dataframe,
    validate_datetime_format,
    convert_to_unixtimestamp,
    validate_parameters,
    create_batches,
    generate_parameters,
    generate_live_parameters,
)

print("=" * 60)
print("🌟 TESTING GROWFIN UTILS MODULE FUNCTIONS 🌟")
print("=" * 60)

# === Test 1: validate_datetime_format ===
print("\n=== Test 1: validate_datetime_format ===")
try:
    dt = validate_datetime_format("2024-01-15")
    print(f"✅ Parsed DateTime: {dt}")
except Exception as e:
    print(f"❌ Error: {e}")

# === Test 2: convert_to_unixtimestamp ===
print("\n=== Test 2: convert_to_unixtimestamp ===")
try:
    ts = convert_to_unixtimestamp("2024-01-15 09:30", "Asia/Kolkata")
    print(f"✅ Unix Timestamp (ms): {ts}")
except Exception as e:
    print(f"❌ Error: {e}")

# === Test 3: validate_parameters ===
print("\n=== Test 3: validate_parameters (interval=15, lookback=30) ===")
try:
    validate_parameters(interval_minutes=15, lookback_days=30, debug=True)
    print("✅ Parameters are valid")
except Exception as e:
    print(f"❌ Error: {e}")

# === Test 4: create_batches (lookback mode) ===
print("\n=== Test 4: create_batches (interval=15, lookback=30) ===")
try:
    batches = create_batches(interval_minutes=15, lookback_days=30, debug=True)
    print(f"✅ Batches Created: {len(batches)}")
    print(f"📦 Sample Batch: {batches[0]}")
except Exception as e:
    print(f"❌ Error: {e}")

# === Test 5: generate_parameters ===
print("\n=== Test 5: generate_parameters (interval=15, lookback=30) ===")
try:
    params = generate_parameters(interval=15, lookback=30, start_date=None, end_date=None, debug=True)
    print(f"✅ Generated Parameters: {len(params)}")
    print(f"🧾 Sample Parameter: {params[0]}")
except Exception as e:
    print(f"❌ Error: {e}")

# === Test 6: generate_live_parameters ===
print("\n=== Test 6: generate_live_parameters (interval=15) ===")
try:
    live_params = generate_live_parameters(interval=15, debug=True)
    print(f"✅ Live Parameters: {live_params}")
except Exception as e:
    print(f"❌ Error: {e}")

# === Test 7: data_to_dataframe ===
print("\n=== Test 7: data_to_dataframe ===")
sample_api_data = {
    "candles": [
        [1705295400, 2500.0, 2550.0, 2490.0, 2540.0, 12000],
        [1705306200, 2540.0, 2560.0, 2520.0, 2555.0, 15000],
    ]
}
try:
    df = data_to_dataframe(sample_api_data)
    print(f"✅ DataFrame Created with {len(df)} rows")
    print(df.head())
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ FINISHED ALL TESTS")
print("=" * 60)
