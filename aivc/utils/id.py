import uuid
from datetime import datetime

def get_id() -> str:
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-3]
    return f"{timestamp}-{uuid.uuid4().hex}"

def get_conversation_id() -> str:
    return uuid.uuid4().hex

def get_message_id() -> str:
    return get_id()