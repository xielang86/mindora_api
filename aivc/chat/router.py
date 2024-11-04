from aivc.chat.task_classifier import TaskClassifier
import asyncio
from aivc.config.config import L
from aivc.common.route import Route
import time
from aivc.common.task_class import TCData
import traceback

class Router:
    def __init__(self,
                route: Route):
        self.route = route

    async def router(self):
        start_time = time.perf_counter()
 
        task_name = await self.task_classifier()
        self.route.task_class = task_name
        L.debug(f"router question:{self.route.query_analyzer.question} task_name:{task_name} cost:{int((time.perf_counter() - start_time) * 1000)}ms")


    async def task_classifier(self):
        task_name = TCData.DEFAULT
        try:
            task_classifier = TaskClassifier(question=self.route.query_analyzer.question)
            task_name = await asyncio.to_thread(task_classifier.classify)
        except Exception as e:
            L.error(f"task_classifier error:{e}")
            traceback.print_exc()
        return task_name