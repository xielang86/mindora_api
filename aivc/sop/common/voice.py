import os
import json
from mutagen.mp3 import MP3
from aivc.tts.manager import TTSManager, TTSType
from aivc.config.config import settings,L
import asyncio
import hashlib
import importlib


# 统一的配置文件映射表
CONFIG_MODULE_MAP = {
    '../sleep/config.py': 'aivc.sop.sleep.config',
    '../mindfulness/intro/config.py': 'aivc.sop.mindfulness.intro.config',
    '../mindfulness/mf1/config.py': 'aivc.sop.mindfulness.mf1.config',
    '../mindfulness/mf2/config.py': 'aivc.sop.mindfulness.mf2.config',
    '../mindfulness/mf3/config.py': 'aivc.sop.mindfulness.mf3.config',
}


def get_subdir_from_config(config_file_path):
    # 获取当前文件所在目录
    current_dir = os.path.dirname(__file__)
    
    # 如果config_file_path是以current_dir开头的绝对路径，移除这部分
    if config_file_path.startswith(current_dir):
        relative_path = config_file_path[len(current_dir):].lstrip('/')
    else:
        relative_path = config_file_path
    
    # 获取目录部分
    dir_path = os.path.dirname(relative_path)
    
    # 去除开头的 '../'
    if dir_path.startswith('../'):
        dir_path = dir_path[3:]
    
    return dir_path

def gen_file_name_from_text(text: str) -> str:
    hash_value = hashlib.md5(text.encode('utf-8')).hexdigest()
    file_name = f"{hash_value}.mp3"
    return file_name

