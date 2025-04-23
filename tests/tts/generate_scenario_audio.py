import asyncio
import os
import shutil
from aivc.tts.manager import TTSManager, TTSType

# 定义场景文本
SCENARIOS = {
    "use_phone": [  # 玩手机场景
        "请放下手中的事物，现在你不需要思考任何问题。",
        "如果需要接听重要的电话，我们可以先暂停一下。我会在这里等你。",
        "请将双手自然的垂放在身体两侧，现你不需控制身体做任何动作。",
        "当你闭上眼睛，才能听见心的声音。",
        "你知道吗？手机的蓝光会影响睡眠，还会增加雀斑的形成哦。",
        "亲爱的请放下手机，安心的睡个好觉吧。",
        "相信我，一次完整的冥想体验可比手机有趣多了。"
    ],
    "sit_up": [  # 坐起场景
        "坐起身是想起有什么事情要做吗？不用着急，慢慢来。我在这里等你",
        "坐姿会让腰部肌肉持续紧张，躺下才能更好的放松身体哦。",
        "让我们专注当下，重新躺好，慢慢归位回到平和的状态。",
        "冥想是一个探索的过程，在过程中你可以随时调整姿势，让自己保持在舒适的状态。等你重新躺下，我们再继续探索。",
        "发生了什么让你感到坐卧不安呢？诉说也是很好的放松，我很愿意陪你聊聊天。不想说也没关系，你只需要静静平躺下来，让身体放松。",
        "舒适的姿势能够更好的帮助我们放松身心。我会等待你重新平躺下来。"
    ],
    "resume": [  # 恢复流程
        "那让我们继续将注意力带回到当下的空间里，感受呼吸带来的平静。",
        "让我们重新整理思绪，不管刚刚想了什么，现在都让它过去。",
        "请将注意力聚焦在自己的呼吸上，继续跟随我踏上今天的美好旅程 。",
        "让我们轻轻地闭上眼睛，觉察身体的细微感觉。感受自己的存在。",
        "现在，请闭上眼睛，抛开杂念，跟随声音的指引，引导你继续探寻内心深处的宁静。",
        "你不必在意刚刚的打断，请允许自己会被杂乱的思绪干扰。让我们闭上眼睛，调整呼吸，一点一点的拉回飘散的思绪。"
    ]
}

# 场景英文名称映射（用于文件命名）
SCENARIO_FILE_NAMES = {
    "use_phone": "use_phone",
    "sit_up": "sitting_up",
    "resume": "flow_resume"
}

async def generate_audio_for_scenario(scenario_key, tts_type=TTSType.DoubaoLM, 
                                     compression_rate=1, speed_ratio=0.8):
    """为特定场景生成语音文件"""
    
    tts = TTSManager.create_tts(tts_type=tts_type)
    
    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(__file__), "output/scenarios")
    os.makedirs(output_dir, exist_ok=True)
    
    scenario_texts = SCENARIOS[scenario_key]
    scenario_file_prefix = SCENARIO_FILE_NAMES[scenario_key]
    
    print(f"开始为场景「{scenario_key}」生成语音文件...")
    
    for i, text in enumerate(scenario_texts, 1):
        # 生成文件名 (使用英文加序号的格式)
        file_name = f"{scenario_file_prefix}_{i:02d}.mp3"
        file_path = os.path.join(output_dir, file_name)
        
        # 调用TTS生成语音
        response = await tts.tts(
            text=text,
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
                print(f"✓ 生成成功: {file_name}")
                print(f"  文件路径: {file_path}")
                print(f"  文件大小: {response.output_length} bytes")
                print(f"  处理耗时: {response.cost} ms")
            else:
                print(f"✗ 警告: 生成的音频文件不存在: {response.audio_path}")
        else:
            print(f"✗ 生成失败: {file_name}")
            print(f"  错误信息: {response.message}, 错误码: {response.code}")

async def main():
    """主函数，生成所有场景的语音文件"""
    
    # TTS参数
    tts_type = TTSType.DoubaoLM
    compression_rate = 1  # 压缩率
    speed_ratio = 0.8  # 语速
    
    print(f"开始生成场景语音，使用TTS类型: {tts_type.name}, 压缩率: {compression_rate}, 语速: {speed_ratio}")
    
    # 为每个场景生成语音
    for scenario in SCENARIOS.keys():
        await generate_audio_for_scenario(
            scenario, 
            tts_type=tts_type,
            compression_rate=compression_rate,
            speed_ratio=speed_ratio
        )
        print("-" * 50)
    
    print("所有场景语音文件生成完成！")

if __name__ == "__main__":
    asyncio.run(main())
