import asyncio
from aivc.config.config import L
from aivc.common.route import Route
import time
import traceback
from sqlmodel import Session
from aivc.data.db.pg_engine import engine
from aivc.model.embed.embed import EmbedModel
from aivc.common.kb import KBSearchResult
from typing import Optional
from aivc.data.db import kb
from aivc.chat.prompt_selector import PromptSelector
from aivc.common.task_class import QuestionType
from aivc.chat.chat import Chat
from aivc.chat.parse_time import extract_time_params
from aivc.common.kb import Params

class Router:
    def __init__(self,
                route: Route,
                chat_instance: Chat = None):
        self.route = route
        self.embed_model = EmbedModel()

    async def search_kb(self, version: int = 2) -> Optional[KBSearchResult]:
        """
        搜索知识库，根据指定版本调用相应的嵌入模型
        
        Args:
            version: 使用的模型版本 (1 或 2)
            
        Returns:
            搜索结果
        """
        L.debug(f"search_kb question:{self.route.query_analyzer.question}")
        try:
            model_version = EmbedModel.V1 if version == 1 else EmbedModel.V2
            
            def sync_search():
                try:
                    with Session(engine) as session:
                        vector = self.embed_model.embed(
                            self.route.query_analyzer.question, 
                            version=model_version
                        )
                        return kb.search_similar_questions(
                            session=session,
                            vector=vector,
                            top_k=5,
                            version=version
                        )
                except Exception as e:
                    L.error(f"search_kb sync_search error: {e} stack:{traceback.format_exc()}")
                    traceback.print_exc()
                    return None

            results = await asyncio.to_thread(sync_search)
            L.debug(f"search_kb results:{results}")
            if results and len(results) > 0:
                first_result = results[0]
                threshold = QuestionType.get_threshold_by_category_name(first_result.category_name)
                if abs(first_result.similarity) >= abs(threshold):
                    return first_result
            return None
                
        except Exception as e:
            L.error(f"search_kb error: {e} stack:{traceback.format_exc()}")
            return None
        
    def init_question_param(self, kb_result: KBSearchResult):
        """
        获取问题参数
        """
        if not kb_result or not kb_result.category_name:
            L.debug("init_question_param kb_result is None or category_name is empty")
            return

        question_type = QuestionType.get_type_by_value(kb_result.category_name)

        if question_type not in [QuestionType.ALARM_SET, QuestionType.ALARM_CANCEL]:
            return
        
        question = self.route.query_analyzer.question
        params = extract_time_params(question)
        
        kb_result.params = Params(**params).model_dump()
        L.debug(f"init_question_param question:{question} params:{params}")

    async def router(self):
        start_time = time.perf_counter()
 
        kb_result = await self.search_kb()
        self.init_question_param(kb_result)
        self.route.kb_result = kb_result
        L.debug(f"router question:{self.route.query_analyzer.question} kb_result:{kb_result} cost:{int((time.perf_counter() - start_time) * 1000)}ms")
        # 选择prompt
        self.route.prompt = PromptSelector(kb_result=kb_result).select()
