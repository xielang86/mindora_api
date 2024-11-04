from aivc.common.task_class import TCData
from pydantic import BaseModel, Field
from aivc.common.query_analyze import QueryAnalyzer

class Route(BaseModel):
    query_analyzer: QueryAnalyzer = Field(default_factory=QueryAnalyzer)
    task_class: str = TCData.DEFAULT