from enum import Enum
from typing import Optional

class Mindfulness2StateType(Enum):
    PREPARE = ("准备", 1)
    MEDITATION1 = ("冥想1", 2)
    MEDITATION2 = ("冥想2", 3)
    MEDITATION3 = ("冥想3", 4)
    MEDITATION4 = ("冥想4", 5)
    MEDITATION5 = ("冥想5", 6)
    MEDITATION6 = ("冥想6", 7)
    MEDITATION7 = ("冥想7", 8)
    MEDITATION8 = ("冥想8", 9)
    MEDITATION9 = ("冥想9", 10)
    MEDITATION10 = ("冥想10", 11)
    END = ("结束", 12)
    
    USING_PHONE = ("玩手机", 400)
    LEAVING = ("离开", 401)

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
        return self.order >= self.USING_PHONE.order

    @classmethod
    def get_next_state(cls, scene_seq: int) -> Optional['Mindfulness2StateType']:
        if scene_seq >= cls.END.order:
            return None
        if scene_seq < cls.USING_PHONE.order:    
            next_order = scene_seq + 1
            for state in cls:
                if state.order == next_order:
                    return state
        return None
