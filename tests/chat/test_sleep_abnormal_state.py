import asyncio
from aivc.chat.sleep_state import AbnormalStateManager
from aivc.common.sleep_common import StateType

async def test_abnormal_state_manager():
    """测试异常状态管理器的基本功能"""
    for i in range(5):
        manager = AbnormalStateManager(mute_duration=2)  # 设置较短的静音时长便于测试
    conversation_id = "test_abnormal"
    abnormal_state = StateType.USING_PHONE
    normal_state = StateType.PREPARE

    # 测试初始化配置
    assert manager.mute_duration == 2

    # 测试正常状态更新
    await manager.update_state(conversation_id, normal_state)
    
    # 第一次报告应该返回True
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is True
    
    # 静音时间内再次报告应该返回False
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is False
    
    # 等待静音时间过后再次报告应该返回True
    await asyncio.sleep(2)
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is True
    
    # 第三次报告即使过了静音时间也应该返回False(达到最大报告次数)
    await asyncio.sleep(2)
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is False

    print("异常状态管理器基本功能测试通过")

async def test_abnormal_state_manager_state_change():
    """测试状态变化时的计数器重置"""
    manager = AbnormalStateManager(mute_duration=1)
    conversation_id = "test_state_change"
    abnormal_state = StateType.USING_PHONE
    
    # 设置初始状态PREPARE
    await manager.update_state(conversation_id, StateType.PREPARE)
    
    # 第一次报告
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is True
    await asyncio.sleep(2)
    # 第二次报告
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is True
    
    # 更新到新状态POSTURE
    await manager.update_state(conversation_id, StateType.POSTURE)
    
    # 状态更新后应该可以重新报告
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is True

    print("异常状态管理器状态变化测试通过")

async def test_abnormal_state_manager_sleep_ready():
    """测试SLEEP_READY状态下的异常报告抑制"""
    manager = AbnormalStateManager(mute_duration=1)
    conversation_id = "test_sleep_ready"
    abnormal_state = StateType.USING_PHONE
    
    # 设置SLEEP_READY状态
    await manager.update_state(conversation_id, StateType.SLEEP_READY)
    
    # SLEEP_READY状态下应该始终返回False
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is False
    await asyncio.sleep(1)
    assert await manager.should_report_abnormal(conversation_id, abnormal_state) is False

    print("异常状态管理器睡眠就绪状态测试通过")

def run_abnormal_state_tests():
    """运行所有异常状态管理器测试"""
    print("\n开始异常状态管理器测试...")
    asyncio.run(test_abnormal_state_manager())
    asyncio.run(test_abnormal_state_manager_state_change())
    asyncio.run(test_abnormal_state_manager_sleep_ready())
    print("所有异常状态管理器测试完成")

if __name__ == "__main__":
    run_abnormal_state_tests()