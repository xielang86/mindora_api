import asyncio
import base64
from aivc.common.sleep_common import ReportReqData, ImageDataPayload
from aivc.common.trace_tree import TraceTree,TraceRoot
from aivc.chat.sleep_dect_rpc import get_state_by_api
from aivc.utils.id import get_message_id

async def test_get_state_by_api():
    """测试睡眠状态检测API函数"""
    print("开始测试 get_state_by_api 函数...")
    
    test_image_path = "/Users/gaochao/Downloads/use_phone.jpg"
    image_data = None
    
    try:
        with open(test_image_path, "rb") as image_file:
            image_bytes = image_file.read()
            image_data = base64.b64encode(image_bytes).decode('utf-8')
    except FileNotFoundError:
        print(f"警告：测试图像文件 {test_image_path} 不存在，使用空图像数据")
        # 如果没有测试图像，创建一个小的测试图像（1x1像素）
        from PIL import Image
        import io
        img = Image.new('RGB', (1, 1), color = 'black')
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # 创建测试数据
    images = ImageDataPayload(format="jpg", data=[image_data])
    report_data = ReportReqData(images=images)

    trace_tree = TraceTree(
        root = TraceRoot(
            message_id=get_message_id(),
            conversation_id=get_message_id(),
        )
    )
    
    # 调用被测试函数
    print("正在调用 get_state_by_api...")
    result = await get_state_by_api(report_data, trace_tree)
    
    # 检查并打印结果
    if result is None:
        print("测试结果：函数返回了 None，可能是RPC连接失败或服务异常")
    else:
        print("测试成功！RPC调用返回结果：")
        print(f"  状态码: {result.status_code}")
        print(f"  消息: {result.message}")
        print(f"  用户ID: {result.user_id}")
        print(f"  会话ID: {result.conversation_id}")
        print(f"  消息ID: {result.message_id}")
        print(f"  睡眠状态: {result.sleep_status}")
        if result.data:
            print(f"  睡眠类型: {result.data.sleep_type}")
            if result.data.pose_info:
                print("  姿态信息:")
                print(f"    身体状态: {result.data.pose_info.body}")
                print(f"    左手状态: {result.data.pose_info.left_hand}")
                print(f"    右手状态: {result.data.pose_info.right_hand}")
                print(f"    左眼状态: {result.data.pose_info.left_eye}")
                print(f"    右眼状态: {result.data.pose_info.right_eye}")

# 执行测试
if __name__ == "__main__":
    print("开始执行RPC测试...")
    asyncio.run(test_get_state_by_api())
    print("RPC测试完成.")
