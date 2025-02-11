import asyncio
import time
from aivc.chat.sleep_dect_rpc import StateManager
from aivc.common.sleep_common import StateType, SceneExecStatus

def test_get_current_state():
    conversation_id = "test"
    start_time = time.strftime('%H:%M:%S')
    current_state = asyncio.run(StateManager().get_current_state(conversation_id))
    time.sleep(1)
    print(f"[{start_time}] current_state:", current_state)
    assert current_state is not None

def run_serial_tests():
    for i in range(10):
        print(f"\n开始执行第 {i+1} 次测试")
        test_get_current_state()  # 直接调用测试函数

def test_get_next_state():
    # 测试场景序号小于7的情况
    assert StateType.get_next_state(0) == StateType.PREPARE  # 1 -> 2
    assert StateType.get_next_state(1) == StateType.POSTURE  # 1 -> 2
    assert StateType.get_next_state(2) == StateType.BREATHING  # 2 -> 3
    assert StateType.get_next_state(6) == StateType.RELAX_4  # 6 -> 7
    
    # 测试场景序号大于等于7的情况
    assert StateType.get_next_state(7) == StateType.RELAX_4  # 7 -> 7
    assert StateType.get_next_state(8) == StateType.SLEEP_READY  # 8 -> 8
    assert StateType.get_next_state(10) == StateType.DEEP_SLEEP  # 10 -> 10
    
    print("所有 get_next_state 测试用例通过")

def test_get_current_state_case1():
    conversation_id = "test"
    scene_exec_status = SceneExecStatus(scene_seq=1, status="COMPLETED")
    current_state = asyncio.run(StateManager().update_state_by_exec_status(conversation_id,scene_exec_status))
    time.sleep(1)
    assert current_state.order == 2

def test_get_current_state_case2():
    conversation_id = "test"
    scene_exec_status = SceneExecStatus(scene_seq=1, status="COMPLETED")
    current_state = asyncio.run(StateManager().update_state_by_exec_status(conversation_id,scene_exec_status))
    time.sleep(1)
    assert current_state.order == 2

    scene_exec_status = SceneExecStatus(scene_seq=400, status="COMPLETED")
    current_state = asyncio.run(StateManager().update_state_by_exec_status(conversation_id,scene_exec_status))
    time.sleep(1)
    assert current_state is None

if __name__ == "__main__":
    test_get_current_state_case2()