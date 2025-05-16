# 📈 High-Performance Crypto Trade Simulator

## 🚀 Project Overview

This is an advanced crypto trade simulator developed as part of the GoQuant recruitment assignment. It connects to OKX exchange via WebSocket to stream real-time L2 order book data, and calculates various trade metrics including slippage, fees, market impact, and more, all in a performance-optimized Python environment.

---

## 🖥️ UI Features

### 📥 Input Panel

- **Exchange**: OKX
- **Spot Asset**: e.g., BTC-USDT-SWAP
- **Order Type**: Market
- **Quantity**: User-defined (~100 USD equivalent)
- **Volatility**: Derived from market data
- **Fee Tier**: Configurable based on OKX docs

### 📤 Output Panel

- **Expected Slippage** (via Linear Regression)
- **Expected Fees** (rule-based)
- **Expected Market Impact** (Almgren-Chriss model)
- **Net Cost** = Slippage + Fees + Market Impact
- **Maker/Taker Proportion** (Logistic Regression)
- **Internal Latency** (per tick)

---

## 🔌 Real-time WebSocket Stream

- **Endpoint**: `wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP`
- **Streaming**: Real-time order book ticks
- **Processing**: Optimized pipeline with per-tick latency tracking

---

## 🧠 Model Implementation

- **Slippage Model**: Linear Regression
- **Maker/Taker Prediction**: Logistic Regression
- **Market Impact**: Almgren-Chriss closed-form equation

---

## 🧪 Model Training Details

### 🔹 Slippage Estimation Model (Linear Regression)

- **Script**: `train_slip.py`
- **Data Source**: `slippage_sam.csv`  
- **Features**:
  - Price
  - Quantity
  - Spread
  - Volatility
- **Target**: Slippage
- **Preprocessing**:
  - StandardScaler
  - Outlier filtering
- **Artifacts**:
  - `lin_slip_model.pkl`
  - `scaler.pkl`

---

### 🔹 Maker/Taker Classification (Logistic Regression)

- **Script**: `log_regre_m_t.py`
- **Data Source**: `okx_trades.csv`
- **Features**:
  - Trade price
  - Mid price
  - Trade size
  - Direction
- **Target**: 0 = Maker, 1 = Taker
- **Heuristics**:
  - Price vs. mid-price for direction labeling
- **Artifact**: `mak_tak_log_model.pkl`

---

## ⚙️ Performance Optimizations

- Async WebSocket handling
- Tick-wise processing latency tracking
- Efficient NumPy-based calculations
- Proper thread-safe updates to UI

---

## 🧾 Submission Requirements (Completed)

- ✅ UI with real-time input/output
- ✅ Trained and integrated ML models
- ✅ Real-time WebSocket integration
- ✅ Internal latency measurement
- ✅ GitHub repository (private)
- ✅ Loom video walkthrough
- ✅ Resume attached
- ✅ Model documentation (this README)

---

## 🛠️ How to Run

```bash
pip install -r requirements.txt
python simulator_ui4.py
```

> **Note:** Use a VPN to connect to OKX WebSocket.

---

## 📩 Confidentiality Notice

This project is submitted strictly for the GoQuant recruitment process and **must not** be made public. Please refrain from uploading this to public repositories or sharing externally.

---
