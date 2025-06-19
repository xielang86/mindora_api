import asyncio
from collections import defaultdict, deque
from aivc.config.config import L
from aivc.sop.common.alert import AlertLevel, SleepAlert
from aivc.sop.common.common import Actions,AbNormalState
from typing import Optional, Tuple

class AlertStateManager:
    """异常状态静音管理器 - 单例模式"""
    _instance = None
    _initialized = False
    MAX_HISTORY = 20  # 状态历史记录最大长度
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._lock = asyncio.Lock()
            self._states = defaultdict(lambda: {
                "normal_state": None, 
                "history": deque(maxlen=self.MAX_HISTORY),
                "last_alert_level": None
            })
            self._initialized = True
            L.debug(f"AlertStateManager初始化")

    async def update_state(self, conversation_id: str, state: str) -> Tuple[Optional[AlertLevel], Optional[Actions]]:
        """
        更新状态并检查是否触发告警
        
        Args:
            conversation_id: 会话ID
            state: 当前状态
            
        Returns:
            Tuple[Optional[AlertLevel], Optional[Actions]]: 
                如果触发告警，返回(告警级别, 对应动作配置)；否则返回(None, None)
        """
        if not state:
            return None, None
            
        async with self._lock:
            conversation_data = self._states[conversation_id]
            
            # 直接记录状态，不进行时间判断
            conversation_data["history"].append(state)
            
            # 将状态历史转换为简化表示
            L.debug(f"AlertStateManager 会话 {conversation_id} 记录状态: {state}")
            
            # 检查状态序列是否触发告警
            alert_level = self._check_state_pattern(conversation_id)
            if alert_level:
                conversation_data["last_alert_level"] = alert_level
                L.debug(f"AlertStateManager 会话 {conversation_id} 触发告警: {alert_level}")
                
                # 创建对应的动作配置
                actions = self._create_alert_actions(alert_level)
                return alert_level, actions
            
            # 如果是正常状态，更新normal_state
            if AbNormalState.is_abnormal(state):
                old_state = conversation_data["normal_state"]
                
                if old_state != state:
                    L.debug(f"AlertStateManager update_state 会话 {conversation_id} 状态从 {old_state} 变为 {state}")
                    conversation_data["normal_state"] = state
                    
            return None, None
            
    def _create_alert_actions(self, level: AlertLevel) -> Actions:
        """
        根据告警级别创建相应的动作配置
        
        Args:
            level: 告警级别
            
        Returns:
            Actions: 告警动作配置
        """
        try:
            return SleepAlert.create_alert_actions(level)
        except Exception as e:
            L.error(f"创建告警动作配置失败: {e}")
            return None
        
    def _check_state_pattern(self, conversation_id: str) -> Optional[AlertLevel]:
        """检查状态历史是否匹配规则表中的模式"""
        conversation_data = self._states[conversation_id]
        history = list(conversation_data["history"])
        
        if len(history) < 2:
            return None
        
        # 将状态历史转换为简化表示
        pattern = []
        for state in history:
            if state == AbNormalState.USING_PHONE:
                pattern.append("Y")
            elif state == AbNormalState.SITTING_UP:
                pattern.append("J")
            elif state == AbNormalState.LEAVING:
                pattern.append("o")
            else:
                pattern.append("N")  # 其他异常状态
        
        # 从最新状态开始回溯判断
        last_state = pattern[-1] if pattern else None
        if not last_state:
            return None
            
        pattern_str = ''.join(pattern)
        L.debug(f"状态模式: {pattern_str}, 最新状态: {last_state}")
        
        # 计算连续的相同状态
        # 从最新状态开始回溯计算连续状态数
        def count_consecutive(state_char):
            count = 0
            for i in range(len(pattern)-1, -1, -1):
                if pattern[i] == state_char:
                    count += 1
                else:
                    break
            return count
        
        # 计算各种状态的连续次数
        y_consecutive = count_consecutive("Y")  # 玩手机连续次数
        j_consecutive = count_consecutive("J")  # 坐起连续次数
        o_consecutive = count_consecutive("o")  # 离开连续次数
        n_consecutive = count_consecutive("N")  # 正常状态连续次数
        
        L.debug(f"连续状态次数: Y={y_consecutive}, J={j_consecutive}, o={o_consecutive}, N={n_consecutive}")
        
        # 状态判断结果，初始为None
        alert_level = None
        
        # 根据最新状态和连续次数，判断是否触发告警级别
        if last_state == "o":
            # L4 级别: "ooo"(离开画面)
            if o_consecutive >= 3:
                alert_level = AlertLevel.L4
        
        elif last_state == "Y":
            # 获取Y状态的统计信息
            recent_pattern_8 = pattern[-8:] if len(pattern) >= 8 else pattern
            recent_pattern_6 = pattern[-6:] if len(pattern) >= 6 else pattern
            y_count_8 = recent_pattern_8.count("Y")
            y_count_6 = recent_pattern_6.count("Y")
            
            # L3 级别: "YY YY YY YY"(干扰行为)
            if y_count_8 >= 8:
                alert_level = AlertLevel.L3
            # L2 级别: "YYY YYY"(持续活动)
            elif y_count_6 >= 6:
                alert_level = AlertLevel.L2
            # L1 级别: "YYY"(短暂活动)
            elif y_consecutive >= 3:
                alert_level = AlertLevel.L1
        
        elif last_state == "J":
            # L3 级别: "JJJJ"(跳出行为)
            if j_consecutive >= 4:
                alert_level = AlertLevel.L3
            # L1 级别: "JJ"(短暂跳出)
            elif j_consecutive >= 2:
                alert_level = AlertLevel.L1
        
        elif last_state == "N":
            # NORMAL: "NNNN"(完全恢复)
            if n_consecutive >= 4:
                alert_level = AlertLevel.NORMAL
            # L0 级别: "NN"(等待恢复)
            elif n_consecutive >= 2 and (y_consecutive>0 or j_consecutive>0 or o_consecutive>0):
                alert_level = AlertLevel.L0
        
        return alert_level

    async def clear_conversation(self, conversation_id: str) -> None:
        """清除会话数据"""
        async with self._lock:
            if conversation_id in self._states:
                del self._states[conversation_id]
