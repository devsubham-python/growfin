# 📈 GrowFin – NSE Stock Data Toolkit

GrowFin is a Python library for accessing **real-time** and **historical** stock data, **corporate events**, and **news** from the **NSE India** exchange using the Groww API (unofficial). It is designed for traders, analysts, and developers who want to programmatically work with Indian stock market data.

---

---

## ⚠️ Disclaimer

This library is not affiliated with Groww. Use at your own risk for educational/research purposes.

---

## 🔧 Installation

```bash
git clone https://github.com/yourusername/growfin.git
cd growfin
pip install -r requirements.txt
pip install .
```

> Requires Python 3.7+

---

## 🚀 Quick Start

```python
from ticker import Ticker

ticker = Ticker("RELIANCE", debug=True)

# Historical candles
history = ticker.history(interval=15, lookback=5)
print(history)

# Live candles for today
live = ticker.live(interval=15)
print(live)

# Company information
ticker.info()

# Corporate events
events = ticker.events()
print(events)

# News
news = ticker.news()
print(news)
```

If the symbol is invalid, `.suggestions` will guide alternatives.

---

## 🧠 Class: `Ticker`

### `Ticker(symbol: str, debug: bool = False)`

Initializes a Ticker object and auto-resolves Groww IDs.

- `symbol` (str): NSE stock symbol (e.g., `"TCS"`, `"RELIANCE"`)
- `debug` (bool): Enable verbose debug output

---

## 📊 Method: `history()`

Fetch historical OHLCV candles.

```python
ticker.history(interval=15, lookback=5, debug=True)
```

**Arguments:**
- `interval` (int): Candle interval in minutes (1, 15, 60, etc.)
- `lookback` (int, optional): Days to go back from today
- `start` (str, optional): Start datetime `'YYYY-MM-DD HH:MM'`
- `end` (str, optional): End datetime `'YYYY-MM-DD HH:MM'`
- `debug` (bool): If `True`, print debug logs

**Returns:**
```python
{
    "data": {"candles": [...]},
    "debug_info": [...],
    "error": [...]
}
```

---

## ⚡ Method: `live()`

Fetch live candles for today.

```python
ticker.live(interval=15, debug=True)
```

**Arguments:**
- `interval` (int): Candle interval in minutes
- `check_trading_day` (bool): Skip weekends if `True`
- `debug` (bool): Show debug logs

**Returns:** Same as `.history()`

---

## 🧾 Method: `info()`

Print company information.

```python
ticker.info(debug=True)
```

**Returns:** None (prints to stdout)

---

## 📅 Method: `events()`

Fetch corporate actions.

```python
ticker.events(debug=True)
```

**Returns:**
```python
{
    "data": {...},
    "debug_info": [...],
    "error": [...]
}
```

---

## 🗞️ Method: `news()`

Get stock-related news.

```python
ticker.news(page=0, size=5, debug=True)
```

**Arguments:**
- `page` (int): Pagination page
- `size` (int): Number of articles per page
- `debug` (bool): Show debug logs

**Returns:** Same format as `.events()`

---
