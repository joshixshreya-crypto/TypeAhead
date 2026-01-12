import asyncio
import time
from dotenv import load_dotenv
from redis_stream import create_consumer_group
from message_worker import message_worker
from redis_client import redis_client

load_dotenv()

async def start_worker():
    print("Starting worker initialization...")
    
    # Wait for Redis to be ready
    max_retries = 5
    for i in range(max_retries):
        try:
            redis_client.ping()
            print(f"Redis is ready!")
            break
        except Exception as e:
            print(f"Waiting for Redis... (attempt {i+1}/{max_retries})")
            await asyncio.sleep(2)
    else:
        print("Redis not available after retries")
        return
    
    # Create consumer group
    try:
        create_consumer_group()
    except Exception as e:
        print(f"Failed to create consumer group: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("🔄 Starting message worker as background task...")
    # Run worker as background task without awaiting
    asyncio.create_task(message_worker())

    
    print("✅ Worker startup initiated")
