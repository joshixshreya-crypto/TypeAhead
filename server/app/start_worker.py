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
    # asyncio.create_task(run_worker_with_error_handling())

    
    print("✅ Worker startup initiated")

# async def run_worker_with_error_handling():
#     """Wrapper to handle worker errors without crashing the app"""
#     try:
#         await message_worker()
#         print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++message worker started")
#     except Exception as e:
#         print(f"❌ Message worker failed: {e}")
#         import traceback
#         traceback.print_exc()
