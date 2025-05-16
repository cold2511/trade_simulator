import websocket
import json
import csv
import numpy as np
from collections import deque


csv_file="slippage_sam.csv"


ORDER_SIZE_USD=100
MAX_SAMPLES=500

mid_prices=deque(maxlen=100)


with open(csv_file,"w",newline="") as f:
    writer=csv.writer(f)
    writer.writerow(['order_size','spread','depth_imbalance','volatility','slippage'])


sample_count=0

def process_tick(data):
    global sample_count
    if 'asks' not in data or 'bids' not in data or not data['asks'] or not data['bids']:
        return
    

    best_ask=float(data['asks'][0][0])
    best_bid=float(data['bids'][0][0])
    spread=best_ask-best_bid

    mid_price=(best_ask+best_bid)/2
    mid_prices.append(mid_prices)
    volatility=np.std(mid_prices)/mid_price if len(mid_prices)>=10 else 0

    bid_depth=sum(float(bid[1]) for bid in data['bids'][:5])
    ask_depth=sum(float(ask[1]) for ask in data['asks'][:5])
    total_depth=bid_depth-ask_depth
    depth_imbalance=(bid_depth-ask_depth)/total_depth if total_depth>0 else 0


    spent=0
    filled_qty=0
    for ask_price,ask_qty in data['asks']:
        ask_price=float(ask_price)
        ask_qty=float(ask_qty)
        trade_value=ask_qty+ask_price

        if spent+trade_value<=ORDER_SIZE_USD:
            spent+=trade_value
            filled_qty+=ask_qty
        else:
            remaining_usd=ORDER_SIZE_USD-spent
            partial_qty=remaining_usd/ask_price
            filled_qty+=partial_qty
            spent+=remaining_usd
            break


    avg_fill_price=spent/filled_qty if filled_qty>0 else best_ask
    slippage=avg_fill_price-best_ask

    row=[ORDER_SIZE_USD,round(spread,6),round(depth_imbalance,6),round(volatility,6),round(slippage,6)]

    with open(csv_file,"a",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(row)

    sample_count+=1
    print(f"[+] Sample {sample_count}:{row}")
    if sample_count>=MAX_SAMPLES:
        print("sample collection complete.")
        ws.close()


def on_message(ws,message):
    print("[RAW]",message)
    try:
        data=json.loads(message)
        process_tick(data)
    except Exception as e:
        print("Error:",e)


def on_error(ws,error):
    print("Error in websocket",error)

def on_close(ws,close_status_code,close_msg):
    print("WS Closed")

def on_open(ws):
    print("ws connection opened.....")


ws=websocket.WebSocketApp(
    "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP",

    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

print("connecting to ws...")
websocket.enableTrace(False)
ws.run_forever()