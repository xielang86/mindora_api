from aivc.srt.manager import SRTManager, SRTType
import asyncio

async def test_srt_recognize(srt_type: SRTType = SRTType.XUNFEI):
    srt = SRTManager.create_srt(srt_type=srt_type)
    rsp = await srt.recognize(audio_path="/Users/gaochao/Downloads/iat_pcm_16k.pcm")
    print(f"最终识别结果: {rsp}")
    assert len(rsp.result) > 0

if __name__ == "__main__":
    asyncio.run(test_srt_recognize())