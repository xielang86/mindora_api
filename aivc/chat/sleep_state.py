import asyncio
from collections import defaultdict
from aivc.common.sleep_common import SceneExecStatus
from aivc.config.config import L
from aivc.common.sleep_config import StateType 
from typing import Optional
import time
from aivc.common.sleep_common import EyeStatus, BodyPoseType
from dataclasses import dataclass


class StateManager:
    """管理状态转换的类"""
    _instance = None
    _initialized = False 

    def __init__(self):
        if not self._initialized:
            self._state_cache = {}
            self._lock = asyncio.Lock()
            self._initialized = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def update_state_by_exec_status(
            self, conversation_id: str, 
            scene_exec_status: SceneExecStatus) -> Optional[StateType]:
        async with self._lock:
            rsp_state = await self.get_current_state(conversation_id)
            if scene_exec_status and scene_exec_status.scene_seq < (StateType.SLEEP_READY.order - 1) and scene_exec_status.status == "COMPLETED":
                rsp_state = StateType.get_next_state(scene_exec_status.scene_seq)
                L.debug(f"update_state_by_exec_status 会话 {conversation_id} scene_exec_status:{scene_exec_status} COMPLETED, 更新状态为 {rsp_state}")
                await self.set_state(conversation_id, rsp_state)
            
            L.debug(f"update_state_by_exec_status 更新会话 {conversation_id} scene_exec_status:{scene_exec_status} 的状态为 {rsp_state}")
            return rsp_state
    
    async def get_current_state(self, conversation_id: str) -> Optional[StateType]:
        return self._state_cache.get(conversation_id, StateType.PREPARE)
    
    async def set_state(self, conversation_id: str, state: StateType) -> None:
        if state is not None and not state.is_abnormal():
            L.debug(f"set_state 设置会话 {conversation_id} 的状态为 {state.name}")
            self._state_cache[conversation_id] = state
        else:
            L.error(f"set_state 无法设置会话 {conversation_id} 的状态为 state：{state}")

class SleepMonitor:
    _instance = None
    _initialized = False
    
    # 正式300秒
    # 测试600秒
    def __init__(self, sleep_threshold: int = 600):
        if not self._initialized:
            self._sleep_start_times = {}  # 记录开始计时的时间戳
            self._sleep_states = {}
            self._lock = asyncio.Lock()
            self.sleep_threshold = sleep_threshold
            self._initialized = True
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def check_sleep_condition(self, 
            conversation_id: str, 
            eye_status: str, 
            lie_status: str, 
            current_state: StateType) -> None:
        abnormal_states = [StateType.USING_PHONE, StateType.SITTING_UP, StateType.LEAVING]
        
        # 移除这里的锁,避免嵌套锁
        if (eye_status == EyeStatus.Closed.value and lie_status == BodyPoseType.Lie.value and 
            current_state not in abnormal_states):
            await self._start_sleep_timer(conversation_id)
            L.debug(f"SleepMonitor _start_sleep_timer 会话 {conversation_id} 睡眠条件满足 eye_status:{eye_status} lie_status:{lie_status} current_state:{current_state}")
        else:
            await self._cancel_sleep_timer(conversation_id)
            L.debug(f"SleepMonitor _cancel_sleep_timer 会话 {conversation_id} 睡眠条件不满足 eye_status:{eye_status} lie_status:{lie_status} current_state:{current_state}")

    async def _start_sleep_timer(self, conversation_id: str) -> None:
        async with self._lock:
            # 记录开始睡眠的时间
            if conversation_id not in self._sleep_start_times:
                self._sleep_start_times[conversation_id] = time.time()
                L.debug(f"SleepMonitor 会话 {conversation_id} 开始睡眠计时，记录开始时间: {self._sleep_start_times[conversation_id]}")
            
            # 检查是否已经达到睡眠阈值
            await self._check_sleep_threshold(conversation_id)

    async def _check_sleep_threshold(self, conversation_id: str) -> None:
        """检查是否达到睡眠阈值"""
        if conversation_id not in self._sleep_start_times:
            return
            
        current_time = time.time()
        sleep_start_time = self._sleep_start_times[conversation_id]
        elapsed_time = current_time - sleep_start_time
        
        if elapsed_time >= self.sleep_threshold and not self._sleep_states.get(conversation_id, False):
            self._sleep_states[conversation_id] = True
            L.info(f"SleepMonitor 会话 {conversation_id} 进入睡眠状态，已经持续 {elapsed_time:.2f} 秒")

    async def _cancel_sleep_timer(self, conversation_id: str) -> None:
        async with self._lock:
            # 删除开始睡眠的时间记录
            if conversation_id in self._sleep_start_times:
                del self._sleep_start_times[conversation_id]
                
            if conversation_id in self._sleep_states:
                del self._sleep_states[conversation_id]
                L.debug(f"SleepMonitor 会话 {conversation_id} 取消睡眠计时并重置状态")

    async def is_sleeping(self, conversation_id: str) -> bool:
        async with self._lock:
            # 先检查是否已经标记为睡眠状态
            is_sleep = self._sleep_states.get(conversation_id, False)
            
            # 如果尚未标记为睡眠，但存在开始时间，则检查是否已达到阈值
            if not is_sleep and conversation_id in self._sleep_start_times:
                await self._check_sleep_threshold(conversation_id)
                is_sleep = self._sleep_states.get(conversation_id, False)
                
            L.info(f"SleepMonitor 会话 {conversation_id} is_sleep:{is_sleep}")
            return is_sleep

    async def interrupt_sleep(self, conversation_id: str) -> None:
        await self._cancel_sleep_timer(conversation_id)
        L.debug(f"SleepMonitor interrupt_sleep 会话 {conversation_id} 睡眠被中断")

