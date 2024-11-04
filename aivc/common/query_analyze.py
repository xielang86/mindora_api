from pydantic import BaseModel 
from aivc.common.task_class import TCData
 
class QueryAnalyzer(BaseModel):
    question: str
    task_class: str = TCData.DEFAULT

     