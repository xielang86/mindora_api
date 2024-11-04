import asyncio
from typing import List, Dict, Any

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class MessageDict(metaclass=Singleton):
    def __init__(self):
        self.data: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = asyncio.Lock()

    async def insert(self, key: str, value: Dict[str, Any]):
        async with self.lock:
            if key in self.data:
                self.data[key].append(value)
            else:
                self.data[key] = [value]

    async def delete(self, key: str):
        async with self.lock:
            if key in self.data:
                del self.data[key]

    async def query(self, key: str) -> List[Dict[str, Any]]:
        async with self.lock:
            return self.data.get(key, [])