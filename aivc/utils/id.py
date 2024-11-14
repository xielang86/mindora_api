import uuid
from datetime import datetime
import base64

def get_id() -> str:
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-3]
    return f"{timestamp}-{uuid.uuid4().hex}"

def get_conversation_id() -> str:
    return uuid.uuid4().hex

def get_message_id() -> str:
    return get_id()

def short_uuid():
    while True:
        uid = base64.urlsafe_b64encode(bytes.fromhex(uuid.uuid4().hex)).decode('ascii').rstrip('=')
        if not uid.startswith(('-', '_')):
            return uid