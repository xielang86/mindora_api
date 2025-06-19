from typing import List, Union # 添加 Union
from sqlmodel import Session, select
from sqlalchemy import text
from aivc.common.kb import QuestionCategory, Question, QuestionV2, KBSearchResult # 添加 QuestionV2
from aivc.common.task_class import QuestionType

def create_category(
    *,
    session: Session,
    category_name: str,
    answer: str
) -> QuestionCategory:
    stmt = select(QuestionCategory).where(QuestionCategory.category_name == category_name)
    existing_category = session.exec(stmt).first()
    
    if existing_category:
        existing_category.answer = answer
        session.add(existing_category)
        session.commit()
        session.refresh(existing_category)
        return existing_category
    
    category = QuestionCategory(category_name=category_name, answer=answer)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

def create_question(
    *,
    session: Session,
    question: str,
    vector: List[float],
    category_id: int,
    version: int = 1  
) -> Union[Question, QuestionV2]:
    Model = QuestionV2 if version == 2 else Question 
    
    stmt = select(Model).where(Model.question == question)
    existing_question = session.exec(stmt).first()
    
    if existing_question:
        existing_question.vector = vector
        existing_question.category_id = category_id
        session.add(existing_question)
        session.commit()
        session.refresh(existing_question)
        return existing_question
    
    question_obj = Model(
        question=question,
        vector=vector,
        category_id=category_id
    )
    session.add(question_obj)
    session.commit()
    session.refresh(question_obj)
    return question_obj
    
def search_similar_questions(
    *,
    session: Session,
    vector: List[float], 
    top_k: int = 5,
    threshold: float = QuestionType.get_min_threshold(),
    version: int = 1  
) -> List[KBSearchResult]:
    """
    根据向量搜索相似问题
    
    Args:
        session: 数据库会话
        vector: 查询向量
        top_k: 返回结果数量
        threshold: 相似度阈值
        version: 使用的模型版本 (1 或 2)
    
    Returns:
        匹配的问题列表
    """
    session.exec(text("SET LOCAL enable_seqscan = OFF"))
    session.exec(text("SET LOCAL hnsw.ef_search = 20")) 
    session.exec(text("SET LOCAL enable_bitmapscan = OFF"))
    session.exec(text("SET LOCAL enable_tidscan = OFF"))

    table_name = "questions_v2" if version == 2 else "questions" 

    statement_sql = f"""
        WITH vector_search AS (
            SELECT 
                q.id,
                q.question,
                qc.category_name,
                qc.answer,
                q.vector <#> cast(:search_vector as vector) as distance
            FROM {table_name} q
            JOIN question_categories qc ON q.category_id = qc.id
            ORDER BY q.vector <#> cast(:search_vector as vector)
            LIMIT :top_k
        )
        SELECT 
            id,
            question,
            category_name,
            answer,
            distance
        FROM vector_search
        WHERE distance <= :threshold
        ORDER BY distance;
    """
    statement = text(statement_sql)
    
    params = {
        "search_vector": vector,
        "top_k": top_k,
        "threshold": threshold
    }
    
    results = session.exec(statement=statement, params=params).all()
    
    search_results = [
        KBSearchResult(
            id=result[0],
            question=result[1], 
            category_name=result[2],
            answer=result[3],
            similarity=result[4]
        )
        for result in results
    ]
    
    return search_results