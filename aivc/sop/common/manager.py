import asyncio
from typing import Optional, Dict, List
from aivc.config.config import L, settings
from aivc.sop.common.common import Actions, SceneExecStatus
from aivc.sop.common.data import load_cn_to_en_mapping, load_and_parse_json, parse_actions, gen_file_name_from_text


class CommandDataManager:
    """管理命令数据缓存的类"""
    _instance = None
    _initialized = False

    def __init__(self):
        if not self._initialized:
            self._command_cache: Dict[str, Dict[str, Actions]] = {}
            self._lock = asyncio.Lock()
            self._initialized = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_command_data(self, command: str) -> tuple[Dict[str, Actions] | None, str | None]:
        """获取命令数据，自动从磁盘加载"""
        # 首先尝试从缓存获取
        actions_dict = await self.get_command_data_cache_only(command)
        if actions_dict:
            return actions_dict, None
        
        # 缓存中没有，从磁盘读取
        L.debug(f"CommandDataManager 缓存中未找到命令数据 {command}，开始从磁盘读取")
        actions_dict, error = await self._load_command_from_disk(command)
        if error:
            return None, error
        
        # 缓存数据
        await self.set_command_data(command, actions_dict)
        return actions_dict, None

    async def get_command_data_cache_only(self, command: str) -> Optional[Dict[str, Actions]]:
        """仅从缓存获取命令数据"""
        async with self._lock:
            actions_dict = self._command_cache.get(command)
            if actions_dict:
                L.debug(f"CommandDataManager 从缓存获取命令数据 {command}，包含 {len(actions_dict)} 个动作")
            else:
                L.debug(f"CommandDataManager 缓存中未找到命令数据 {command}")
            return actions_dict

    async def _load_command_from_disk(self, command: str) -> tuple[Dict[str, Actions] | None, str | None]:
        """从磁盘加载命令数据"""
        cmd_mapping = load_cn_to_en_mapping()
        
        # 反向查找：从英文命令找到对应的中文命令
        cn_command = None
        for cn_key, en_value in cmd_mapping.items():
            if en_value == command:
                cn_command = cn_key
                break
        
        if not cn_command:
            error_msg = f"未找到命令 {command} 对应的中文映射"
            L.error(error_msg)
            return None, error_msg

        file = settings.DATA_DIR + "/" + cn_command + ".json"
        data, error = load_and_parse_json(file)
        if error:
            L.error(error)
            return None, error
     
        actions_dict, error = parse_actions(data)
        if error:
            L.error(error)
            return None, error
        
        # 拼接文件名到 actions_dict 中的每个动作
        for action_index, (process, action) in enumerate(actions_dict.items(), 1):
            if action.voice and action.voice.voices:
                for voice in action.voice.voices:
                    if not hasattr(voice, 'text') or not voice.text:
                        continue
                    voice.filename = gen_file_name_from_text(
                        text=voice.text,
                        english_name=command,
                        action_index=action_index
                    )
        
        return actions_dict, None

    async def set_command_data(self, command: str, actions_dict: Dict[str, Actions]) -> None:
        """存储命令和对应的actions_dict"""
        async with self._lock:
            self._command_cache[command] = actions_dict
            L.debug(f"CommandDataManager 缓存命令数据 {command}，包含 {len(actions_dict)} 个动作")

    async def clear_command_data(self, command: str) -> None:
        """清除指定命令的缓存数据"""
        async with self._lock:
            if command in self._command_cache:
                del self._command_cache[command]
                L.debug(f"CommandDataManager 清除命令数据缓存 {command}")

    async def clear_all_data(self) -> None:
        """清除所有缓存数据"""
        async with self._lock:
            self._command_cache.clear()
            L.debug("CommandDataManager 清除所有命令数据缓存")

    async def get_command_process_data(self, command: str, process: str) -> tuple[Actions | None, int | None, str | None]:
        """根据命令和process获取特定的Actions，返回(action, seq, error)"""
        # 首先获取完整的命令数据
        actions_dict, error = await self.get_command_data(command)
        if error:
            return None, None, error
        
        # 从字典中获取指定的process，同时计算序号
        for seq, (proc_name, action) in enumerate(actions_dict.items(), 1):
            if proc_name == process:
                L.debug(f"CommandDataManager 获取命令 {command} 的 process {process} 数据成功，seq: {seq}")
                return action, seq, None
        
        error_msg = f"命令 {command} 中未找到 process: {process}"
        L.error(error_msg)
        return None, None, error_msg


