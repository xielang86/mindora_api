from enum import Enum
from typing import Optional

class SleepStateType(Enum):
    PREPARE = ("准备", 1)
    POSTURE = ("身姿", 2)
    BREATHING = ("呼吸", 3)
    RELAX_1 = ("放松-1", 4)
    RELAX_2 = ("放松-2", 5)
    RELAX_3 = ("放松-3", 6)

    SLEEP_READY = ("入睡", 10)
    LIGHT_SLEEP = ("浅睡", 11)
    DEEP_SLEEP = ("深睡", 12)
    
    STOP = ("停止", 13)
    
    # 异常状态
    USING_PHONE = ("玩手机", 400)
    SITTING_UP = ("坐起", 401)
    LEAVING = ("离开", 402)

    def __init__(self, name: str, order: int):
        self._name = name
        self._order = order
    
    @property
    def name_cn(self) -> str:
        return self._name
    
    @property
    def order(self) -> int:
        return self._order

    def is_abnormal(self) -> bool:
        """判断当前状态是否为异常状态"""
        return self.order >= self.USING_PHONE.order

    @classmethod
    def get_next_state(cls, scene_seq: int) -> Optional['SleepStateType']:
        if scene_seq >= cls.SLEEP_READY.order and scene_seq < cls.USING_PHONE.order:
            for state in cls:
                if state.order == scene_seq:
                    return state

        if scene_seq < cls.SLEEP_READY.order:    
            next_order = min(scene_seq + 1, cls.RELAX_3.order)
            for state in cls:
                if state.order == next_order:
                    return state
        return None