import os
import json
from mutagen.mp3 import MP3
from aivc.tts.manager import TTSManager, TTSType
from aivc.common.sleep_config import states_dict
from aivc.config.config import settings,L
import asyncio
import hashlib

class VoiceManager:
    def __init__(self):
        self.tts_type = TTSType.DoubaoLM
        self.compression_rate = 10
        self.speed_ratio = 0.8
        self.sound_dir = settings.SOUND_DIR
        self.voice_map_file = os.path.join(self.sound_dir, 'voice_map.json')
        self.voice_map = {}
        self._ensure_directories()
        self._load_voice_map()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        if not os.path.exists(self.sound_dir):
            os.makedirs(self.sound_dir, exist_ok=True)
            L.debug(f"创建语音目录: {self.sound_dir}")

    def _load_voice_map(self):
        """加载或初始化语音映射文件"""
        try:
            if os.path.exists(self.voice_map_file):
                with open(self.voice_map_file, 'r', encoding='utf-8') as f:
                    self.voice_map = json.load(f)
                    L.debug(f"已加载现有语音映射，包含 {len(self.voice_map)} 条记录")
            else:
                L.debug("语音映射文件不存在，将创建新的映射")
                self.voice_map = {}
        except Exception as e:
            L.debug(f"加载语音映射文件失败: {e}")
            self.voice_map = {}

    def _save_voice_map(self):
        """保存语音映射到文件"""
        os.makedirs(self.sound_dir, exist_ok=True)
        with open(self.voice_map_file, 'w', encoding='utf-8') as f:
            json.dump(self.voice_map, f, ensure_ascii=False, indent=2)

    def cleanup_unused_files(self):
        """清理不在voice_map中的语音文件"""
        if not os.path.exists(self.sound_dir):
            return
            
        # 获取所有使用中的文件名
        used_files = set(self.voice_map.values())
        
        # 遍历目录中的所有mp3文件
        for filename in os.listdir(self.sound_dir):
            if filename.endswith('.mp3'):
                if filename not in used_files:
                    try:
                        file_path = os.path.join(self.sound_dir, filename)
                        os.remove(file_path)
                        L.debug(f"删除未使用的语音文件: {filename}")
                    except OSError as e:
                        L.debug(f"删除文件失败 {filename}: {e}")

    async def generate_all_voice_files(self):
        """遍历states_dict生成所有语音文件"""
        if not states_dict:
            L.debug("警告: states_dict 为空!")
            return

        L.debug(f"开始处理 {len(states_dict)} 个状态的语音生成")
        tts = TTSManager.create_tts(tts_type=self.tts_type)
        generated_count = 0
        
        for state_type, actions in states_dict.items():
            try:
                if not hasattr(actions, 'voice') or not actions.voice:
                    L.debug(f"跳过 {state_type}: 没有voice属性或voice为空")
                    continue

                # 处理每个voice sequence中的所有voice action
                for voice_action in actions.voice.voices:
                    if not voice_action or not voice_action.text:
                        continue

                    text = voice_action.text
                    hash_value = hashlib.md5(text.encode('utf-8')).hexdigest()
                    file_name = f"{state_type.name}_{hash_value}.mp3"
                    file_path = os.path.join(self.sound_dir, file_name)

                    if os.path.exists(file_path):
                        L.debug(f"文件已存在，跳过生成: {file_path}")
                        self.voice_map[text] = file_name  # 只存储文件名
                        generated_count += 1
                        continue

                    L.debug(f"正在为状态 {state_type.name} 生成语音: {text}")
                    response = await tts.tts(
                        text=text,
                        audio_format="mp3",
                        compression_rate=self.compression_rate,
                        speed_ratio=self.speed_ratio
                    )
                    
                    if response.code == 0 and response.audio_path:
                        os.rename(response.audio_path, file_path)
                        self.voice_map[text] = file_name  # 只存储文件名
                        generated_count += 1
                        L.debug(f"成功生成语音文件: {file_path}")
                    else:
                        L.debug(f"生成语音失败 {state_type.name}: {response.message}")

            except Exception as e:
                L.debug(f"处理状态 {state_type.name} 时发生错误: {e}")
        
        L.debug(f"语音生成完成，成功生成 {generated_count} 个文件")
        self._save_voice_map()
        self.cleanup_unused_files()
        self.check_voice_mapping()

    def get_voice_file(self, text: str) -> str:
        """根据文本内容查找对应的语音文件"""
        filename = self.voice_map.get(text)
        if filename:
            return os.path.join(self.sound_dir, filename)
        return None

    def get_voice_time(self, text: str) -> float:
        """获取语音文件的播放时长（秒）
        
        Args:
            text: 语音文本内容
            
        Returns:
            float: 音频时长（秒），如果文件不存在则返回 0
        """
        file_path = self.get_voice_file(text)
        if not file_path or not os.path.exists(file_path):
            return 0
            
        try:
            audio = MP3(file_path)
            return audio.info.length
        except Exception as e:
            L.debug(f"获取音频时长失败: {e}")
            return 0

    def check_voice_mapping(self):
        """检查voice_map文件中的映射和states_dict中VoiceAction的filename是否一致"""
        # 读取最新的映射内容
        try:
            with open(self.voice_map_file, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            L.debug("成功读取voice_map文件内容")
        except Exception as e:
            L.debug(f"读取voice_map文件失败: {e}")
            return

        # 遍历states_dict中的所有VoiceAction
        from aivc.common.sleep_config import states_dict
        for state, actions in states_dict.items():
            if not hasattr(actions, 'voice') or not actions.voice:
                continue
            for voice_action in actions.voice.voices:
                text = voice_action.text
                expected_filename = voice_action.filename
                mapped_filename = mapping.get(text)
                if mapped_filename is None:
                    L.debug(f"[缺失映射] 状态 {state.name} 文本: '{text}' 未在voice_map中找到。")
                elif mapped_filename != expected_filename:
                    L.debug(f"[不匹配] 状态 {state.name} 文本: '{text}' 映射值: '{mapped_filename}' 与预期: '{expected_filename}' 不一致。")
                else:
                    pass
 
# 创建全局实例
voice_manager = VoiceManager()

async def main():
    L.debug("开始生成语音文件...")
    await voice_manager.generate_all_voice_files()
    L.debug(f"语音文件生成完成，映射关系已保存到: {voice_manager.voice_map_file}")
    L.debug(f"当前语音映射数量: {len(voice_manager.voice_map)}")

if __name__ == "__main__":
    asyncio.run(main())