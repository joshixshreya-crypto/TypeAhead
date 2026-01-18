import asyncio
from collections import deque


class AsyncQueue:
    def __init__(self):
        self.items = deque()

    async def put(self,item ):
        self.items.append(item)

    async def get(self):
        while(not self.items):
            await asyncio.sleep(0.1)
        a = self.items.popleft()
        return a