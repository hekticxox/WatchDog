import asyncio
import json
import websockets

endpoint = "wss://ws-api-futures.kucoin.com/"
token = "2neAiuYvAU61ZDXANAGAsiL4-iAExhsBXZxftpOeh_55i3Ysy2q2LEsEWU64mdzUOPusi34M_wGoSf7iNyEWJ9Ydq3-ytBNUpIxNZ-GlZJtpNI-2di4Pt9iYB9J6i9GjsxUuhPw3Blq6rhZlGykT3Vp1phUafnulOOpts-MEmEE2LOdtdhZM5tGV5iL_SfjbJBvJHl5Vs9Y=.hEYnaEYp5J29cYFLxrXovw=="  # Replace with your token

async def subscribe(ws, topic, token):
    sub_msg = {
        "id": "1",
        "type": "subscribe",
        "topic": topic,
        "privateChannel": False,
        "response": True,
        "token": token
    }
    await ws.send(json.dumps(sub_msg))

async def main():
    ws_url = f"{endpoint}?token={token}"
    async with websockets.connect(ws_url) as ws:
        await subscribe(ws, "/contractMarket/level2:XBTUSDTM", token)
        async for msg in ws:
            data = json.loads(msg)
            # Only process order book updates
            if data.get("topic") == "/contractMarket/level2:XBTUSDTM" and "data" in data:
                change = data["data"]["change"].split(",")
                price = float(change[0])
                side = change[1]  # "buy" or "sell"
                size = float(change[2])
                print(f"Orderbook update: {side.upper()} {size} @ {price}")
                # Here you can update your in-memory order book, run analytics, etc.

if __name__ == "__main__":
    asyncio.run(main())