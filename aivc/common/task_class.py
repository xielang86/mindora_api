from typing import List
from aivc.model.embed.embed import EmbedModel

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
    
class TCData:
    _instance = None
    task_vectors = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self.task_vectors is None:
            self._initialize_task_vectors()

    def _initialize_task_vectors(self):
        task_similar_words = [" ".join(task.similar_words) for task in self.task_classes]
        self.task_vectors = EmbedModel().embed(task_similar_words)

    def get_task_vectors(self):
        return self.task_vectors

    DEFAULT = "default"
    ABOUT = "about"
    Songs = "songs"

    BUILT_IN_QUESTION = [
        "介绍下自己",
        "唱个儿歌",
    ]

    task_classes:List[TaskClass] =  [
        TaskClass(
            name = ABOUT,
            similar_words = [
                "你的名字", "你是什么", "你来自哪里", 
                "你是谁呀", "你叫什么名字", "你是机器人吗",
                "介绍一下你自己", "你能干什么", "你会做什么",
                "我想认识你", "和我说说你吧", "你好厉害啊是谁呀"
            ],
            keywords =  ["自我介绍"]            
        ),
        TaskClass(
            name = Songs,
            similar_words = [
                "唱歌", "唱首歌", "唱个儿歌",
                "给我唱歌", "给我唱个儿歌", "唱首儿歌",
                "会唱歌吗", "你会唱歌吗", "来一首儿歌",
                "想听儿歌", "我要听歌", "给我来首歌"
            ],
            keywords =  ["儿歌"]
        ),
    ]