class VoiceManager:
    def __init__(self):
        self.tts_type = TTSType.DoubaoLM
        self.compression_rate = 10
        self.speed_ratio = 0.8
        self.sound_dir = "/usr/local/src/seven_ai/aivoicechat/assets/sound"
        self.config_file = None
        self.voice_map = {}
        self._ensure_directories()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        if not os.path.exists(self.sound_dir):
            os.makedirs(self.sound_dir, exist_ok=True)
            L.debug(f"创建语音目录: {self.sound_dir}")

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

    async def gen_voice_files(self):
        if not os.path.exists(self.config_file):
            L.debug(f"配置文件不存在: {self.config_file}")
            return

        try:
            # 获取子目录
            subdir = get_subdir_from_config(self.config_file)
            if subdir:
                subdir = subdir + "/"
            else:
                subdir = ""
            
            # 读取配置文件内容
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            import re
            
            tts = TTSManager.create_tts(tts_type=self.tts_type)
            generated_count = 0
            skipped_count = 0
            
            # 分段处理，查找所有VoiceAction
            result = content
            pos = 0
            
            while True:
                # 查找下一个VoiceAction
                match = re.search(r'VoiceAction\s*\(', result[pos:])
                if not match:
                    break
                
                start_pos = pos + match.start()
                
                # 从VoiceAction开始位置找到对应的结束括号
                bracket_count = 0
                i = start_pos
                voice_action_start = start_pos
                
                while i < len(result):
                    if result[i] == '(':
                        bracket_count += 1
                    elif result[i] == ')':
                        bracket_count -= 1
                        if bracket_count == 0:
                            voice_action_end = i + 1
                            break
                    i += 1
                else:
                    # 没找到匹配的括号，跳过这个
                    pos = start_pos + len('VoiceAction(')
                    continue
                
                # 提取VoiceAction内容
                voice_action_content = result[voice_action_start:voice_action_end]
                
                # 提取text内容
                text_match = re.search(r'text\s*=\s*"([^"]*)"', voice_action_content)
                if not text_match:
                    pos = voice_action_end
                    continue
                
                text_content = text_match.group(1)
                if not text_content:
                    pos = voice_action_end
                    continue
                
                # 提取filename
                filename_match = re.search(r'filename\s*=\s*"([^"]*)"', voice_action_content)
                if not filename_match:
                    L.debug(f"VoiceAction缺少filename: {text_content[:50]}...")
                    pos = voice_action_end
                    continue
                
                filename = filename_match.group(1)
                if not filename:
                    pos = voice_action_end
                    continue
                
                # 添加子目录到filename
                filename = subdir + filename
                
                # 构建完整文件路径
                full_filename = os.path.join(self.sound_dir, filename)
                
                # 确保子目录存在
                subdir_path = os.path.dirname(full_filename)
                if not os.path.exists(subdir_path):
                    os.makedirs(subdir_path, exist_ok=True)
                    L.debug(f"创建子目录: {subdir_path}")
                
                # 检查文件是否已存在
                if os.path.exists(full_filename):
                    L.debug(f"文件已存在，跳过生成: {filename}")
                    self.voice_map[text_content] = filename
                    skipped_count += 1
                    pos = voice_action_end
                    continue
                
                # 生成语音文件
                L.debug(f"正在生成语音文件: {filename} - {text_content[:50]}...")
                try:
                    response = await tts.tts(
                        text=text_content,
                        audio_format="mp3",
                        compression_rate=self.compression_rate,
                        speed_ratio=self.speed_ratio
                    )
                    
                    if response.code == 0 and response.audio_path:
                        os.rename(response.audio_path, full_filename)
                        self.voice_map[text_content] = filename
                        generated_count += 1
                        L.debug(f"成功生成语音文件: {filename}")
                    else:
                        L.debug(f"生成语音失败: {filename} - {response.message}")
                        
                except Exception as e:
                    L.debug(f"生成语音文件时发生错误 {filename}: {e}")
                
                pos = voice_action_end

            L.debug(f"语音生成完成，成功生成 {generated_count} 个文件，跳过 {skipped_count} 个已存在文件")
            self.cleanup_unused_files()

        except Exception as e:
            L.debug(f"生成语音文件失败: {e}")
            import traceback
            L.debug(f"详细错误: {traceback.format_exc()}")
        
        L.debug(f"语音生成完成，成功生成 {generated_count} 个文件")
        self.cleanup_unused_files()

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

    def gen_voice_filename(self):
        if not os.path.exists(self.config_file):
            L.debug(f"配置文件不存在: {self.config_file}")
            return

        try:
            # 读取配置文件内容
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用正则表达式查找所有的VoiceAction
            import re
            
            modified = False
            
            # 分段处理，避免嵌套问题
            result = content
            pos = 0
            
            while True:
                # 查找下一个VoiceAction
                match = re.search(r'VoiceAction\s*\(', result[pos:])
                if not match:
                    break
                
                start_pos = pos + match.start()
                
                # 从VoiceAction开始位置找到对应的结束括号
                bracket_count = 0
                i = start_pos
                voice_action_start = start_pos
                
                while i < len(result):
                    if result[i] == '(':
                        bracket_count += 1
                    elif result[i] == ')':
                        bracket_count -= 1
                        if bracket_count == 0:
                            voice_action_end = i + 1
                            break
                    i += 1
                else:
                    # 没找到匹配的括号，跳过这个
                    pos = start_pos + len('VoiceAction(')
                    continue
                
                # 提取VoiceAction内容
                voice_action_content = result[voice_action_start:voice_action_end]
                
                # 提取text内容
                text_match = re.search(r'text\s*=\s*"([^"]*)"', voice_action_content)
                if not text_match:
                    pos = voice_action_end
                    continue
                
                text_content = text_match.group(1)
                if not text_content:
                    pos = voice_action_end
                    continue
                
                # 生成filename
                filename = gen_file_name_from_text(text_content)
                
                # 检查是否已经有filename，如果有则替换，没有则添加
                if 'filename=' in voice_action_content:
                    # 替换现有的filename
                    new_voice_action = re.sub(
                        r'filename\s*=\s*"[^"]*"',
                        f'filename="{filename}"',
                        voice_action_content
                    )
                    result = result[:voice_action_start] + new_voice_action + result[voice_action_end:]
                    modified = True
                    pos = voice_action_start + len(new_voice_action)
                else:
                    # 在VoiceAction的最后一个参数后添加filename
                    lines = voice_action_content.split('\n')
                    
                    # 找到最后一个有效参数行（不是空行也不是结束括号）
                    insert_index = -1
                    indent = ""
                    
                    for i in range(len(lines) - 1, -1, -1):
                        line = lines[i].strip()
                        if line and not line == ')' and not line.startswith(')'):
                            insert_index = i
                            # 获取缩进
                            for j in range(len(lines)):
                                if 'text=' in lines[j] or 'action=' in lines[j]:
                                    indent = lines[j][:len(lines[j]) - len(lines[j].lstrip())]
                                    break
                            break
                    
                    if insert_index >= 0:
                        # 确保前一行以逗号结尾
                        if not lines[insert_index].rstrip().endswith(','):
                            lines[insert_index] = lines[insert_index].rstrip() + ','
                        
                        # 插入filename行
                        filename_line = f'{indent}filename="{filename}"'
                        lines.insert(insert_index + 1, filename_line)
                        
                        # 替换原内容
                        new_voice_action = '\n'.join(lines)
                        result = result[:voice_action_start] + new_voice_action + result[voice_action_end:]
                        modified = True
                        
                        # 更新位置
                        pos = voice_action_start + len(new_voice_action)
                    else:
                        pos = voice_action_end

            # 如果有修改，写回文件
            if modified:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                L.debug("已更新配置文件中的filename")
            else:
                L.debug("没有需要更新的filename")

        except Exception as e:
            L.debug(f"更新配置文件失败: {e}")
            import traceback
            L.debug(f"详细错误: {traceback.format_exc()}")
    
    def gen_json_file(self):
        """生成JSON配置文件"""
        if not os.path.exists(self.config_file):
            L.debug(f"配置文件不存在: {self.config_file}")
            return

        try:
            # 获取子目录
            subdir = get_subdir_from_config(self.config_file)
            if subdir:
                subdir = subdir + "/"
            else:
                subdir = ""
            
            # 构建JSON文件名和路径
            filename = subdir + "config.json"
            full_filename = os.path.join(self.sound_dir, filename)
            
            # 确保子目录存在
            subdir_path = os.path.dirname(full_filename)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path, exist_ok=True)
                L.debug(f"创建子目录: {subdir_path}")
            
            # 根据配置文件路径确定要导入的模块
            module_name = None
            config_relative_path = os.path.relpath(self.config_file, os.path.dirname(__file__))
            
            # 标准化路径分隔符
            config_relative_path = config_relative_path.replace('\\', '/')
            
            # 查找匹配的模块名
            module_name = CONFIG_MODULE_MAP.get(config_relative_path)
            
            if not module_name:
                L.debug(f"未知的配置文件路径: {config_relative_path}")
                return
            
            # 动态导入模块并获取states_dict
            try:
                module = importlib.import_module(module_name)
                states_dict = getattr(module, 'states_dict')
            except (ImportError, AttributeError) as e:
                L.debug(f"导入模块失败 {module_name}: {e}")
                return
            
            # 将states_dict转换为可序列化的格式
            serializable_dict = {state.order: action for state, action in states_dict.items()}
            
            # 保存为JSON文件
            with open(full_filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_dict, default=lambda x: x.__dict__, indent=2, ensure_ascii=False, fp=f)
            
            L.debug(f"成功生成JSON配置文件: {full_filename}")
            
        except Exception as e:
            L.debug(f"生成JSON配置文件失败: {e}")
            import traceback
            L.debug(f"详细错误: {traceback.format_exc()}")