@dataclass
class AbnormalTimerInfo:
    last_reported: float  # 上次报告时间戳
    report_count: int  # 报告次数统计

class AbnormalStateManager:
    """异常状态静音管理器 - 单例模式"""
    _instance = None
    _initialized = False
    MAX_REPORTS = 2  # 同一状态下最大报告次数
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, mute_duration: int = 60):
        if not self._initialized:
            self._lock = asyncio.Lock()
            self._states = defaultdict(lambda: {"normal_state": None, "timers": {}})
            self.mute_duration = mute_duration
            self._initialized = True
            L.debug(f"AbnormalStateManager初始化: mute_duration={mute_duration}")

    @property
    def mute_duration(self) -> int:
        return self._mute_duration

    @mute_duration.setter
    def mute_duration(self, value: int):
        self._mute_duration = max(1, value)  # 确保静音时长至少为1秒

    async def update_state(self, conversation_id: str, state: StateType) -> None:
        if not state or state.is_abnormal():
            return
            
        async with self._lock:
            conversation_data = self._states[conversation_id]
            old_state = conversation_data["normal_state"]
            
            if old_state != state:
                L.debug(f"AbnormalStateManager update_state 会话 {conversation_id} 状态从 {old_state} 变为 {state}, 清空异常状态计时器")
                conversation_data["normal_state"] = state
                conversation_data["timers"].clear()

    async def should_report_abnormal(self, 
            conversation_id: str,
            abnormal_state: StateType) -> bool:
        if not abnormal_state.is_abnormal():
            return False
            
        async with self._lock:
            conversation_data = self._states[conversation_id]
            current_state = conversation_data["normal_state"]
            
            # 如果当前状态已经到达或超过SLEEP_READY,不再触发异常
            if current_state and current_state.order >= StateType.SLEEP_READY.order:
                return False
                
            now = time.time()
            timers = conversation_data["timers"]
            
            # 获取或初始化计时器信息
            timer_info = timers.get(abnormal_state)
            if timer_info is None:
                timer_info = AbnormalTimerInfo(last_reported=0, report_count=0)
                timers[abnormal_state] = timer_info
            
            # 检查报告次数是否已达上限
            if timer_info.report_count >= self.MAX_REPORTS:
                L.debug(f"AbnormalStateManager should_report_abnormal 会话 {conversation_id} 异常状态 {abnormal_state} 已达到最大报告次数 {self.MAX_REPORTS}")
                return False
            
            # 如果计时器已过期
            if now - timer_info.last_reported >= self.mute_duration:
                timer_info.last_reported = now
                timer_info.report_count += 1
                L.debug(f"AbnormalStateManager should_report_abnormal 会话 {conversation_id} 异常状态 {abnormal_state} 可以报告, 上次报告时间: {timer_info.last_reported}, 当前报告次数: {timer_info.report_count}")
                return True
                
            return False

    async def clear_conversation(self, conversation_id: str) -> None:
        async with self._lock:
            if conversation_id in self._states:
                del self._states[conversation_id]
