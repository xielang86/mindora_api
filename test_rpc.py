import asyncio
from aivc.chat.sleep_dect_rpc import RpcClient

async def main():
    for i in range(3):
        client = await RpcClient.get_connected_client()
        print(f"第 {i+1} 次获取的 RPC Client: {client}")

if __name__ == "__main__":
    asyncio.run(main())
