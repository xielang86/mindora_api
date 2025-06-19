from typing import List
from enum import Enum

class QuestionType(Enum):
    DEFAULT = ('default', -0.90)
    ABOUT = ('about', -0.99)
    SUPPORT = ('support', -0.99)
    SONG = ('song', -0.99)
    TAKE_PHOTO = ('take_photo', -0.99)
    SLEEP_ASSISTANT = ('sleep_assistant', -0.94)
    PHOTO_RECOGNITION = ('photo_recognition', -0.94)
    WEATHER = ('weather', -0.94)

    VOLUME_MAIN_UP = ('volume_main_up', -0.94)
    VOLUME_MAIN_DOWN = ('volume_main_down', -0.94)
    VOLUME_MUTE = ('volume_mute', -0.94)
    VOLUME_UNMUTE = ('volume_unmute', -0.94)
    VOLUME_VOICE_UP = ('volume_voice_up', -0.94)
    VOLUME_VOICE_DOWN = ('volume_voice_down', -0.94)
    VOLUME_VOICE_MUTE = ('volume_voice_mute', -0.94)
    VOLUME_BACKGROUND_UP = ('volume_background_up', -0.94)
    VOLUME_BACKGROUND_DOWN = ('volume_background_down', -0.94)
    VOLUME_BACKGROUND_MUTE = ('volume_background_mute', -0.94)
    VOLUME_MUSIC_UP = ('volume_music_up', -0.94)
    VOLUME_MUSIC_DOWN = ('volume_music_down', -0.94)
    VOLUME_MUSIC_MUTE = ('volume_music_mute', -0.94)

    LIGHT_BRIGHTNESS_UP = ('light_brightness_up', -0.94)
    LIGHT_BRIGHTNESS_DOWN = ('light_brightness_down', -0.94)
    LIGHT_COLOR_GREEN = ('light_color_green', -0.94)
    LIGHT_COLOR_RED = ('light_color_red', -0.94)
    LIGHT_COLOR_BLUE = ('light_color_blue', -0.94)
    LIGHT_COLOR_PURPLE = ('light_color_purple', -0.94)
    LIGHT_COLOR_YELLOW = ('light_color_yellow', -0.94)
    LIGHT_COLOR_WHITE = ('light_color_white', -0.94)
    LIGHT_STATE_ON = ('light_state_on', -0.94)
    LIGHT_STATE_OFF = ('light_state_off', -0.94)
    NIGHT_LIGHT_ON = ('night_light_on', -0.94)
    NIGHT_LIGHT_OFF = ('night_light_off', -0.94)

    LIGHT_MODE_FLOWING_COLOR = ('light_mode_flowing_color', -0.94)
    LIGHT_MODE_STARRY_SKY = ('light_mode_starry_sky', -0.94)
    LIGHT_MODE_JELLYFISH = ('light_mode_jellyfish', -0.94)
    LIGHT_MODE_FLAME = ('light_mode_flame', -0.94)
    LIGHT_MODE_WAVES = ('light_mode_waves', -0.94)
    LIGHT_MODE_RANDOM = ('light_mode_random', -0.94)
    LIGHT_MODE_NEXT = ('light_mode_next', -0.94)

    FRAGRANCE_ON = ('fragrance_on', -0.94)
    FRAGRANCE_OFF = ('fragrance_off', -0.94)
    FRAGRANCE_LOWER = ('fragrance_lower', -0.94)
    FRAGRANCE_HIGHER = ('fragrance_higher', -0.94)

    SYSTEM_SLEEP = ('system_sleep', -0.94)
    SYSTEM_SHUTDOWN = ('system_shutdown', -0.94)
    
    CAMERA_ON = ('camera_on', -0.94)
    CAMERA_OFF = ('camera_off', -0.94)
    
    MICROPHONE_ON = ('microphone_on', -0.94)
    MICROPHONE_OFF = ('microphone_off', -0.94)
    
    SCREEN_BRIGHTNESS_UP = ('screen_brightness_up', -0.94)
    SCREEN_BRIGHTNESS_DOWN = ('screen_brightness_down', -0.94)
    
    MEDITATION_START = ('meditation_start', -0.94)
    MEDITATION_STOP = ('meditation_stop', -0.94)
    
    SLEEP_ASSISTANT_START = ('sleep_assistant_start', -0.94)
    SLEEP_ASSISTANT_STOP = ('sleep_assistant_stop', -0.94)
    
    MUSIC_PLAY = ('music_play', -0.94)
    MUSIC_STOP = ('music_stop', -0.94)
    MUSIC_NEXT = ('music_next', -0.94)
    MUSIC_REPEAT_ALL = ('music_repeat_all', -0.94)
    MUSIC_REPEAT_ONE = ('music_repeat_one', -0.94)
    
    ALARM_START = ('alarm_start', -0.94)
    ALARM_STOP = ('alarm_stop', -0.94)
    ALARM_SET = ('alarm_set', -0.94)
    ALARM_CANCEL = ('alarm_cancel', -0.94)
    

    def __init__(self, value: str, threshold: float):
        self._value_ = value
        self.threshold = threshold

    @property
    def value(self) -> str:
        return self._value_

    def get_threshold(self) -> float:
        return self.threshold

    @classmethod
    def get_threshold_by_category_name(cls, category_name: str) -> float:
        for question_type in cls:
            if question_type.value == category_name:
                return question_type.get_threshold()
        return cls.DEFAULT.get_threshold()

    @classmethod
    def get_min_threshold(cls) -> float:
        return min((type.threshold for type in cls), key=lambda x: abs(x))
        
    @classmethod
    def get_type_by_value(cls, value_str: str):
        """
        根据字符串值返回对应的 QuestionType 枚举实例
        """
        for question_type in cls:
            if question_type.value == value_str:
                return question_type
        return None
        
    @classmethod
    def is_cmd(cls, question_type) -> bool:
        """
        判断一个 QuestionType 是否属于命令类型
        """
        enum_members = list(cls.__members__.keys())
        cmd_start_index = enum_members.index('VOLUME_MAIN_UP')

        return enum_members.index(question_type.name) >= cmd_start_index
    
    @classmethod
    def is_cmd_by_value(cls, value_str: str) -> bool:
        """
        判断一个 QuestionType 是否属于命令类型
        """
        question_type = cls.get_type_by_value(value_str)
        if question_type is None:
            return False
        return cls.is_cmd(question_type)

QuestionWithAnswer = [QuestionType.ABOUT.value, QuestionType.SUPPORT.value]

class TaskClass:
    def __init__(self, 
            name: str, 
            similar_words: List[str]=[],
            keywords: list=[],
            vector: List[float]=[]):
        self.name = name
        self.similar_words = similar_words
        self.keywords = keywords
        self.vector = vector

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"], 
            similar_words=data["similar_words"],
            keywords=data["keywords"],
            vector=data.get("vector", []))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "similar_words": self.similar_words,
            "keywords": self.keywords,
            "vector": self.vector
        }

