from enum import Enum
from typing import Optional

class MindfulnessIntroStateType(Enum):
    MINDFULNESS_INTRO_SPEECH_1 = ("正念介绍第一部分", 1)
    MINDFULNESS_INTRO_SPEECH_2 = ("正念介绍第二部分", 2)
    MINDFULNESS_INTRO_SEQUENCE_END = ("介绍流程结束", 3)
    
    # 异常状态可以根据需要添加
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
        """判断当前状态是否为异常状态"""
        return self.order >= self.USING_PHONE.order

    @classmethod
    def get_next_state(cls, scene_seq: int) -> Optional['MindfulnessIntroStateType']:
        """根据当前场景序号获取下一个状态"""
        if scene_seq >= cls.MINDFULNESS_INTRO_SEQUENCE_END.order:
            return None
            
        if scene_seq < cls.USING_PHONE.order:    
            next_order = scene_seq + 1
            for state in cls:
                if state.order == next_order:
                    return state
        return None
