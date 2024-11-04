from aivc.utils.audio import calculate_pcm_duration,audio_file_to_base64

def test_calculate_pcm_duration(buffer):
    duration = calculate_pcm_duration(buffer)
    print(duration)
    assert duration > 0

def test_audio_file_to_base64(file_path: str) -> str:
    base64_str = audio_file_to_base64(file_path)
    print(base64_str)
    assert base64_str != ""

if __name__ == "__main__":
    filename = "/usr/local/src/seven_ai/aivoicechat/upload/20241029-101648-187-e4d00389eaf04885a81a3c389b0b376b"
    test_audio_file_to_base64(filename)
