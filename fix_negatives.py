import asyncio
import json
import os
from datetime import datetime, timezone
import websockets
from dotenv import load_dotenv

load_dotenv()

HA_URL = os.getenv("HA_URL", "ws://homeassistant.local:8123/api/websocket")
HA_TOKEN = os.getenv("HA_TOKEN", "")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
START_DATE = datetime.strptime(os.getenv("START_DATE", "01/01/1970"), "%d/%m/%Y").replace(tzinfo=timezone.utc)
END_DATE = datetime.strptime(os.getenv("END_DATE", "31/12/2099"), "%d/%m/%Y").replace(tzinfo=timezone.utc)
msg_id = 0


def next_id():
    global msg_id
    msg_id += 1
    return msg_id


async def send_and_receive(ws, payload):
    payload["id"] = next_id()
    await ws.send(json.dumps(payload))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == payload["id"]:
            return resp


async def fix_negatives():
    if DRY_RUN:
        print("*** DRY RUN MODE - no changes will be applied ***\n")

    async with websockets.connect(HA_URL, max_size=None) as ws:
        await ws.recv()  # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
        auth_resp = json.loads(await ws.recv())
        if auth_resp.get("type") != "auth_ok":
            print(f"Auth failed: {auth_resp}")
            return

        with open("list.txt") as f:
            statistic_ids = [line.strip() for line in f if line.strip()]

        for stat_id in statistic_ids:
            print(f"\n--- {stat_id} ---")
            resp = await send_and_receive(ws, {
                "type": "recorder/statistics_during_period",
                "start_time": "1970-01-01T00:00:00Z",
                "statistic_ids": [stat_id],
                "period": "hour",
            })

            records = resp.get("result", {}).get(stat_id, [])
            if len(records) < 2:
                print("  Not enough records, skipping.")
                continue

            fixed = 0
            for i in range(1, len(records)):
                prev_sum = records[i - 1].get("sum", 0) or 0
                curr_sum = records[i].get("sum", 0) or 0
                delta = curr_sum - prev_sum

                rec_dt = datetime.fromtimestamp(records[i]["start"] / 1000, tz=timezone.utc)
                if rec_dt < START_DATE or rec_dt > END_DATE:
                    continue

                if delta < 0:
                    adjustment = -delta
                    start_time = records[i]["start"]
                    dt = datetime.fromtimestamp(start_time / 1000, tz=timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
                    print(f"  Negative delta at {dt}: {delta:.4f} -> adjustment needed +{adjustment:.4f}")

                    if not DRY_RUN:
                        adj_resp = await send_and_receive(ws, {
                            "type": "recorder/adjust_sum_statistics",
                            "statistic_id": stat_id,
                            "start_time": rec_dt.isoformat(),
                            "adjustment": adjustment,
                            "adjustment_unit_of_measurement": "kWh",
                        })
                        if adj_resp.get("success"):
                            fixed += 1
                        else:
                            print(f"  ERROR: {adj_resp}")
                    else:
                        fixed += 1

            print(f"  {'Would fix' if DRY_RUN else 'Fixed'} {fixed} negative delta(s)." if fixed else "  No negative deltas found.")


if __name__ == "__main__":
    if not HA_TOKEN:
        print("Error: set HA_TOKEN in .env")
        exit(1)
    asyncio.run(fix_negatives())
