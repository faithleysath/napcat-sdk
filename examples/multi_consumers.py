import asyncio

from napcat.client import NapCatClient


# --- 消费者 A：只做简单计数和类型打印 ---
async def consumer_monitor(client: NapCatClient):
    print(">>> [Monitor] 启动: 准备记录日志...")
    count = 0
    async for event in client.events():
        count += 1
        # 模拟日志记录：只关心是什么类型的事件
        print(f"📝 [Monitor] 第 {count} 个事件 | 类型: {event.post_type}")


# --- 消费者 B：模拟业务逻辑（例如只处理消息） ---
async def consumer_logic(client: NapCatClient):
    print(">>> [Logic] 启动: 准备处理业务...")
    async for event in client.events():
        # 模拟业务逻辑：这里简单的打印出事件的详细 repr
        # 注意：这里会和 Monitor 同时收到同一个事件
        if event.post_type == "meta_event":
            print("⚙️  [Logic]   收到心跳/元数据，忽略...")
        else:
            print(f"✨ [Logic]   收到重要事件! {event.post_type}")


async def main():
    # 替换你的 WebSocket 地址
    url = "ws://localhost:3001"

    # 实例化 client
    # 注意：我们把 client 实例传给两个协程，它们共享同一个连接
    client = NapCatClient(url)

    async with client:
        print(f"连接成功: {url}")

        # 使用 asyncio.gather 让两个协程并发运行
        # 它们会分别调用 client.events()，获得各自独立的 Queue
        await asyncio.gather(consumer_monitor(client), consumer_logic(client))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户停止运行。")
