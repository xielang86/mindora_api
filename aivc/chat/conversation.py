from aivc.data.db import conversation
from typing import List, Dict, Any
from aivc.data.db.pg_engine import engine
from sqlmodel import Session
from aivc.common.task_class import QuestionType

def get_conversation_history(conversation_id: str, limit: int = 2, max_content_length: int = 30) -> List[Dict[str, Any]]:
    messages = []
    with Session(engine) as session:
        conversation_list = conversation.get_conversation_history(
            session=session, 
            conversation_id=conversation_id)
        
        # 如果指定了limit，只取最后limit条记录
        if limit is not None:
            conversation_list = conversation_list[-limit:]
            
        for conv in conversation_list:
            content = conv.content
            # 如果指定了最大内容长度，进行截断
            if max_content_length is not None and len(content) > max_content_length:
                content = content[:max_content_length]
                
            messages.append({
                "role": conv.role,
                "content": content
            })
    return messages

def get_last_take_photo_question(conversation_id: str) -> str:
    with Session(engine) as session:
        conversation_list = conversation.get_conversation_history(
            session=session, 
            conversation_id=conversation_id)
        for conv in reversed(conversation_list):
            if conv.role == "user" and conv.question_type == QuestionType.TAKE_PHOTO.value:
                return conv.content

def save_conversation(conversation_id: str, 
                    question: str, 
                    answer: str,
                    question_type:str = None) -> bool:
    with Session(engine) as session:
        conversation.save_conversation(
            session=session,
            conversation_id=conversation_id,
            role="user",
            content=question,
            question_type=question_type
        )

        conversation.save_conversation(
            session=session,
            conversation_id=conversation_id,
            role="assistant",
            content=answer
        )