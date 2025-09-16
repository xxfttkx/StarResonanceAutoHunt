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
TARGET_GROUP = ["火焰食人魔","飓风哥布林王","铁牙","小猪·闪闪","小猪·爱","小猪·风","小猪·雷","小猪·火","小猪·水","小猪·土","小猪·木","小猪·光","小猪·暗"]
TARGET_GROUP = ["小猪·闪闪","小猪·爱","小猪·风","娜宝·银辉","娜宝·闪闪"]

def find_enemy(enemies, target_group):
    for eid, info in enemies.items():
        for name in target_group:
            if info.get('name') == name:
                return eid, info
    return None

async def listen(enemy_names):
    async with aiohttp.ClientSession() as session:
        targethp = 0
        lastHP = -1
        count = 0
        while True:
            async with session.get(ENEMY_URL) as response:
                if response.status != 200:
                    log(f"GET {ENEMY_URL} -> HTTP {response.status}")
                    return
                data = await response.json(content_type=None)
                enimies = data.get('enemy', {})
                target_group = len(enemy_names)>0 and enemy_names or TARGET_GROUP
                # target_group = [enemy_name] if enemy_name else TARGET_GROUP
                target = find_enemy(enimies, target_group)
                if target:
                    target = target[1]
                log(f"target: {target}")
                if target and target.get('max_hp', 0)>0:
                    targethp = target.get('hp', -1)
                    if targethp == 0:
                        if callable(on_monster_dead):
                            on_monster_dead()
                    if lastHP == targethp:
                        # 丢包
                        count +=1
                        if (count > 10 and targethp < 1000) or (count>20):
                            if callable(on_monster_dead):
                                on_monster_dead()
                    else:
                        count = 0
                        lastHP = targethp
                        if callable(on_monster_alive):
                            on_monster_alive()
                else:
                    if callable(on_monster_dead):
                        on_monster_dead()
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
