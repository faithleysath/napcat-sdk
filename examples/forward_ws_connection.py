import asyncio

from websockets.asyncio.client import connect as ws_connect

from napcat.connection import Connection


async def forward_ws_connection(url: str) -> None:
    async with ws_connect(url) as ws:
        async with Connection(ws) as conn:
            async for event in conn.events():
                print(event)


async def main():
    await forward_ws_connection("ws://localhost:3001")


asyncio.run(main())
