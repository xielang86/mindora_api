from aivc.utils.id import get_id,get_conversation_id,get_message_id

def test_get_id():
    id = get_id()
    assert len(id) == 52

def test_get_conversation_id():
    conversation_id = get_conversation_id()
    print(conversation_id)
    assert len(conversation_id) > 0

def test_get_message_id():
    message_id = get_message_id()
    print(message_id)
    assert len(message_id) > 0

if __name__ == '__main__':
    test_get_id()
    test_get_conversation_id()
    test_get_message_id()