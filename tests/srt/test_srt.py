from aivc.srt.manager import SRTManager, SRTType
import asyncio
from aivc.utils.id import get_message_id

async def test_srt_recognize(srt_type: SRTType = SRTType.XUNFEI):
    srt = SRTManager.create_srt(srt_type=srt_type)
    rsp = await srt.recognize(audio_path="/Users/gaochao/Downloads/iat_pcm_16k.pcm", message_id="test-message-id")
    print(f"最终识别结果: {rsp}")
    assert len(rsp.result) > 0

async def test_srt_recognize_case2(srt_type: SRTType = SRTType.DOUBAO):
    message_id = get_message_id()
    srt = SRTManager.create_srt(srt_type=srt_type)
    rsp = await srt.recognize(audio_path="/usr/local/src/seven_ai/aivoicechat/upload/20250311-122921-232-c1dbad04315346a1b9ce3424c531d346", message_id=message_id)
    print(f"最终识别结果: {rsp}")
    assert len(rsp.result) > 0

if __name__ == "__main__":
    asyncio.run(test_srt_recognize_case2())