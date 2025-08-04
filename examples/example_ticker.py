import os 
import sys
## Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ticker import Ticker

ticker = Ticker("reliance")
"""
print("\n" + "="*50 + "\n")
print("\n" + "="*50 + "\n")
print("\n" + "="*50 + "\n")

events = ticker.events(debug=True)
print("gnerating events printing on console logs only if debug=True")
print("\n" + "="*50 + "\n")
print("actural events return values")
print(events)
print("\n" + "="*50 + "\n")
print("\n" + "="*50 + "\n")

news = ticker.news(debug=True)
print("gnerating news printing console logs only if debug=True")
print("\n" + "="*50 + "\n")
print("actural return values")
print(news)
print("\n" + "="*50 + "\n")
print("\n" + "="*50 + "\n")

info = ticker.info(debug=True)
print("gnerating news printing console logs only if debug=True")
print("\n" + "="*50 + "\n")
print("actural return values")
print(info)
print("\n" + "="*50 + "\n")
print("\n" + "="*50 + "\n")

"""

## test news case with debug and without debug ## uncomment to run

"""
print("\n" + "=" * 60)
print("🔵 TEST: ticker.news(debug=True) — Should Print Logs")
print("=" * 60)
news_debug = ticker.news(debug=True)

print("\n" + "=" * 60)
print("🟢 ACTUAL RETURN VALUE (debug=True)")
print("=" * 60)
print(news_debug)

print("\n" + "=" * 60)
print("🔴 TEST: ticker.news(debug=False) — Should NOT Print Logs")
print("=" * 60)
news = ticker.news()

print("\n" + "=" * 60)
print("🟢 ACTUAL RETURN VALUE (debug=False)")
print("=" * 60)
print(news)
"""

## test events case with debug and without debug ##
"""
print("\n" + "=" * 60)
print("🔵 TEST: ticker.events(debug=True) — Should Print Logs")
print("=" * 60)
events_debug = ticker.events(debug=True)

print("\n" + "=" * 60)
print("🟢 ACTUAL RETURN VALUE (debug=True)")
print("=" * 60)
print(events_debug)

print("\n" + "=" * 60)
print("🔴 TEST: ticker.events(debug=False) — Should NOT Print Logs")
print("=" * 60)
events = ticker.events()

print("\n" + "=" * 60)
print("🟢 ACTUAL RETURN VALUE (debug=False)")
print("=" * 60)
print(events)

"""

print("\n" + "=" * 60)
print("🔵 TEST: ticker.events(debug=True) — Should Print Logs")
print("=" * 60)
live_debug = ticker.live(interval=5,debug=True)

print("\n" + "=" * 60)
print("🟢 ACTUAL RETURN VALUE (debug=True)")
print("=" * 60)
print(live_debug)

print("\n" + "=" * 60)
print("🔴 TEST: ticker.events(debug=False) — Should NOT Print Logs")
print("=" * 60)
live = ticker.live(interval=5)

print("\n" + "=" * 60)
print("🟢 ACTUAL RETURN VALUE (debug=False)")
print("=" * 60)
print(live)
