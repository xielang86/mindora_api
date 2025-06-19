from enum import Enum
from typing import Optional

class Mindfulness1StateType(Enum):
    PREPARE = ("准备", 1)
    MEDITATION_1 = ("冥想1", 2)
    MEDITATION_3 = ("冥想3", 3)
    MEDITATION_4 = ("冥想4", 4) # Corrected typo from MEDitation_4
    MEDITATION_5 = ("冥想5", 5)
    MEDITATION_6 = ("冥想6", 6)
    MEDITATION_7 = ("冥想7", 7)
    MEDITATION_8 = ("冥想8", 8)
    MEDITATION_9 = ("冥想9", 9)
    MEDITATION_10 = ("冥想10", 10)
    MEDITATION_11 = ("冥想11", 11)
    END = ("结束", 12)
    
    def __init__(self, name: str, order: int):
        self._name = name
        self._order = order
    
    @property
    def name_cn(self) -> str:
        return self._name
    
    @property
    def order(self) -> int:
        return self._order

    @classmethod
    def get_next_state(cls, scene_seq: int) -> Optional['Mindfulness1StateType']:
        """根据当前场景序号获取下一个状态"""
        if scene_seq >= cls.END.order: # 如果当前是END状态或之后（理论上不应发生），则没有下一个状态
            return None
            
        next_order = scene_seq + 1
        for state in cls:
            if state.order == next_order:
                return state
        return None
