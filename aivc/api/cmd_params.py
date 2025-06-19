from aivc.common.task_class import QuestionType
from aivc.common.chat import ActionParams, Params
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
        
    def get_action_params(self, question_type_value: str, params: Optional[Params] = None) -> Optional[ActionParams]:
        """
        根据 QuestionType.value 获取对应的 ActionParams
        如果不是命令类型，则返回 None
        
        Args:
            question_type_value: 问题类型的值字符串
            params: 可选的参数对象，用于闹钟等需要额外参数的命令
            
        Returns:
            ActionParams: 对应的动作参数，如果不是命令则返回 None
        """
        question_type = QuestionType.get_type_by_value(question_type_value)
        if question_type is None:
            return None

        if not QuestionType.is_cmd(question_type):
            return None

        # 音量调节命令
        if question_type == QuestionType.VOLUME_MAIN_UP:
            return ActionParams(device="volume", operation="main", value="up")
        elif question_type == QuestionType.VOLUME_MAIN_DOWN:
            return ActionParams(device="volume", operation="main", value="down")
        elif question_type == QuestionType.VOLUME_MUTE:
            return ActionParams(device="volume", operation="main", value="mute")
        elif question_type == QuestionType.VOLUME_UNMUTE:
            return ActionParams(device="volume", operation="main", value="unmute")
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
        elif question_type == QuestionType.NIGHT_LIGHT_ON:
            return ActionParams(device="light", operation="night_light", value="on")
        elif question_type == QuestionType.NIGHT_LIGHT_OFF:
            return ActionParams(device="light", operation="night_light", value="off")
        
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
        elif question_type == QuestionType.LIGHT_MODE_NEXT:
            return ActionParams(device="light", operation="mode", value="next")
        
        # 香薰控制命令
        elif question_type == QuestionType.FRAGRANCE_ON:
            return ActionParams(device="fragrance", value="on")
        elif question_type == QuestionType.FRAGRANCE_OFF:
            return ActionParams(device="fragrance", value="off")
        elif question_type == QuestionType.FRAGRANCE_LOWER:
            return ActionParams(device="fragrance", operation="intensity", value="lower")
        elif question_type == QuestionType.FRAGRANCE_HIGHER:
            return ActionParams(device="fragrance", operation="intensity", value="higher")
        
        # 系统命令
        elif question_type == QuestionType.SYSTEM_SLEEP:
            return ActionParams(device="system", value="sleep")
        elif question_type == QuestionType.SYSTEM_SHUTDOWN:
            return ActionParams(device="system", value="shutdown")
            
        # 摄像头控制命令
        elif question_type == QuestionType.CAMERA_ON:
            return ActionParams(device="camera", value="on")
        elif question_type == QuestionType.CAMERA_OFF:
            return ActionParams(device="camera", value="off")
            
        # 麦克风控制命令
        elif question_type == QuestionType.MICROPHONE_ON:
            return ActionParams(device="microphone", value="on")
        elif question_type == QuestionType.MICROPHONE_OFF:
            return ActionParams(device="microphone", value="off")
            
        # 屏幕控制命令
        elif question_type == QuestionType.SCREEN_BRIGHTNESS_UP:
            return ActionParams(device="screen", operation="brightness", value="up")
        elif question_type == QuestionType.SCREEN_BRIGHTNESS_DOWN:
            return ActionParams(device="screen", operation="brightness", value="down")
            
        # 冥想功能命令
        elif question_type == QuestionType.MEDITATION_START:
            return ActionParams(device="meditation", value="start")
        elif question_type == QuestionType.MEDITATION_STOP:
            return ActionParams(device="meditation", value="stop")
            
        # 助眠功能命令
        elif question_type == QuestionType.SLEEP_ASSISTANT_START:
            return ActionParams(device="sleep_assistant", value="start")
        elif question_type == QuestionType.SLEEP_ASSISTANT_STOP:
            return ActionParams(device="sleep_assistant", value="stop")
            
        # 音乐播放控制命令
        elif question_type == QuestionType.MUSIC_PLAY:
            return ActionParams(device="music", value="play")
        elif question_type == QuestionType.MUSIC_STOP:
            return ActionParams(device="music", value="stop")
        elif question_type == QuestionType.MUSIC_NEXT:
            return ActionParams(device="music", value="next")
        elif question_type == QuestionType.MUSIC_REPEAT_ALL:
            return ActionParams(device="music", operation="mode", value="repeat_all")
        elif question_type == QuestionType.MUSIC_REPEAT_ONE:
            return ActionParams(device="music", operation="mode", value="repeat_one")
            
        elif question_type == QuestionType.ALARM_START:
            return ActionParams(device="alarm", value="on")
        elif question_type == QuestionType.ALARM_STOP:
            return ActionParams(device="alarm", value="off")
        elif question_type == QuestionType.ALARM_SET:
            return ActionParams(device="alarm", value="set", params=params)
        elif question_type == QuestionType.ALARM_CANCEL:
            return ActionParams(device="alarm", value="cancel", params=params)
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
        question_type = QuestionType.get_type_by_value(question_type_value)
        if question_type is None:
            return None

        if not QuestionType.is_cmd(question_type):
            return None
        
        # 音频文件名格式固定为 QuestionType名称.mp3
        audio_filename = f"{question_type.name}.mp3"
        
        # 音量调节命令
        if question_type == QuestionType.VOLUME_MAIN_UP:
            return "好的，音量已调大", audio_filename
        elif question_type == QuestionType.VOLUME_MAIN_DOWN:
            return "好的，音量已调小", audio_filename
        elif question_type == QuestionType.VOLUME_MUTE:
            return "好的，音量已静音", audio_filename
        elif question_type == QuestionType.VOLUME_UNMUTE:
            return "好的，音量已取消静音", audio_filename
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
        elif question_type == QuestionType.NIGHT_LIGHT_ON:
            return "好的，夜灯已开", audio_filename
        elif question_type == QuestionType.NIGHT_LIGHT_OFF:
            return "好的，夜灯已关", audio_filename
        
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
        elif question_type == QuestionType.LIGHT_MODE_NEXT:
            return "好的，已切换到下一个灯光模式", audio_filename
        
        # 香薰控制命令
        elif question_type == QuestionType.FRAGRANCE_ON:
            return "好的，香氛已开启", audio_filename
        elif question_type == QuestionType.FRAGRANCE_OFF:
            return "好的，香氛已关闭", audio_filename
        elif question_type == QuestionType.FRAGRANCE_LOWER:
            return "好的，香氛浓度已降低", audio_filename
        elif question_type == QuestionType.FRAGRANCE_HIGHER:
            return "好的，香氛浓度已提高", audio_filename
        
        # 系统命令
        elif question_type == QuestionType.SYSTEM_SLEEP:
            return "好的，设备即将进入休眠模式", audio_filename
        elif question_type == QuestionType.SYSTEM_SHUTDOWN:
            return "好的，设备即将关机", audio_filename
        
        # 摄像头控制命令
        elif question_type == QuestionType.CAMERA_ON:
            return "好的，摄像头已开启", audio_filename
        elif question_type == QuestionType.CAMERA_OFF:
            return "好的，摄像头已关闭", audio_filename
            
        # 麦克风控制命令
        elif question_type == QuestionType.MICROPHONE_ON:
            return "好的，麦克风已开启", audio_filename
        elif question_type == QuestionType.MICROPHONE_OFF:
            return "好的，麦克风已关闭", audio_filename
            
        # 屏幕控制命令
        elif question_type == QuestionType.SCREEN_BRIGHTNESS_UP:
            return "好的，屏幕亮度已调高", audio_filename
        elif question_type == QuestionType.SCREEN_BRIGHTNESS_DOWN:
            return "好的，屏幕亮度已调低", audio_filename
            
        # 冥想功能命令
        elif question_type == QuestionType.MEDITATION_START:
            return "好的，冥想功能已开启", audio_filename
        elif question_type == QuestionType.MEDITATION_STOP:
            return "好的，冥想功能已关闭", audio_filename
            
        # 助眠功能命令
        elif question_type == QuestionType.SLEEP_ASSISTANT_START:
            return "好的，助眠功能已开启", audio_filename
        elif question_type == QuestionType.SLEEP_ASSISTANT_STOP:
            return "好的，助眠功能已关闭", audio_filename
            
        # 音乐播放控制命令
        elif question_type == QuestionType.MUSIC_PLAY:
            return "好的，音乐播放已开启", audio_filename
        elif question_type == QuestionType.MUSIC_STOP:
            return "好的，音乐播放已停止", audio_filename
        elif question_type == QuestionType.MUSIC_NEXT:
            return "好的，已切换到下一首音乐", audio_filename
        elif question_type == QuestionType.MUSIC_REPEAT_ALL:
            return "好的，已设置音乐循环播放所有", audio_filename
        elif question_type == QuestionType.MUSIC_REPEAT_ONE:
            return "好的，已设置音乐单曲循环", audio_filename
            
        # 闹钟功能命令
        elif question_type == QuestionType.ALARM_START:
            return "好的，闹钟已开启", audio_filename
        elif question_type == QuestionType.ALARM_STOP:
            return "好的，已停止所有闹钟", audio_filename
        elif question_type == QuestionType.ALARM_SET:
            return "好的，闹钟已设置", audio_filename
        elif question_type == QuestionType.ALARM_CANCEL:
            return "好的，闹钟已取消", audio_filename
        
        # 未知命令类型
        return "", ""
    
    def run_tests(self):
        """运行所有测试函数"""
        self.test_get_action_params()
        self.test_get_cmd_response()
    
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