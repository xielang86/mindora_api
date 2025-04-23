from aivc.chat.sleep_handler import get_curren_state
from aivc.common.sleep_config import StateType

def test_get_current_state_case1():
    local_state = StateType.BREATHING
    api_state = None
    llm_state = StateType.USING_PHONE
    current_state =  get_curren_state(
        local_state=local_state,
        api_state=api_state,
        llm_state=llm_state
    )
    print(current_state)

def test_get_current_state_case2():
    local_state = StateType.BREATHING
    api_state = StateType.USING_PHONE
    llm_state = StateType.USING_PHONE
    current_state =  get_curren_state(
        local_state=local_state,
        api_state=api_state,
        llm_state=llm_state
    )
    print(current_state)

def test_get_current_state_case3():
    local_state = StateType.BREATHING
    api_state = StateType.USING_PHONE
    llm_state = StateType.DEEP_SLEEP
    current_state =  get_curren_state(
        local_state=local_state,
        api_state=api_state,
        llm_state=llm_state
    )
    print(current_state)        

def test_get_current_state_case4():
    local_state = StateType.BREATHING
    api_state = StateType.SITTING_UP
    llm_state = StateType.SITTING_UP
    current_state =  get_curren_state(
        local_state=local_state,
        api_state=api_state,
        llm_state=llm_state
    )
    print(current_state)

if __name__ == "__main__":
    test_get_current_state_case4()
    test_get_current_state_case2()