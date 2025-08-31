import asyncio
import socketio
import aiohttp
from utils import log

sio = socketio.AsyncClient()

ENEMY_URL = "http://localhost:8989/api/enemies"
POLL_INTERVAL_SEC = 1
TARGET_UUIDS = {19276: "粉猪", 19277: "风猪"}

on_monster_alive = None  # 回调函数
on_not_monster_alive = None  # 回调函数
on_monster_dead = None  # 回调函数


async def listen():
    async with aiohttp.ClientSession() as session:
        targethp = 0
        while True:
            async with session.get(ENEMY_URL) as response:
                if response.status != 200:
                    log(f"GET {ENEMY_URL} -> HTTP {response.status}")
                    return
                data = await response.json(content_type=None)
                target = data.get('enemy', {})
                if '19276' in target.keys():
                    #丢包
                    if targethp == target['19276']['hp'] and targethp<1000:
                        if callable(on_not_monster_alive):
                            on_not_monster_alive()
                    else:
                        targethp = target['19276']['hp']
                        if callable(on_monster_alive):
                            on_monster_alive()
                elif '19277' in target.keys():
                    if targethp == target['19277']['hp'] and targethp<1000:
                        if callable(on_not_monster_alive):
                            on_not_monster_alive()
                    else:
                        targethp = target['19277']['hp']
                        if callable(on_monster_alive):
                            on_monster_alive()
                else:
                    targethp = 0
                    if callable(on_not_monster_alive):
                        on_not_monster_alive()
            await asyncio.sleep(POLL_INTERVAL_SEC)

def set_monster_alive_callback(func):
    global on_monster_alive
    on_monster_alive = func

def set_not_monster_alive_callback(func):
    global on_not_monster_alive
    on_not_monster_alive = func

def set_monster_dead_callback(func):
    global on_monster_dead
    on_monster_dead = func

if __name__ == '__main__':
    asyncio.run(listen())
