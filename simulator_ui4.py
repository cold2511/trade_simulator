import tkinter as tk
from tkinter import ttk
import time
import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler
import websocket
import json
import threading

# Load models and scalers
slippage_model = joblib.load("lin_slip_model.pkl")
# scaler_slippage = joblib.load("slippage_scaler.pkl")
log_model = joblib.load("mak_tak_log_model.pkl")
scaler_log = joblib.load("scaler.pkl")

# simplified version of Almgren-Chriss model
def calculate_market_impact(quantity, volatility,T=1.0,eta=0.142,gamma=2.5e-6):
    v = quantity / T  # trading rate
    temp_impact = eta * v
    perm_impact = 0.5 * gamma * quantity
    total_impact = temp_impact + perm_impact
    return total_impact

def calculate_fees(quantity, fee_rate=0.001):
    return quantity * fee_rate

# Real-time Orderbook Data
orderbook_data = {"asks": [], "bids": [], "timestamp": ""}

# WebSocket listener
def on_message(ws, message):
    data = json.loads(message)
    orderbook_data["asks"] = data.get("asks", [])
    orderbook_data["bids"] = data.get("bids", [])
    orderbook_data["timestamp"] = data.get("timestamp", "")
    if app:
        app.update_latency()

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connection opened")

# Start WebSocket in background thread
def start_websocket():
    ws = websocket.WebSocketApp(
        "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever()

ws_thread = threading.Thread(target=start_websocket)
ws_thread.daemon = True
ws_thread.start()

# GUI Application
class TradeSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GoQuant Trade Simulator")

        self.input_frame = ttk.LabelFrame(root, text="Input Parameters")
        self.input_frame.grid(row=0, column=0, padx=10, pady=10)

        self.output_frame = ttk.LabelFrame(root, text="Output Parameters")
        self.output_frame.grid(row=0, column=1, padx=10, pady=10)

        # Inputs
        self.asset_label = ttk.Label(self.input_frame, text="Asset (e.g. BTC-USDT)")
        self.asset_label.grid(row=0, column=0)
        self.asset_entry = ttk.Entry(self.input_frame)
        self.asset_entry.insert(0, "BTC-USDT")
        self.asset_entry.grid(row=0, column=1)

        self.qty_label = ttk.Label(self.input_frame, text="Quantity (USD)")
        self.qty_label.grid(row=1, column=0)
        self.qty_entry = ttk.Entry(self.input_frame)
        self.qty_entry.insert(0, "100")
        self.qty_entry.grid(row=1, column=1)

        self.vol_label = ttk.Label(self.input_frame, text="Volatility")
        self.vol_label.grid(row=2, column=0)
        self.vol_entry = ttk.Entry(self.input_frame)
        self.vol_entry.insert(0, "0.02")
        self.vol_entry.grid(row=2, column=1)

        self.fee_label = ttk.Label(self.input_frame, text="Fee Tier")
        self.fee_label.grid(row=3, column=0)
        self.fee_entry = ttk.Entry(self.input_frame)
        self.fee_entry.insert(0, "0.001")
        self.fee_entry.grid(row=3, column=1)

        self.calc_btn = ttk.Button(self.input_frame, text="Calculate", command=self.calculate)
        self.calc_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Outputs
        self.slippage_label = ttk.Label(self.output_frame, text="Expected Slippage:")
        self.slippage_label.grid(row=0, column=0)
        self.slippage_val = ttk.Label(self.output_frame, text="-")
        self.slippage_val.grid(row=0, column=1)

        self.fee_val_label = ttk.Label(self.output_frame, text="Expected Fees:")
        self.fee_val_label.grid(row=1, column=0)
        self.fee_val = ttk.Label(self.output_frame, text="-")
        self.fee_val.grid(row=1, column=1)

        self.impact_label = ttk.Label(self.output_frame, text="Market Impact:")
        self.impact_label.grid(row=2, column=0)
        self.impact_val = ttk.Label(self.output_frame, text="-")
        self.impact_val.grid(row=2, column=1)

        self.net_label = ttk.Label(self.output_frame, text="Net Cost:")
        self.net_label.grid(row=3, column=0)
        self.net_val = ttk.Label(self.output_frame, text="-")
        self.net_val.grid(row=3, column=1)

        self.makertaker_label = ttk.Label(self.output_frame, text="Maker/Taker Proba:")
        self.makertaker_label.grid(row=4, column=0)
        self.makertaker_val = ttk.Label(self.output_frame, text="-")
        self.makertaker_val.grid(row=4, column=1)

        self.latency_label = ttk.Label(self.output_frame, text="Internal Latency:")
        self.latency_label.grid(row=5, column=0)
        self.latency_val = ttk.Label(self.output_frame, text="-")
        self.latency_val.grid(row=5, column=1)

    def update_latency(self):
        self.latency_val.config(text=f"{time.time():.2f} s")

    def calculate(self):
        try:
            start_time = time.time()
            qty = float(self.qty_entry.get())
            vol = float(self.vol_entry.get())
            fee_rate = float(self.fee_entry.get())
            asset = self.asset_entry.get()
            timestamp = int(time.time())

            X_slippage = [[qty, vol, fee_rate, timestamp]]
            slippage = slippage_model.predict(X_slippage)[0]

            X_log = scaler_log.transform([[qty, vol, timestamp]])
            log_proba = log_model.predict_proba(X_log)[0][1]

            impact = calculate_market_impact(qty, vol)
            fees = calculate_fees(qty, fee_rate)
            net_cost = slippage + impact + fees

            self.slippage_val.config(text=f"{slippage:.4f}")
            self.fee_val.config(text=f"{fees:.4f}")
            self.impact_val.config(text=f"{impact:.4f}")
            self.net_val.config(text=f"{net_cost:.4f}")
            self.makertaker_val.config(text=f"{log_proba:.2f}")

            latency = time.time() - start_time
            self.latency_val.config(text=f"{latency:.4f} s")
        except Exception as e:
            print("Error:", e)

# Run the GUI
root = tk.Tk()
app = TradeSimulatorApp(root)
root.mainloop()