async def handler(config_file=None):
    # 如果没有提供config_file，使用默认的sleep配置文件
    if config_file is None:
        L.error("未提供配置文件路径，使用默认的sleep配置文件")
        raise ValueError("未提供配置文件路径")

    # 创建全局实例
    voice_manager = VoiceManager()
    voice_manager.config_file = os.path.join(os.path.dirname(__file__), config_file)

    L.debug(f"{config_file} 补充文件名...")
    voice_manager.gen_voice_filename()
    
    L.debug("生成JSON配置文件...")
    voice_manager.gen_json_file()
    
    L.debug("开始生成语音文件...")
    await voice_manager.gen_voice_files()

    L.debug("开始生成配置文件...")
    voice_manager.gen_json_file()

# 创建全局实例
voice_manager = VoiceManager()

async def process_configs():
    config_files = list(CONFIG_MODULE_MAP.keys())
    L.debug(f"开始按顺序处理 {len(config_files)} 个配置文件")
    
    for index, config_file in enumerate(config_files, 1):
        L.debug(f"[{index}/{len(config_files)}] 开始处理配置文件: {config_file}")
        await handler(config_file)
        L.debug(f"[{index}/{len(config_files)}] 完成处理配置文件: {config_file}")
    
    L.debug("所有配置文件处理完成")

if __name__ == "__main__":
    asyncio.run(process_configs())