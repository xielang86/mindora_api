import asyncio
from aivc.chat.sleep_state import StateManager
from aivc.common.sleep_common import StateType, SceneExecStatus

async def test_state_manager_initialization():
    """测试状态管理器初始化"""
    manager = StateManager()
    conversation_id = "test_init"
    
    # 测试初始状态为PREPARE
    current_state = await manager.get_current_state(conversation_id)
    assert current_state == StateType.PREPARE
    
    print("状态管理器初始化测试通过")

async def test_state_update_and_get():
    """测试状态更新和获取"""
    manager = StateManager()
    conversation_id = "test_update"
    
    # 测试设置正常状态
    await manager.set_state(conversation_id, StateType.POSTURE)
    current_state = await manager.get_current_state(conversation_id)
    assert current_state == StateType.POSTURE
    
    # 测试设置异常状态(应该被忽略)
    await manager.set_state(conversation_id, StateType.USING_PHONE)
    current_state = await manager.get_current_state(conversation_id)
    assert current_state == StateType.POSTURE  # 状态应该保持不变
    
    print("状态更新和获取测试通过")

async def test_exec_status_update():
    """测试场景执行状态更新"""
    manager = StateManager()
    conversation_id = "test_exec"
    
    # 测试场景执行完成状态更新
    exec_status = SceneExecStatus(scene_seq=1, status="COMPLETED")
    new_state = await manager.update_state_by_exec_status(conversation_id, exec_status)
    
    # 验证状态已正确更新到下一个状态
    assert new_state == StateType.get_next_state(1)
    current_state = await manager.get_current_state(conversation_id)
    assert current_state == new_state
    
    print("场景执行状态更新测试通过")

async def test_exec_status_not_completed():
    """测试未完成的场景执行状态"""
    manager = StateManager()
    conversation_id = "test_not_completed"
    
    # 设置初始状态
    await manager.set_state(conversation_id, StateType.POSTURE)
    
    # 测试未完成状态不会触发状态更新
    exec_status = SceneExecStatus(scene_seq=2, status="RUNNING")
    new_state = await manager.update_state_by_exec_status(conversation_id, exec_status)
    
    # 验证状态保持不变
    assert new_state == StateType.POSTURE
    current_state = await manager.get_current_state(conversation_id)
    assert current_state == StateType.POSTURE
    
    print("未完成场景状态测试通过")

async def test_concurrent_state_updates():
    """测试并发状态更新"""
    manager = StateManager()
    conversation_id = "test_concurrent"
    
    # 创建多个并发的状态更新任务
    update_tasks = []
    states = [StateType.PREPARE, StateType.POSTURE, StateType.SLEEP_READY]
    
    for state in states:
        task = asyncio.create_task(manager.set_state(conversation_id, state))
        update_tasks.append(task)
    
    # 等待所有更新完成
    await asyncio.gather(*update_tasks)
    
    # 验证最终状态是最后一个有效的更新
    current_state = await manager.get_current_state(conversation_id)
    assert current_state == StateType.SLEEP_READY
    
    print("并发状态更新测试通过")

async def test_get_next_state():
    """测试状态转换逻辑"""
    # 测试正常序列状态转换 (1-6)
    assert StateType.get_next_state(1) == StateType.POSTURE
    assert StateType.get_next_state(2) == StateType.BREATHING
    assert StateType.get_next_state(3) == StateType.RELAX_1
    assert StateType.get_next_state(4) == StateType.RELAX_2
    assert StateType.get_next_state(5) == StateType.RELAX_3
    assert StateType.get_next_state(6) == StateType.RELAX_3  # 最大状态不再增长
    
    # 测试睡眠相关状态 (10-12)
    assert StateType.get_next_state(10) == StateType.SLEEP_READY
    assert StateType.get_next_state(11) == StateType.LIGHT_SLEEP
    assert StateType.get_next_state(12) == StateType.DEEP_SLEEP
    
    # 测试边界情况
    assert StateType.get_next_state(0) == StateType.PREPARE  # 最小值
    assert StateType.get_next_state(7) == StateType.RELAX_3  # 超过正常序列但小于10
    assert StateType.get_next_state(9) == StateType.RELAX_3  # 超过正常序列但小于10
    assert StateType.get_next_state(14) is None  # 超过最大状态
    assert StateType.get_next_state(400) is None  # 异常状态序号
    
    print("状态转换逻辑测试通过")

async def run_all_tests():
    """运行所有状态管理器测试"""
    test_functions = [
        test_state_manager_initialization,
        test_state_update_and_get,
        test_exec_status_update,
        test_exec_status_not_completed,
        test_concurrent_state_updates,
        test_get_next_state
    ]
    
    print("\n开始状态管理器测试...")
    for test in test_functions:
        await test()
    print("所有状态管理器测试完成")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
