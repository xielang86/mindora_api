from enum import Enum
import hashlib
import os
from typing import Dict, List, Tuple, Callable, Any
import asyncio
from aivc.common.sleep_common import (
    Actions, FragranceAction, LightAction, VoiceAction, BgmAction, 
    VoiceSequence, MediaAction, FragranceStatus, LightMode
)
from aivc.tts.manager import TTSManager, TTSType
from aivc.config.config import settings, L

class AlertLevel(Enum):
    NORMAL = -1  # 完全恢复正常状态
    L0 = 0  # 最轻微异常，恢复流程，提供引导语音
    L1 = 1  # 轻微异常，暂停引导但保持当前场景设置  
    L2 = 2  # 中等异常，暂停引导，降低音量，添加提示音
    L3 = 3  # 严重异常，暂停引导，降低音量，停止香氛，切换灯光，语音询问
    L4 = 4  # 致命异常，终止退出，关闭所有设备

class SleepAlert:
    """睡眠状态异常检测与响应"""
    
    @staticmethod
    def create_alert_actions(level: AlertLevel) -> Actions:
        """
        根据告警级别创建相应的动作配置
        
        Args:
            level: 告警级别
            
        Returns:
            Actions: 告警动作配置
        """
        if level == AlertLevel.L0:
            return SleepAlert.create_l0_actions()
        elif level == AlertLevel.L1:
            return SleepAlert.create_l1_actions()
        elif level == AlertLevel.L2:
            return SleepAlert.create_l2_actions()
        elif level == AlertLevel.L3:
            return SleepAlert.create_l3_actions()
        elif level == AlertLevel.L4:
            return SleepAlert.create_l4_actions()
        else:
            return None
    
    @staticmethod
    def create_l0_actions() -> Actions:
        """
        L0级别告警动作：
        - 引导语音：无
        - 音乐：播放（断点场景音乐）
        - 香氛：持续（断点场景设置）
        - 灯光：持续（断点场景设置）
        - 提示响应："恢复流程语音'你不必在意刚刚的打断，请允许自己会被杂乱的思绪干扰。让我们试着调整呼吸，一点一点的拉回飘散的思绪。'"
        """
        return Actions(
            voice=VoiceSequence(
                voices=[
                    VoiceAction(
                        action="play",
                        text="你不必在意刚刚的打断，请允许自己会被杂乱的思绪干扰。让我们试着调整呼吸，一点一点的拉回飘散的思绪。",
                        filename="ALERT_L0_b0d843c12bcb285548ac69076b2c883e.mp3"
                    )
                ]
            ),
            action_feature="alert_level_0"
        )
    
    @staticmethod
    def create_l1_actions() -> Actions:
        """
        L1级别告警动作：
        - 引导语音：暂停引导（当前句结束）
        - 音乐：持续（当前场景音乐）
        - 香氛：持续（当前场景设置）
        - 灯光：持续（当前场景灯光模式）
        - 提示响应：无
        """

        return Actions(
            voice=VoiceSequence(
                voices=[VoiceAction(action="stop")]
            ),
            action_feature="alert_level_1"
        )
    
    @staticmethod
    def create_l2_actions() -> Actions:
        """
        L2级别告警动作：
        - 引导语音：暂停（当前句结束）
        - 音乐：音量-20（当前场景音乐）
        - 香氛：持续（当前场景设置）
        - 灯光：持续（当前场景灯光模式）
        - 提示响应：钵音敲击提醒
        """
                 
        return Actions(
            voice=VoiceSequence(
                voices=[
                    VoiceAction(action="stop")
                ]),
            bgm=BgmAction(
                action=MediaAction.PLAY,
                volume=-20,
                filename="bowl_sound.mp3"
            ),
            action_feature="alert_level_2"
        )
    
    @staticmethod
    def create_l3_actions() -> Actions:
        """
        L3级别告警动作：
        - 引导语音：暂停（当前句结束）
        - 音乐：音量-20（当前场景音乐）
        - 香氛：停止
        - 灯光：对话模式（亮度同场景）
        - 提示响应："语音询问"今天的你似乎不在状态呢，需要帮您结束引导吗？""
        """        
        return Actions(
            voice=VoiceSequence(
                voices=[
                    VoiceAction(
                        action="play",
                        text="今天的你似乎不在状态呢，需要帮您结束引导吗？",
                        filename="ALERT_L3_493e6c8c13a0eda3e154ba6ce0eb9191.mp3"
                    )
                ]),
            bgm=BgmAction(action=MediaAction.PLAY, volume=-20),
            fragrance=FragranceAction(status=FragranceStatus.OFF),
            light=LightAction(mode=LightMode.BREATHING, rgb="rgb(255,255,255)"),
            action_feature="alert_level_3"
        )
    
    @staticmethod
    def create_l4_actions() -> Actions:
        """
        L4级别告警动作：
        - 引导语音：停止（终止退出）
        - 音乐：减弱关闭
        - 香氛：关闭
        - 灯光：待机模式
        - 提示响应：无
        """
        return Actions(
            voice=VoiceSequence(voices=[VoiceAction(action="stop")]),
            bgm=BgmAction(action=MediaAction.FADE_OUT),
            fragrance=FragranceAction(status=FragranceStatus.OFF),
            light=LightAction(mode=LightMode.STATIC, rgb="rgb(5,5,5)"),
            action_feature="alert_level_4",
        )    
     
    @staticmethod
    async def generate_voice_files() -> Dict[str, str]:
        """
        遍历所有告警级别，找到包含语音文本的VoiceAction，生成语音文件
        
        Args:
            output_dir: 语音文件输出目录，如果为None则使用默认配置
            
        Returns:
            Dict[str, str]: 字典，键为生成的文件名，值为原始文本
        """
        output_dir = settings.SOUND_DIR
        os.makedirs(output_dir, exist_ok=True)
        result = {}
        generated_files = {}
        voice_map = {}
        
        print("开始生成睡眠告警语音文件:")
        
        # 初始化TTS
        tts_type = TTSType.DoubaoLM  # 使用豆包大模型
        compression_rate = 10
        speed_ratio = 0.8
        
        try:
            tts = TTSManager.create_tts(tts_type=tts_type)
            print(f"已初始化TTS引擎: {tts_type.name}")
        except Exception as e:
            print(f"初始化TTS引擎失败: {str(e)}")
            return {}
        
        # 遍历所有告警级别
        for level in AlertLevel:
            print(f"\n处理{level.name}级别告警...")
            actions = SleepAlert.create_alert_actions(level)
            
            # 检查是否有语音序列
            if actions.voice and actions.voice.voices:
                for voice_action in actions.voice.voices:
                    if voice_action.text:
                        # 生成文件名：使用文本的哈希作为文件名基础
                        text = voice_action.text
                        hash_value = hashlib.md5(text.encode('utf-8')).hexdigest()
                        filename = f"ALERT_{level.name}_{hash_value}.mp3"
                        file_path = os.path.join(output_dir, filename)
                        
                        print(f"  - 文本: {text}")
                        print(f"  - 文件: {file_path}")
                        
                        # 检查文件是否已存在
                        if os.path.exists(file_path):
                            print(f"  - 文件已存在，跳过生成")
                            voice_map[text] = filename
                            generated_files[filename] = text
                            
                            # 更新voice_action
                            voice_action.filename = filename
                            voice_action.text = None
                            continue
                        
                        # 生成语音文件
                        try:
                            response = await tts.tts(
                                text=text,
                                audio_format="mp3",
                                compression_rate=compression_rate,
                                speed_ratio=speed_ratio
                            )
                            
                            if response.code == 0 and response.audio_path:
                                # 移动生成的文件到目标位置
                                os.rename(response.audio_path, file_path)
                                print(f"  - 生成成功")
                                
                                # 记录映射
                                voice_map[text] = filename
                                generated_files[filename] = text
                                
                                # 更新voice_action
                                voice_action.filename = filename
                                voice_action.text = None
                            else:
                                print(f"  - 生成失败: {response.message}")
                                
                        except Exception as e:
                            print(f"  - 生成失败: {str(e)}")
                            
                        # 如果该级别还不在结果中，则添加
                        if level.name not in result:
                            result[level.name] = []
                            
                        result[level.name].append((text, file_path))
            else:
                print(f"  - 无语音文本")
        
        # 保存语音映射
        voice_map_file = os.path.join(output_dir, 'alert_voice_map.json')
        try:
            import json
            with open(voice_map_file, 'w', encoding='utf-8') as f:
                json.dump(voice_map, f, ensure_ascii=False, indent=2)
            print(f"\n语音映射已保存到: {voice_map_file}")
        except Exception as e:
            print(f"保存语音映射失败: {str(e)}")
                
        print("\n语音文件生成总结:")
        print(f"总共生成了 {len(generated_files)} 个文件")
        for level_name, files in result.items():
            print(f"{level_name}级别: {len(files)}个文件")
            
        return generated_files


# 添加一个主函数用于测试
async def main():
    print("开始生成所有告警级别的语音文件...")
    await SleepAlert.generate_voice_files()
    print("语音文件生成完成!")

if __name__ == "__main__":
    asyncio.run(main())