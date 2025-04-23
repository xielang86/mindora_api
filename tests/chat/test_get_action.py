from aivc.chat.sleep_dect_rpc import get_actions
from aivc.common.sleep_common import StateType
import asyncio

async def test_get_actions():
    """测试获取动作"""
    state = StateType.SITTING_UP
    actions = await get_actions(state)
    assert actions
    print("获取动作测试通过")

if __name__ == "__main__":
    asyncio.run(test_get_actions())