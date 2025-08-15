import asyncio
import socketio
from utils import log

sio = socketio.AsyncClient()

damage_map = {}  # 存 player_id -> 伤害值

on_monster_alive = None  # 回调函数
on_not_monster_alive = None  # 回调函数

@sio.event
async def connect():
    log("连接成功")

@sio.event
async def disconnect():
    log("连接断开")

@sio.on('data')
def on_data(data):
    users = data.get("user", {})
    alive_monster = False
    for player_id, info in users.items():
        total_damage = info.get("total_damage", {})
        damage = total_damage.get("normal", 0)

        old_damage = damage_map.get(player_id, 0)
        if old_damage != damage:
            if damage-old_damage<50 :
                alive_monster = True
            damage_map[player_id] = damage
            # log(f"玩家 {player_id} 造成有效伤害由{old_damage}变更为: {damage} , damage-old_damage<50 = {damage-old_damage<50}")
    if alive_monster:
        # log("场上有神奇生物")
        if callable(on_monster_alive):
            on_monster_alive()  # 调用回调
    else:
        # log("场上无神奇生物")
        if callable(on_not_monster_alive):
            on_not_monster_alive()  # 调用回调
        
# target: 粉-19276 风-19277
async def listen():
    await sio.connect('http://localhost:8989')
    await sio.wait()

def set_monster_alive_callback(func):
    global on_monster_alive
    on_monster_alive = func

def set_not_monster_alive_callback(func):
    global on_not_monster_alive
    on_not_monster_alive = func

if __name__ == '__main__':
    asyncio.run(listen())
