from aivc.tts.manager import TTSManager, TTSType
import asyncio

async def test_tts(tts_type: TTSType = TTSType.DoubaoLM, compression_rate:int = 1, speed_ratio:float = 0.8):
    tts = TTSManager.create_tts(tts_type=tts_type)
    response = await tts.tts(
        text = "现在，让我们继续将注意力带回到呼吸上，感受呼吸带来的平静。",
        audio_format="mp3",
        compression_rate=compression_rate,
        speed_ratio=speed_ratio)
    if response.code == 0:
        print(f"TTS成功，音频文件保存在: {response.audio_path}, "
                f"音频数据大小: {response.output_length} bytes, "
                f"输入大小: {response.input_size} characters, "
                f"耗时: {response.cost} ms"
                f"compression_rate: {compression_rate}")
    else:
        print(f"TTS失败: {response.message}, 错误码: {response.code}")
    assert response.output_length > 0

if __name__ == "__main__":
    compression_rate = 10
    speed_ratio = 0.8
    asyncio.run(test_tts(
        tts_type=TTSType.DoubaoLM,
        compression_rate=compression_rate,
        speed_ratio=speed_ratio))
