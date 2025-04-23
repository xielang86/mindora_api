import asyncio
import os
import shutil
from aivc.tts.manager import TTSManager, TTSType
from aivc.common.task_class import QuestionType
from aivc.api.cmd_params import CmdParamsManager


async def generate_all_cmd_responses():
    """生成所有命令响应的语音文件"""
    
    # TTS参数
    tts_type = TTSType.DoubaoLM
    compression_rate = 1  # 压缩率
    speed_ratio = 0.8  # 语速
    
    # 获取命令参数管理器实例
    cmd_manager = CmdParamsManager.get_instance()
    
    print(f"开始生成命令响应语音，使用TTS类型: {tts_type.name}, 压缩率: {compression_rate}, 语速: {speed_ratio}")
    
    # 获取所有QuestionType
    question_types = list(QuestionType)
    success_count = 0
    skipped_count = 0
    
    # 遍历所有QuestionType，生成命令响应语音
    for question_type in question_types:
        if cmd_manager.is_cmd_question_type(question_type.value):
            result = await generate_audio_for_cmd_response(
                question_type,
                cmd_manager,
                tts_type=tts_type,
                compression_rate=compression_rate,
                speed_ratio=speed_ratio
            )
            if result:
                success_count += 1
            print("-" * 50)
        else:
            skipped_count += 1
    
    print(f"命令响应语音生成完成！成功: {success_count}, 跳过: {skipped_count}")


async def generate_audio_for_cmd_response(question_type: QuestionType, cmd_manager: CmdParamsManager,
                                         tts_type=TTSType.DoubaoLM, compression_rate=1, speed_ratio=0.8):
    """为特定命令类型生成语音响应文件"""
    
    # 获取响应文本和音频文件名
    response_text, audio_filename = cmd_manager.get_cmd_response(question_type.value)
    if not response_text:
        print(f"跳过 {question_type.name} - 不是命令类型或无响应文本")
        return False
    
    tts = TTSManager.create_tts(tts_type=tts_type)
    
    # 确保输出目录存在
    output_dir = "/usr/local/src/seven_ai/aivoicechat/assets/cmd_rsp"
    os.makedirs(output_dir, exist_ok=True)
    
    # 使用返回的文件名
    file_path = os.path.join(output_dir, audio_filename)
    
    print(f"正在为命令「{question_type.name}」生成语音响应...")
    print(f"响应文本: '{response_text}'")
    print(f"音频文件: '{audio_filename}'")
    
    # 调用TTS生成语音
    response = await tts.tts(
        text=response_text,
        audio_format="mp3",
        compression_rate=compression_rate,
        speed_ratio=speed_ratio
    )
    
    if response.code == 0:
        # 将生成的音频文件从临时位置移动到目标路径
        if os.path.exists(response.audio_path):
            # 如果目标文件已存在，先删除
            if os.path.exists(file_path):
                os.remove(file_path)
            # 移动文件
            shutil.move(response.audio_path, file_path)
            print(f"✓ 生成成功: {audio_filename}")
            print(f"  文件路径: {file_path}")
            print(f"  文件大小: {response.output_length} bytes")
            print(f"  处理耗时: {response.cost} ms")
            return True
        else:
            print(f"✗ 警告: 生成的音频文件不存在: {response.audio_path}")
            return False
    else:
        print(f"✗ 生成失败: {audio_filename}")
        print(f"  错误信息: {response.message}, 错误码: {response.code}")
        return False


async def main():
    await generate_all_cmd_responses()


if __name__ == "__main__":
    asyncio.run(main())
