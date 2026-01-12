import asyncio

from napcat.client import NapCatClient


async def forward_ws_connection(url: str) -> None:
    async with NapCatClient(url) as client:
        async for event in client.events():
            print(event)


async def main():
    await forward_ws_connection("ws://localhost:3001")


asyncio.run(main())
