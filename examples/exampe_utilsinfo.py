import os 
import sys
# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils_info import get_search_id, get_growid

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
print("=== Test 5: xyz without debug ===")
result5 = get_search_id("xyz")
print(result5)

print("\n" + "="*50 + "\n")

# Example 6: get invalid data with debug True get search id
print("=== Test 6: xyz with debug ===")
result6 = get_search_id("xyz", debug=True)
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
print("=== Test 11: xyz growid without debug ===")
result11 = get_growid("xyz")
print(result11)

print("\n" + "="*50 + "\n")

# Example 12: get invalid data with debug True get grow id
print("=== Test 12: xyz growid with debug ===")
result12 = get_growid("xyz", debug=True)
print(result12)

print("\n" + "="*60 + "\n")

