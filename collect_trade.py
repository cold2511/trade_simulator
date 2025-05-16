import asyncio
import websockets
import json
import csv
from datetime import datetime

async def collect_tcsv(duration_sec,filename='okx_trades.csv'):
    url="wss://ws.okx.com:8443/ws/v5/public"
    subscribe_msg={
        "op":"subscribe",
        "args":[
            {
                "channel":"trades",
                "instId":"BTC-USDT"
            }
        ]
    }


    print(f"Collecting live trades for {duration_sec} seconds...")
    start_time=datetime.now()

    with open(filename,mode='w',newline='')as file:
        writer=csv.writer(file)
        writer.writerow(["timestamp","side","price","size","trade_id"])

        async with websockets.connect(url) as ws:
            await ws.send(json.dumps(subscribe_msg))

            while(datetime.now()-start_time).seconds< duration_sec:
                try:
                    msg=await asyncio.wait_for(ws.recv(),timeout=5)
                    data=json.loads(msg)

                    if "data" in data:
                        for trade in data["data"]:
                            writer.writerow([
                                trade.get("ts"),
                                trade.get("side"),
                                trade.get("px"),
                                trade.get("sz"),
                                trade.get("tradeId")
                            ])

                except asyncio.TimeoutError:
                    continue
    print("data saved")
if __name__=="__main__":
  asyncio.run(collect_tcsv(duration_sec=60))

