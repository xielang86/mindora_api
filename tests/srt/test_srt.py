from aivc.srt.manager import SRTManager, SRTType
import asyncio
from aivc.utils.id import get_message_id

async def test_srt_recognize(srt_type: SRTType = SRTType.XUNFEI, audio_path: str = "/Users/gaochao/Downloads/iat_pcm_16k.pcm"):
    message_id = get_message_id()
    srt = SRTManager.create_srt(srt_type=srt_type)
    rsp = await srt.recognize(audio_path=audio_path, message_id=message_id)
    print(f"最终识别结果: {rsp}")
    assert len(rsp.text) > 0

async def test_xunfei_recognition():
    await test_srt_recognize(SRTType.XUNFEI)

async def test_doubao_recognition():
    audio_path = "/usr/local/src/seven_ai/aivoicechat/upload/20250311-122921-232-c1dbad04315346a1b9ce3424c531d346"
    await test_srt_recognize(SRTType.DOUBAO, audio_path)

async def test_google_recognition():
    await test_srt_recognize(SRTType.GOOGLE)

async def test_microsoft_recognition():
    audio_path = "/Users/gaochao/Downloads/iat_pcm_16k.wav"
    await test_srt_recognize(SRTType.MICROSOFT,audio_path)

if __name__ == "__main__":
    asyncio.run(test_microsoft_recognition())