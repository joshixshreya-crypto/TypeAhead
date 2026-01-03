import asyncio
from redis_stream import create_consumer_group
from message_worker import message_worker

async def start_worker():
    create_consumer_group()
    await message_worker()
    print("success")

if __name__ == "__main__":
    asyncio.run(start_worker())
