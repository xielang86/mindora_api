from aivc.common.task_class import QuestionType
from aivc.common.chat import ActionParams
from typing import Optional, Tuple, Dict, Set


class CmdParamsManager:
    """命令参数管理器，处理命令类型的识别、动作参数生成和响应文本获取"""
    
    # 单例实例
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = CmdParamsManager()
        return cls._instance
    
    def __init__(self):
        """初始化命令参数管理器"""
        # 从值字符串到对应QuestionType的映射
        self._value_to_question_type: Dict[str, QuestionType] = {qt.value: qt for qt in QuestionType}
        
        # 命令类型值的集合
        self._cmd_values: Set[str] = set()
        self._init_cmd_values()
    
    def _init_cmd_values(self):
        """初始化命令类型值集合"""
        enum_members = list(QuestionType.__members__.keys())
        cmd_start_index = enum_members.index('VOLUME_MAIN_UP')
        
        for i in range(cmd_start_index, len(enum_members)):
            cmd_type = getattr(QuestionType, enum_members[i])
            self._cmd_values.add(cmd_type.value)
    
    def is_cmd_question_type(self, question_type_value: str) -> bool:
        """
        判断 QuestionType.value 是否属于命令(cmd)
        
        Args:
            question_type_value: 问题类型的值字符串
            
        Returns:
            bool: 如果是命令类型则返回 True，否则返回 False
        """
        return question_type_value in self._cmd_values
    
    def get_action_params(self, question_type_value: str) -> Optional[ActionParams]:
        """
        根据 QuestionType.value 获取对应的 ActionParams
        如果不是命令类型，则返回 None
        
        Args:
            question_type_value: 问题类型的值字符串
            
        Returns:
            ActionParams: 对应的动作参数，如果不是命令则返回 None
        """
        # 首先判断是否为命令类型
        if not self.is_cmd_question_type(question_type_value):
            return None
        
        # 获取对应的QuestionType枚举
        if question_type_value not in self._value_to_question_type:
            return None
        
        question_type = self._value_to_question_type[question_type_value]
        
        # 音量调节命令
        if question_type == QuestionType.VOLUME_MAIN_UP:
            return ActionParams(device="volume", operation="main", value="up")
        elif question_type == QuestionType.VOLUME_MAIN_DOWN:
            return ActionParams(device="volume", operation="main", value="down")
        elif question_type == QuestionType.VOLUME_MUTE:
            return ActionParams(device="volume", operation="main", value="mute")
        elif question_type == QuestionType.VOLUME_VOICE_UP:
            return ActionParams(device="volume", operation="voice", value="up")
        elif question_type == QuestionType.VOLUME_VOICE_DOWN:
            return ActionParams(device="volume", operation="voice", value="down")
        elif question_type == QuestionType.VOLUME_VOICE_MUTE:
            return ActionParams(device="volume", operation="voice", value="mute")
        elif question_type == QuestionType.VOLUME_BACKGROUND_UP:
            return ActionParams(device="volume", operation="background_sound", value="up")
        elif question_type == QuestionType.VOLUME_BACKGROUND_DOWN:
            return ActionParams(device="volume", operation="background_sound", value="down")
        elif question_type == QuestionType.VOLUME_BACKGROUND_MUTE:
            return ActionParams(device="volume", operation="background_sound", value="mute")
        elif question_type == QuestionType.VOLUME_MUSIC_UP:
            return ActionParams(device="volume", operation="music", value="up")
        elif question_type == QuestionType.VOLUME_MUSIC_DOWN:
            return ActionParams(device="volume", operation="music", value="down")
        elif question_type == QuestionType.VOLUME_MUSIC_MUTE:
            return ActionParams(device="volume", operation="music", value="mute")
        
        # 灯光控制命令
        elif question_type == QuestionType.LIGHT_BRIGHTNESS_UP:
            return ActionParams(device="light", operation="brightness", value="up")
        elif question_type == QuestionType.LIGHT_BRIGHTNESS_DOWN:
            return ActionParams(device="light", operation="brightness", value="down")
        elif question_type == QuestionType.LIGHT_COLOR_GREEN:
            return ActionParams(device="light", operation="color", value="green")
        elif question_type == QuestionType.LIGHT_COLOR_RED:
            return ActionParams(device="light", operation="color", value="red")
        elif question_type == QuestionType.LIGHT_COLOR_BLUE:
            return ActionParams(device="light", operation="color", value="blue")
        elif question_type == QuestionType.LIGHT_COLOR_PURPLE:
            return ActionParams(device="light", operation="color", value="purple")
        elif question_type == QuestionType.LIGHT_COLOR_YELLOW:
            return ActionParams(device="light", operation="color", value="yellow")
        elif question_type == QuestionType.LIGHT_COLOR_WHITE:
            return ActionParams(device="light", operation="color", value="white")
        elif question_type == QuestionType.LIGHT_STATE_ON:
            return ActionParams(device="light", operation="state", value="on")
        elif question_type == QuestionType.LIGHT_STATE_OFF:
            return ActionParams(device="light", operation="state", value="off")
        
        # 灯光模式控制命令
        elif question_type == QuestionType.LIGHT_MODE_FLOWING_COLOR:
            return ActionParams(device="light", operation="mode", value="flowing_color")
        elif question_type == QuestionType.LIGHT_MODE_STARRY_SKY:
            return ActionParams(device="light", operation="mode", value="starry_sky")
        elif question_type == QuestionType.LIGHT_MODE_JELLYFISH:
            return ActionParams(device="light", operation="mode", value="jellyfish")
        elif question_type == QuestionType.LIGHT_MODE_FLAME:
            return ActionParams(device="light", operation="mode", value="flame")
        elif question_type == QuestionType.LIGHT_MODE_WAVES:
            return ActionParams(device="light", operation="mode", value="waves")
        elif question_type == QuestionType.LIGHT_MODE_RANDOM:
            return ActionParams(device="light", operation="mode", value="random")
        
        # 香薰控制命令
        elif question_type == QuestionType.FRAGRANCE_ON:
            return ActionParams(device="fragrance", value="on")
        elif question_type == QuestionType.FRAGRANCE_OFF:
            return ActionParams(device="fragrance", value="off")
        
        # 系统命令
        elif question_type == QuestionType.SYSTEM_SLEEP:
            return ActionParams(device="system", value="sleep")
        
        # 未知命令类型
        return None
    
    def get_cmd_response(self, question_type_value: str) -> Tuple[str, str]:
        """
        根据 QuestionType.value 获取对应的文本响应和语音文件名
        如果不是命令类型，则返回空字符串和空文件名
        
        Args:
            question_type_value: 问题类型的值字符串
            
        Returns:
            Tuple[str, str]: (响应文本, 语音文件名)，如果不是命令则返回 ("", "")
        """
        # 首先判断是否为命令类型
        if not self.is_cmd_question_type(question_type_value):
            return "", ""
        
        # 获取对应的QuestionType枚举
        if question_type_value not in self._value_to_question_type:
            return "", ""
        
        question_type = self._value_to_question_type[question_type_value]
        
        # 音频文件名格式固定为 QuestionType名称.mp3
        audio_filename = f"{question_type.name}.mp3"
        
        # 音量调节命令
        if question_type == QuestionType.VOLUME_MAIN_UP:
            return "好的，音量已调大", audio_filename
        elif question_type == QuestionType.VOLUME_MAIN_DOWN:
            return "好的，音量已调小", audio_filename
        elif question_type == QuestionType.VOLUME_MUTE:
            return "好的，音量已静音", audio_filename
        elif question_type == QuestionType.VOLUME_VOICE_UP:
            return "好的，人声已调大", audio_filename
        elif question_type == QuestionType.VOLUME_VOICE_DOWN:
            return "好的，人声已调小", audio_filename
        elif question_type == QuestionType.VOLUME_VOICE_MUTE:
            return "好的，人声已静音", audio_filename
        elif question_type == QuestionType.VOLUME_BACKGROUND_UP:
            return "好的，背景音已调大", audio_filename
        elif question_type == QuestionType.VOLUME_BACKGROUND_DOWN:
            return "好的，背景音已调小", audio_filename
        elif question_type == QuestionType.VOLUME_BACKGROUND_MUTE:
            return "好的，背景音已静音", audio_filename
        elif question_type == QuestionType.VOLUME_MUSIC_UP:
            return "好的，音乐已调大", audio_filename
        elif question_type == QuestionType.VOLUME_MUSIC_DOWN:
            return "好的，音乐已调小", audio_filename
        elif question_type == QuestionType.VOLUME_MUSIC_MUTE:
            return "好的，音乐已静音", audio_filename
        
        # 灯光控制命令
        elif question_type == QuestionType.LIGHT_BRIGHTNESS_UP:
            return "好的，灯光已调亮", audio_filename
        elif question_type == QuestionType.LIGHT_BRIGHTNESS_DOWN:
            return "好的，灯光已调暗", audio_filename
        elif question_type == QuestionType.LIGHT_COLOR_GREEN:
            return "好的，灯光已变成绿色", audio_filename
        elif question_type == QuestionType.LIGHT_COLOR_RED:
            return "好的，灯光已变成红色", audio_filename
        elif question_type == QuestionType.LIGHT_COLOR_BLUE:
            return "好的，灯光已变成蓝色", audio_filename
        elif question_type == QuestionType.LIGHT_COLOR_PURPLE:
            return "好的，灯光已变成紫色", audio_filename
        elif question_type == QuestionType.LIGHT_COLOR_YELLOW:
            return "好的，灯光已变成黄色", audio_filename
        elif question_type == QuestionType.LIGHT_COLOR_WHITE:
            return "好的，灯光已变成白色", audio_filename
        elif question_type == QuestionType.LIGHT_STATE_ON:
            return "好的，灯光已开", audio_filename
        elif question_type == QuestionType.LIGHT_STATE_OFF:
            return "好的，灯光已关", audio_filename
        
        # 灯光模式控制命令
        elif question_type == QuestionType.LIGHT_MODE_FLOWING_COLOR:
            return "好的，已设置为流光溢彩模式", audio_filename
        elif question_type == QuestionType.LIGHT_MODE_STARRY_SKY:
            return "好的，已设置为星空模式", audio_filename
        elif question_type == QuestionType.LIGHT_MODE_JELLYFISH:
            return "好的，已设置为水母模式", audio_filename
        elif question_type == QuestionType.LIGHT_MODE_FLAME:
            return "好的，已设置为火焰模式", audio_filename
        elif question_type == QuestionType.LIGHT_MODE_WAVES:
            return "好的，已设置为海浪模式", audio_filename
        elif question_type == QuestionType.LIGHT_MODE_RANDOM:
            return "好的，已切换灯光显示模式", audio_filename
        
        # 香薰控制命令
        elif question_type == QuestionType.FRAGRANCE_ON:
            return "好的，香氛已开启", audio_filename
        elif question_type == QuestionType.FRAGRANCE_OFF:
            return "好的，香氛已关闭", audio_filename
        
        # 系统命令
        elif question_type == QuestionType.SYSTEM_SLEEP:
            return "好的，设备即将进入休眠模式", audio_filename
        
        # 未知命令类型
        return "", ""
    
    def run_tests(self):
        """运行所有测试函数"""
        self.test_is_cmd_question_type()
        self.test_get_action_params()
        self.test_get_cmd_response()
    
    def test_is_cmd_question_type(self):
        """测试 is_cmd_question_type 函数功能"""
        print("======== 测试 is_cmd_question_type 功能 ========")
        
        # 测试 VOLUME_MAIN_UP 之前的类型 (应该不是命令)
        non_cmd_types = [
            QuestionType.DEFAULT.value,
            QuestionType.ABOUT.value,
            QuestionType.SUPPORT.value,
            QuestionType.SONG.value,
            QuestionType.TAKE_PHOTO.value,
            QuestionType.SLEEP_ASSISTANT.value,
            QuestionType.PHOTO_RECOGNITION.value,
            QuestionType.WEATHER.value
        ]
        
        # 测试 VOLUME_MAIN_UP 及之后的类型 (应该是命令)
        cmd_types = [
            QuestionType.VOLUME_MAIN_UP.value,
            QuestionType.VOLUME_MAIN_DOWN.value,
            QuestionType.LIGHT_COLOR_RED.value,
            QuestionType.FRAGRANCE_ON.value,
            QuestionType.SYSTEM_SLEEP.value
        ]
        
        print("\n非命令类型测试 (预期结果: False):")
        for value in non_cmd_types:
            result = self.is_cmd_question_type(value)
            print(f"{value}: {result} {'✓' if result == False else '✗'}")
        
        print("\n命令类型测试 (预期结果: True):")
        for value in cmd_types:
            result = self.is_cmd_question_type(value)
            print(f"{value}: {result} {'✓' if result == True else '✗'}")
        
        print("\n测试完成")
    
    def test_get_action_params(self):
        """测试 get_action_params 函数功能"""
        print("======== 测试 get_action_params 功能 ========")
        
        test_types = [
            QuestionType.DEFAULT.value,
            QuestionType.VOLUME_MAIN_UP.value,
            QuestionType.VOLUME_VOICE_DOWN.value,
            QuestionType.LIGHT_COLOR_RED.value,
            QuestionType.LIGHT_STATE_ON.value,
            QuestionType.FRAGRANCE_ON.value,
            QuestionType.SYSTEM_SLEEP.value
        ]
        
        for value in test_types:
            action_params = self.get_action_params(value)
            print(f"{value}: {action_params}")
        
        print("\n测试完成")
    
    def test_get_cmd_response(self):
        """测试 get_cmd_response 函数功能"""
        print("======== 测试 get_cmd_response 功能 ========")
        
        test_types = [
            QuestionType.DEFAULT.value,
            QuestionType.VOLUME_MAIN_UP.value,
            QuestionType.VOLUME_VOICE_DOWN.value,
            QuestionType.LIGHT_COLOR_RED.value,
            QuestionType.LIGHT_STATE_ON.value,
            QuestionType.FRAGRANCE_ON.value,
            QuestionType.SYSTEM_SLEEP.value
        ]
        
        for value in test_types:
            response_text, audio_filename = self.get_cmd_response(value)
            print(f"{value}: \"{response_text}\" (音频文件: {audio_filename})")
        
        print("\n测试完成")


if __name__ == "__main__":
    # 创建实例并运行测试
    cmd_manager = CmdParamsManager()
    cmd_manager.run_tests()