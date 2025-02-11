import base64
from aivc.chat.sleep_dect_rpc import detect_sleep_scene
from aivc.common.sleep_common import ReportReqData, ImageDataPayload
import asyncio
 
def read_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def test_detect_sleep_scene():
    sleep = "/Users/gaochao/Downloads/sleep.jpg"
    awake = "/Users/gaochao/Downloads/awake.jpg"
    
    # 读取并转换图片
    sleep_base64 = read_image_to_base64(sleep)
    awake_base64 = read_image_to_base64(awake)
    
    # 测试睡眠图片
    report_data = ReportReqData(
            images=ImageDataPayload(
                format="jpeg",
                data=[sleep_base64]
            )
        )
    result = await detect_sleep_scene(report_data)
    print(f"Sleep image detection result: {result}")
    
    # 测试清醒图片
    report_data = ReportReqData(
            images=ImageDataPayload(
                format="jpeg",
                data=[awake_base64]
            )
        )
    result = await detect_sleep_scene(report_data)
    print(f"Awake image detection result: {result}")

if __name__ == '__main__':
    asyncio.run(test_detect_sleep_scene())
