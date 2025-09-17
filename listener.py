import asyncio
import aiohttp
from utils import log

TARGET_UUIDS = {19276: "粉猪", 19277: "风猪"}
TARGET_GROUP = ["火焰食人魔","飓风哥布林王","铁牙","小猪·闪闪","小猪·爱","小猪·风","小猪·雷","小猪·火","小猪·水","小猪·土","小猪·木","小猪·光","小猪·暗"]
TARGET_GROUP = ["小猪·闪闪","娜宝·银辉","娜宝·闪闪"]
TARGET_GROUP = ["小猪·爱","小猪·风"]

def find_enemy(enemies, target_group):
        for eid, info in enemies.items():
            for name in target_group:
                if info.get('name') == name:
                    return eid, info
        return None

class EnemyListener:
    def __init__(self, target_group=None):
        self.target_group = target_group if target_group else TARGET_GROUP
        self.on_monster_dead = None
        self.enemy_url = "http://localhost:8989/api/enemies"
        self.poll_interval_sec = 1
        
    def set_monster_dead_callback(self, func):
        self.on_monster_dead = func

    async def listen(self):
        async with aiohttp.ClientSession() as session:
            targethp = 0
            lastHP = -1
            count = 0
            while True:
                async with session.get(self.enemy_url) as response:
                    if response.status != 200:
                        log(f"GET {self.enemy_url} -> HTTP {response.status}")
                        return
                    data = await response.json(content_type=None)
                    enimies = data.get('enemy', {})
                    target = find_enemy(enimies, self.target_group)
                    if target:
                        target = target[1]
                        targethp = target.get('hp', -1)
                        if lastHP != targethp or targethp==target.get('max_hp', 0):
                            log(f"target: {target}")
                    if target and target.get('max_hp', 0)>0:
                        targethp = target.get('hp', -1)
                        if targethp == 0:
                            if callable(self.on_monster_dead):
                                self.on_monster_dead()
                        if lastHP == targethp:
                            # 丢包
                            count +=1
                            if (count > 10 and targethp < 1000) or (count>20):
                                if callable(self.on_monster_dead):
                                    self.on_monster_dead()
                        else:
                            count = 0
                            lastHP = targethp
                    else:
                        if callable(self.on_monster_dead):
                            self.on_monster_dead()
                await asyncio.sleep(self.poll_interval_sec)
