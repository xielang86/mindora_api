import asyncio
from aivc.chat.sleep_state import SleepMonitor
from aivc.common.sleep_common import StateType, EyeStatus, BodyPoseType
import time

async def test_sleep_condition_detection():
    """测试睡眠条件检测"""
    monitor = SleepMonitor(sleep_threshold=2)
    conversation_id = "test_sleep_condition"

    # 测试满足睡眠条件的情况
    await monitor.check_sleep_condition(
        conversation_id,
        eye_status=EyeStatus.Closed.value,
        lie_status=BodyPoseType.Lie.value,
        current_state=StateType.POSTURE
    )
    
    # 验证开始睡眠时间已记录
    assert conversation_id in monitor._sleep_start_times
    
    # 测试不满足睡眠条件的情况
    await monitor.check_sleep_condition(
        conversation_id,
        eye_status=EyeStatus.Open.value,
        lie_status=BodyPoseType.Lie.value,
        current_state=StateType.POSTURE
    )
    
    # 验证开始睡眠时间已被删除
    assert conversation_id not in monitor._sleep_start_times

    print("睡眠条件检测测试通过")
 
async def test_sleep_threshold():
    """测试睡眠阈值功能"""
    monitor = SleepMonitor(sleep_threshold=2)
    conversation_id = "test_sleep_threshold"
    
    # 启动睡眠计时
    await monitor.check_sleep_condition(
        conversation_id,
        eye_status=EyeStatus.Closed.value,
        lie_status=BodyPoseType.Lie.value,
        current_state=StateType.POSTURE
    )
    
    # 验证初始状态
    assert not await monitor.is_sleeping(conversation_id)
    
    # 手动调整开始时间使其超过阈值
    monitor._sleep_start_times[conversation_id] = time.time() - 3
    
    # 再次检查，此时应该已经达到睡眠状态
    assert await monitor.is_sleeping(conversation_id)
    
    print("睡眠阈值功能测试通过")

async def test_sleep_interruption():
    """测试睡眠中断功能"""
    monitor = SleepMonitor(sleep_threshold=2)
    conversation_id = "test_interruption"
    
    # 启动睡眠计时
    await monitor.check_sleep_condition(
        conversation_id,
        eye_status=EyeStatus.Closed.value,
        lie_status=BodyPoseType.Lie.value,
        current_state=StateType.POSTURE
    )
    
    # 手动调整开始时间使其超过阈值
    monitor._sleep_start_times[conversation_id] = time.time() - 3
    
    # 检查是否已进入睡眠状态
    assert await monitor.is_sleeping(conversation_id)
    
    # 测试睡眠中断
    await monitor.interrupt_sleep(conversation_id)
    
    # 验证状态已重置
    assert not await monitor.is_sleeping(conversation_id)
    assert conversation_id not in monitor._sleep_start_times
    assert conversation_id not in monitor._sleep_states
    
    print("睡眠中断功能测试通过")

async def test_abnormal_states():
    """测试异常状态下的睡眠检测"""
    monitor = SleepMonitor(sleep_threshold=2)
    conversation_id = "test_abnormal"
    
    # 测试异常状态下的睡眠条件检测
    for abnormal_state in [StateType.USING_PHONE, StateType.SITTING_UP, StateType.LEAVING]:
        await monitor.check_sleep_condition(
            conversation_id,
            eye_status=EyeStatus.Closed.value,
            lie_status=BodyPoseType.Lie.value,
            current_state=abnormal_state
        )
        
        # 验证异常状态下不会记录睡眠开始时间
        assert conversation_id not in monitor._sleep_start_times
    
    print("异常状态睡眠检测测试通过")

async def test_continuous_sleep_tracking():
    """测试持续的睡眠跟踪"""
    monitor = SleepMonitor(sleep_threshold=2)
    conversation_id = "test_continuous"
    
    # 第一次满足睡眠条件
    await monitor.check_sleep_condition(
        conversation_id,
        eye_status=EyeStatus.Closed.value,
        lie_status=BodyPoseType.Lie.value,
        current_state=StateType.POSTURE
    )
    
    # 记录当前开始时间
    start_time = monitor._sleep_start_times[conversation_id]
    
    # 等待一点时间，但不足以达到阈值
    await asyncio.sleep(0.5)
    
    # 再次满足睡眠条件
    await monitor.check_sleep_condition(
        conversation_id,
        eye_status=EyeStatus.Closed.value,
        lie_status=BodyPoseType.Lie.value,
        current_state=StateType.POSTURE
    )
    
    # 验证开始时间没有被重置
    assert monitor._sleep_start_times[conversation_id] == start_time
    
    # 手动调整时间超过阈值并检查
    monitor._sleep_start_times[conversation_id] = time.time() - 3
    assert await monitor.is_sleeping(conversation_id)
    
    print("持续睡眠跟踪测试通过")

async def test_concurrent_operations():
    """测试并发操作"""
    monitor = SleepMonitor(sleep_threshold=2)
    conversation_ids = [f"concurrent_{i}" for i in range(5)]
    
    # 同时为多个会话开始睡眠计时
    tasks = []
    for conversation_id in conversation_ids:
        task = asyncio.create_task(
            monitor.check_sleep_condition(
                conversation_id,
                eye_status=EyeStatus.Closed.value,
                lie_status=BodyPoseType.Lie.value,
                current_state=StateType.POSTURE
            )
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    # 验证所有会话都开始了睡眠计时
    for conversation_id in conversation_ids:
        assert conversation_id in monitor._sleep_start_times
    
    # 手动调整一个会话的开始时间，使其达到睡眠阈值
    monitor._sleep_start_times[conversation_ids[0]] = time.time() - 3
    assert await monitor.is_sleeping(conversation_ids[0])
    
    # 其他会话应该还未达到睡眠状态
    for conversation_id in conversation_ids[1:]:
        assert not await monitor.is_sleeping(conversation_id)
    
    print("并发操作测试通过")

def run_sleep_monitor_tests():
    """运行所有睡眠监控测试"""
    print("\n开始睡眠监控测试...")
    
    asyncio.run(test_sleep_condition_detection())
    asyncio.run(test_sleep_threshold())
    asyncio.run(test_sleep_interruption())
    asyncio.run(test_abnormal_states())
    asyncio.run(test_continuous_sleep_tracking())
    asyncio.run(test_concurrent_operations())
    
    print("所有睡眠监控测试完成")

if __name__ == "__main__":
    run_sleep_monitor_tests()