class CommandStateManager:
    """管理命令状态转换的类"""
    _instance = None
    _initialized = False

    def __init__(self):
        if not self._initialized:
            self._state_cache: Dict[str, List[Dict[str, str]]] = {}  # conversation_id -> [{command: current_state}]
            self._command_states: Dict[str, List[str]] = {}  # command -> state_list
            self._lock = asyncio.Lock()
            self._initialized = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def _initialize_command_states_internal(self, command: str) -> tuple[bool, str | None]:
        """内部方法：初始化命令的状态列表（不获取锁）"""
        # 使用 CommandDataManager 获取命令数据
        command_data_manager = CommandDataManager()
        actions_dict, error = await command_data_manager.get_command_data(command)
        
        if error:
            L.error(f"CommandStateManager 初始化命令状态失败: {error}")
            return False, error
        
        if not actions_dict:
            error_msg = f"命令 {command} 的动作数据为空"
            L.error(error_msg)
            return False, error_msg
        
        # 提取状态名称列表（即JSON中的key）
        state_names = list(actions_dict.keys())
        
        self._command_states[command] = state_names
        L.debug(f"CommandStateManager 初始化命令 {command} 的状态列表: {state_names}")
        return True, None

    async def initialize_command_states(self, command: str) -> tuple[bool, str | None]:
        """根据command初始化命令的状态列表"""
        async with self._lock:
            return await self._initialize_command_states_internal(command)

    async def get_current_state(self, conversation_id: str, command: str = None) -> Optional[str]:
        """获取当前状态"""
        async with self._lock:
            conversation_states = self._state_cache.get(conversation_id, [])
            if command:
                # 查找指定命令的状态
                for state_dict in conversation_states:
                    if command in state_dict:
                        current_state = state_dict[command]
                        L.debug(f"CommandStateManager 获取会话 {conversation_id} 命令 {command} 当前状态: {current_state}")
                        return current_state
                L.debug(f"CommandStateManager 会话 {conversation_id} 命令 {command} 未找到状态")
                return None
            else:
                # 如果没有指定命令，返回第一个找到的状态（兼容性处理）
                if conversation_states:
                    first_state_dict = conversation_states[0]
                    current_state = next(iter(first_state_dict.values())) if first_state_dict else None
                    L.debug(f"CommandStateManager 获取会话 {conversation_id} 第一个状态: {current_state}")
                    return current_state
                return None

    async def set_current_state(self, conversation_id: str, state: str, command: str = None) -> None:
        """设置当前状态"""
        async with self._lock:
            if conversation_id not in self._state_cache:
                self._state_cache[conversation_id] = []
            
            conversation_states = self._state_cache[conversation_id]
            
            if command:
                # 查找是否已存在该命令的状态
                found = False
                for state_dict in conversation_states:
                    if command in state_dict:
                        state_dict[command] = state
                        found = True
                        break
                
                # 如果没有找到，添加新的命令状态
                if not found:
                    conversation_states.append({command: state})
                
                L.debug(f"CommandStateManager 设置会话 {conversation_id} 命令 {command} 状态为: {state}")
            else:
                # 兼容性处理：如果没有指定命令，更新所有已存在命令的状态
                if conversation_states:
                    for state_dict in conversation_states:
                        for cmd in state_dict:
                            state_dict[cmd] = state
                    L.debug(f"CommandStateManager 设置会话 {conversation_id} 所有命令状态为: {state}")

    async def update_state_by_exec_status(
        self, 
        conversation_id: str, 
        scene_exec_status: SceneExecStatus = None
    ) -> Optional[str]:
        """根据场景执行状态更新命令状态"""
        from aivc.sop.common.common import SceneExecStatus
        
        # 如果 scene_exec_status 为 None，直接返回当前状态
        if scene_exec_status is None:
            # 获取第一个命令的状态作为返回值（兼容性处理）
            conversation_states = self._state_cache.get(conversation_id, [])
            if conversation_states:
                for state_dict in conversation_states:
                    for command, state in state_dict.items():
                        L.debug(f"CommandStateManager update_state_by_exec_status 会话 {conversation_id} scene_exec_status为空，返回当前状态: {state}")
                        return state
            L.debug(f"CommandStateManager update_state_by_exec_status 会话 {conversation_id} scene_exec_status为空且无状态，返回None")
            return None
        
        # 不在这里获取锁，避免死锁
        conversation_states = self._state_cache.get(conversation_id, [])
        current_command = scene_exec_status.command if scene_exec_status else None
        
        # 查找当前命令的状态
        current_state = None
        if current_command:
            for state_dict in conversation_states:
                if current_command in state_dict:
                    current_state = state_dict[current_command]
                    break
        
        L.debug(f"CommandStateManager update_state_by_exec_status 会话 {conversation_id} 命令 {current_command} 当前状态: {current_state}")
        
        if not current_state and scene_exec_status and scene_exec_status.scene and current_command:
            # 如果没有当前状态，但有场景执行状态，初始化为该场景
            current_state = scene_exec_status.scene
            await self.set_current_state(conversation_id, current_state, current_command)
            L.debug(f"CommandStateManager 会话 {conversation_id} 命令 {current_command} 初始化状态为: {current_state}")
        
        if (scene_exec_status and 
            isinstance(scene_exec_status, SceneExecStatus) and
            scene_exec_status.status == "COMPLETED" and
            current_command):
            
            # 确保命令状态已初始化
            if current_command not in self._command_states:
                L.warning(f"CommandStateManager 命令 {current_command} 未初始化，尝试初始化")
                success, error = await self.initialize_command_states(current_command)
                if not success:
                    L.error(f"CommandStateManager 初始化命令 {current_command} 失败: {error}")
                    return current_state
            
            state_list = self._command_states[current_command]
            scene_name = scene_exec_status.scene
            
            # 根据 scene 名称找到下一个状态
            try:
                if scene_name in state_list:
                    current_index = state_list.index(scene_name)
                    # 获取下一个状态
                    if current_index < len(state_list) - 1:
                        next_state = state_list[current_index + 1]
                        # 直接更新缓存，避免调用需要锁的方法
                        async with self._lock:
                            if conversation_id not in self._state_cache:
                                self._state_cache[conversation_id] = []
                            
                            conversation_states = self._state_cache[conversation_id]
                            # 查找并更新指定命令的状态
                            found = False
                            for state_dict in conversation_states:
                                if current_command in state_dict:
                                    state_dict[current_command] = next_state
                                    found = True
                                    break
                            
                            # 如果没有找到，添加新的命令状态
                            if not found:
                                conversation_states.append({current_command: next_state})
                        
                        L.debug(f"CommandStateManager update_state_by_exec_status 会话 {conversation_id} 命令 {current_command} scene:{scene_name} COMPLETED, 更新状态为 {next_state}")
                        return next_state
                    else:
                        L.debug(f"CommandStateManager 命令 {current_command} 场景 {scene_name} 已是最后一个状态")
                else:
                    L.warning(f"CommandStateManager 场景 {scene_name} 不在状态列表中: {state_list}")
                    
            except Exception as e:
                L.error(f"CommandStateManager 处理场景状态更新失败: {e}")
        
        L.debug(f"CommandStateManager update_state_by_exec_status 会话 {conversation_id} 命令 {current_command} scene_exec_status:{scene_exec_status} 状态未更新，当前状态: {current_state}")
        return current_state
