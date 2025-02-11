from typing import List
from enum import Enum

class QuestionType(Enum):
    DEFAULT = ('default', -0.83)
    ABOUT = ('about', -0.9)
    SUPPORT = ('support', -0.85)
    SONG = ('song', -0.83)
    TAKE_PHOTO = ('take_photo', -0.83)
    SLEEP_ASSISTANT = ('sleep_assistant', -0.91)
    PHOTO_RECOGNITION = ('photo_recognition', -0.83)
    WEATHER = ('weather', -0.76)

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

