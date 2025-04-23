import asyncio
import time
from aivc.chat.sleep_alert_state import AlertStateManager
from aivc.common.sleep_config import StateType
from aivc.common.sleep_alert import AlertLevel
from aivc.common.sleep_common import Actions

# 测试辅助函数
def assert_equal(a, b, message=None):
    if a != b:
        error_message = f"断言失败: {a} != {b}"
        if message:
            error_message += f" - {message}"
        raise AssertionError(error_message)

def assert_is(a, b, message=None):
    if a is not b:
        error_message = f"断言失败: {a} 不是 {b}"
        if message:
            error_message += f" - {message}"
        raise AssertionError(error_message)

def assert_in(a, b, message=None):
    if a not in b:
        error_message = f"断言失败: {a} 不在 {b} 中"
        if message:
            error_message += f" - {message}"
        raise AssertionError(error_message)

def assert_not_in(a, b, message=None):
    if a in b:
        error_message = f"断言失败: {a} 在 {b} 中"
        if message:
            error_message += f" - {message}"
        raise AssertionError(error_message)

def assert_is_none(a, message=None):
    if a is not None:
        error_message = f"断言失败: {a} 不是 None"
        if message:
            error_message += f" - {message}"
        raise AssertionError(error_message)

# 测试函数
async def test_singleton_pattern():
    """测试单例模式"""
    print("测试单例模式...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager1 = AlertStateManager()
    manager2 = AlertStateManager()
    assert_is(manager1, manager2, "单例模式失败: 创建了多个实例")
    print("✓ 通过")

async def test_update_state_normal():
    """测试更新正常状态"""
    print("测试更新正常状态...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    state = StateType.PREPARE  # 正常状态
    alert_level, actions = await manager.update_state(conversation_id, state)
    assert_is_none(alert_level, "正常状态不应触发告警")
    assert_is_none(actions, "正常状态不应返回动作")
    
    # 验证状态已记录
    conversation_data = manager._states[conversation_id]
    assert_equal(len(conversation_data["history"]), 1)
    assert_equal(conversation_data["history"][0], state)
    assert_equal(conversation_data["normal_state"], state)
    print("✓ 通过")

async def test_update_state_abnormal_using_phone_l1():
    """测试玩手机状态触发L1告警"""
    print("测试玩手机状态触发L1告警...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 连续添加3次玩手机状态
    results = []
    actions_list = []
    for _ in range(3):
        alert_level, actions = await manager.update_state(conversation_id, StateType.USING_PHONE)
        results.append(alert_level)
        actions_list.append(actions)
    
    # 第3次应该触发L1告警
    assert_equal(results[-1], AlertLevel.L1)
    assert_in("action_feature", actions_list[-1].dict())
    assert_equal(actions_list[-1].action_feature, "alert_level_1")
    
    conversation_data = manager._states[conversation_id]
    assert_equal(conversation_data["last_alert_level"], AlertLevel.L1)
    print("✓ 通过")

async def test_update_state_abnormal_using_phone_l2():
    """测试玩手机状态触发L2告警"""
    print("测试玩手机状态触发L2告警...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 添加6次玩手机状态
    results = []
    actions_list = []
    for _ in range(6):
        alert_level, actions = await manager.update_state(conversation_id, StateType.USING_PHONE)
        results.append(alert_level)
        actions_list.append(actions)
    
    # 第6次应该触发L2告警
    assert_equal(results[-1], AlertLevel.L2)
    assert_in("action_feature", actions_list[-1].dict())
    assert_equal(actions_list[-1].action_feature, "alert_level_2")
    
    conversation_data = manager._states[conversation_id]
    assert_equal(conversation_data["last_alert_level"], AlertLevel.L2)
    print("✓ 通过")

async def test_update_state_abnormal_using_phone_l3():
    """测试玩手机状态触发L3告警"""
    print("测试玩手机状态触发L3告警...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 添加8次玩手机状态
    results = []
    actions_list = []
    for _ in range(8):
        alert_level, actions = await manager.update_state(conversation_id, StateType.USING_PHONE)
        results.append(alert_level)
        actions_list.append(actions)
    
    # 第8次应该触发L3告警
    assert_equal(results[-1], AlertLevel.L3)
    assert_in("action_feature", actions_list[-1].dict())
    assert_equal(actions_list[-1].action_feature, "alert_level_3")
    
    conversation_data = manager._states[conversation_id]
    assert_equal(conversation_data["last_alert_level"], AlertLevel.L3)
    print("✓ 通过")

async def test_update_state_abnormal_sitting_up_l1():
    """测试坐起状态触发L1告警"""
    print("测试坐起状态触发L1告警...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 连续添加2次坐起状态
    results = []
    actions_list = []
    for _ in range(2):
        alert_level, actions = await manager.update_state(conversation_id, StateType.SITTING_UP)
        results.append(alert_level)
        actions_list.append(actions)
    
    # 第2次应该触发L1告警
    assert_equal(results[-1], AlertLevel.L1)
    assert_in("action_feature", actions_list[-1].dict())
    assert_equal(actions_list[-1].action_feature, "alert_level_1")
    
    conversation_data = manager._states[conversation_id]
    assert_equal(conversation_data["last_alert_level"], AlertLevel.L1)
    print("✓ 通过")

async def test_update_state_abnormal_sitting_up_l3():
    """测试坐起状态触发L3告警"""
    print("测试坐起状态触发L3告警...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 连续添加4次坐起状态
    results = []
    actions_list = []
    for _ in range(4):
        alert_level, actions = await manager.update_state(conversation_id, StateType.SITTING_UP)
        results.append(alert_level)
        actions_list.append(actions)
    
    # 第4次应该触发L3告警
    assert_equal(results[-1], AlertLevel.L3)
    assert_in("action_feature", actions_list[-1].dict())
    assert_equal(actions_list[-1].action_feature, "alert_level_3")
    
    conversation_data = manager._states[conversation_id]
    assert_equal(conversation_data["last_alert_level"], AlertLevel.L3)
    print("✓ 通过")

async def test_update_state_abnormal_leaving_l4():
    """测试离开状态触发L4告警"""
    print("测试离开状态触发L4告警...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 连续添加3次离开状态
    results = []
    actions_list = []
    for _ in range(3):
        alert_level, actions = await manager.update_state(conversation_id, StateType.LEAVING)
        results.append(alert_level)
        actions_list.append(actions)
    
    # 第3次应该触发L4告警
    assert_equal(results[-1], AlertLevel.L4)
    assert_in("action_feature", actions_list[-1].dict())
    assert_equal(actions_list[-1].action_feature, "alert_level_4")
    
    conversation_data = manager._states[conversation_id]
    assert_equal(conversation_data["last_alert_level"], AlertLevel.L4)
    print("✓ 通过")

async def test_update_state_recovery_l0():
    """测试正常状态触发L0告警（等待恢复）"""
    print("测试正常状态触发L0告警（等待恢复）...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 先添加异常状态
    await manager.update_state(conversation_id, StateType.USING_PHONE)
    
    # 然后连续添加2次正常状态
    results = []
    actions_list = []
    for _ in range(2):
        alert_level, actions = await manager.update_state(conversation_id, StateType.PREPARE)
        results.append(alert_level)
        actions_list.append(actions)
    
    # 第2次应该触发L0告警
    assert_equal(results[-1], AlertLevel.L0)
    assert_in("action_feature", actions_list[-1].dict())
    assert_equal(actions_list[-1].action_feature, "alert_level_0")
    
    conversation_data = manager._states[conversation_id]
    assert_equal(conversation_data["last_alert_level"], AlertLevel.L0)
    print("✓ 通过")

async def test_update_state_recovery_normal():
    """测试正常状态触发NORMAL告警（完全恢复）"""
    print("测试正常状态触发NORMAL告警（完全恢复）...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 先添加异常状态
    await manager.update_state(conversation_id, StateType.USING_PHONE)
    
    # 然后连续添加4次正常状态
    results = []
    actions_list = []
    for _ in range(4):
        alert_level, actions = await manager.update_state(conversation_id, StateType.PREPARE)
        results.append(alert_level)
        actions_list.append(actions)
    
    # 第4次应该触发NORMAL告警
    assert_equal(results[-1], AlertLevel.NORMAL)
    # 目前没有为NORMAL级别定义动作，检查是否返回了任何动作
    assert_in("action_feature", actions_list[-1].dict() if actions_list[-1] else {})
    
    conversation_data = manager._states[conversation_id]
    assert_equal(conversation_data["last_alert_level"], AlertLevel.NORMAL)
    print("✓ 通过")

async def test_mixed_states():
    """测试混合状态的场景"""
    print("测试混合状态的场景...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 添加一系列混合状态
    states = [
        StateType.PREPARE,       # 正常
        StateType.USING_PHONE,   # 异常
        StateType.USING_PHONE,   # 异常
        StateType.PREPARE,       # 正常
        StateType.USING_PHONE,   # 异常
        StateType.SITTING_UP,    # 异常
        StateType.SITTING_UP,    # 异常 - 应触发L1
    ]
    
    results = []
    actions_list = []
    for state in states:
        alert_level, actions = await manager.update_state(conversation_id, state)
        results.append(alert_level)
        actions_list.append(actions)
        
    # 验证最后一次更新应该触发L1告警
    assert_equal(results[-1], AlertLevel.L1)
    
    # 验证历史记录
    conversation_data = manager._states[conversation_id]
    assert_equal(len(conversation_data["history"]), len(states))
    print("✓ 通过")

async def test_clear_conversation():
    """测试清除会话数据"""
    print("测试清除会话数据...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation_id = "test_conversation"
    
    # 添加一些状态
    await manager.update_state(conversation_id, StateType.USING_PHONE)
    await manager.update_state(conversation_id, StateType.USING_PHONE)
    
    # 清除会话
    await manager.clear_conversation(conversation_id)
    
    # 验证会话数据已被清除
    assert_not_in(conversation_id, manager._states)
    
    # 清除不存在的会话不应该引发异常
    try:
        await manager.clear_conversation("non_existent_conversation")
        print("✓ 清除不存在的会话不会引发异常")
    except Exception as e:
        raise AssertionError(f"清除不存在的会话引发了异常: {e}")
    print("✓ 通过")

async def test_multiple_conversations():
    """测试多个会话的情况"""
    print("测试多个会话的情况...")
    # 重置单例
    AlertStateManager._instance = None
    AlertStateManager._initialized = False
    
    manager = AlertStateManager()
    conversation1 = "conversation1"
    conversation2 = "conversation2"
    
    # 在conversation1中添加状态
    await manager.update_state(conversation1, StateType.USING_PHONE)
    await manager.update_state(conversation1, StateType.USING_PHONE)
    
    # 在conversation2中添加状态
    await manager.update_state(conversation2, StateType.SITTING_UP)
    await manager.update_state(conversation2, StateType.SITTING_UP)
    
    # 验证两个会话的状态互不干扰
    assert_in(conversation1, manager._states)
    assert_in(conversation2, manager._states)
    
    conversation1_data = manager._states[conversation1]
    conversation2_data = manager._states[conversation2]
    
    assert_equal(len(conversation1_data["history"]), 2)
    assert_equal(len(conversation2_data["history"]), 2)
    
    assert_equal(conversation1_data["history"][0], StateType.USING_PHONE)
    assert_equal(conversation2_data["history"][0], StateType.SITTING_UP)
    print("✓ 通过")

async def run_tests():
    """运行所有测试"""
    test_functions = [
        test_singleton_pattern,
        test_update_state_normal,
        test_update_state_abnormal_using_phone_l1,
        test_update_state_abnormal_using_phone_l2,
        test_update_state_abnormal_using_phone_l3,
        test_update_state_abnormal_sitting_up_l1,
        test_update_state_abnormal_sitting_up_l3,
        test_update_state_abnormal_leaving_l4,
        test_update_state_recovery_l0,
        test_update_state_recovery_normal,
        test_mixed_states,
        test_clear_conversation,
        test_multiple_conversations
    ]
    
    passed = 0
    failed = 0
    
    print(f"开始运行测试，共 {len(test_functions)} 个测试...")
    print("-" * 50)
    
    for test in test_functions:
        try:
            await test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ 测试 {test.__name__} 失败: {str(e)}")
    
    print("-" * 50)
    print(f"测试结束，通过: {passed}，失败: {failed}")

# 如果直接运行此文件，则执行测试
if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(run_tests())
    end_time = time.time()
    print(f"总耗时: {end_time - start_time:.2f}秒")
