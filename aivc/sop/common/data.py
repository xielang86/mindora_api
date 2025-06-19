from aivc.config.config import settings,L
import json
import os
from aivc.sop.common.common import Actions
from aivc.tts.manager import TTSManager, TTSType
import hashlib
from pydub import AudioSegment
import tempfile
from typing import Dict


def load_directory_data(path=settings.DIR_JSON_PATH):
    """加载目录数据"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return [{"name": f"加载目录数据失败: {str(e)}", "children": []}]

def save_directory_data(data, path=settings.DIR_JSON_PATH):
    """保存目录数据"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

def get_leaf_nodes_with_path(data):
    result = []
    
    def traverse(node, current_path=[]):
        path = current_path + [node['name']]
        
        # 检查是否为叶子节点（没有children或children为空）
        if 'children' not in node or not node['children']:
            result.append(path)
        else:
            # 继续遍历子节点
            for child in node['children']:
                traverse(child, path)
    
    # 开始遍历
    for root_node in data:
        traverse(root_node)
    
    return result

def get_commonds():
    path =  os.path.join(settings.DATA_DIR, "dir_en.json")
    data = load_directory_data(path)
    result = get_leaf_nodes_with_path(data)
    
    commands = []
    for item in result:
        if len(item) < 2:
            continue
        if item[0] == "meditation" and item[1] == "mindfulness":
            commands.append(".".join(item))

    return commands

def get_files():
    data = load_directory_data()
    result = get_leaf_nodes_with_path(data)

    files = []
    for item in result:
        if len(item) < 4:
            continue
        if item[0] == "冥想" and item[3] == "自然呼吸":
            file = settings.DATA_DIR + "/" + ">".join(item) + ".json"
            files.append(file)

    return files


def load_cn_to_en_mapping():
    """加载中英文映射数据"""
    try:
        with open(settings.DIR_CN_TO_EN, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        L.error(f"加载中英文映射文件失败: {str(e)}")
        return {}

def gen_file_name_from_text(text, english_name=None, action_index=None) -> str:
    """根据英文名称和动作索引生成文件名，如果没有则使用hash"""
    if english_name:
        # 使用英文名称生成文件名
        base_name = english_name.replace('.', '_')
        if action_index is not None:
            file_name = f"{base_name}_{action_index:03d}.mp3"
        else:
            file_name = f"{base_name}.mp3"
        return file_name
    else:
        # fallback到原来的hash方式
        if isinstance(text, list):
            text = ''.join(text)
        elif not isinstance(text, str):
            text = str(text)
        
        hash_value = hashlib.md5(text.encode('utf-8')).hexdigest()
        file_name = f"{hash_value}.mp3"
        return file_name

def _process_single_text(text: str) -> list[str]:
    """处理单条文本，直接返回原文本"""
    return [text]

def _process_text_list(texts: list[str]) -> list[str]:
    """处理文本列表，每个文本作为独立的语音片段"""
    return texts if texts else []

async def _generate_voice_file(tts, text: str, file_path: str, max_retries: int = 5) -> bool:
    """生成单个语音文件"""
    retry_count = 0
    success = False
    
    while retry_count < max_retries and not success:
        try:
            L.debug(f"正在生成语音文件 (尝试 {retry_count + 1}/{max_retries}): {os.path.basename(file_path)}")
            
            response = await tts.tts(
                text=text,
                audio_format="mp3",
                compression_rate=10,
                speed_ratio=0.8
            )

            if response.code == 0 and response.audio_path:
                # 将生成的文件重命名并移动到目标位置
                os.rename(response.audio_path, file_path)
                L.debug(f"成功生成语音文件: {os.path.basename(file_path)}")
                success = True
            else:
                L.warning(f"TTS生成失败: {response.message}")
                retry_count += 1
                
        except Exception as e:
            L.error(f"TTS调用异常: {str(e)}")
            retry_count += 1
    
    if not success:
        L.error(f"生成语音文件失败，已重试 {max_retries} 次: {os.path.basename(file_path)}")
    
    return success

def load_and_parse_json(file: str) -> tuple[dict, str]:
    """加载并解析JSON文件"""
    if not file:
        return None, "文件路径不能为空"
    
    if not os.path.exists(file):
        return None, f"文件不存在: {file}"
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return None, f"读取文件失败: {str(e)}"
    
    if not data:
        return None, "文件内容为空"
    
    return data, None

def parse_actions(data: dict) -> tuple[Dict[str, Actions], str]:
    """解析动作数据，返回process到Actions的映射"""
    result: Dict[str, Actions] = {}
    
    for process, action_data in data.items():
        try:
            actions = Actions(**action_data)
            actions.action_feature = process
            result[process] = actions
        except Exception as e:
            L.error(f"解析动作数据失败: {str(e)}, process: {process}")
            continue

    if not result:
        return None, "没有成功解析任何动作数据"
    
    return result, None

def _process_voice_text(voice) -> list[str]:
    """处理语音文本，返回文本片段列表"""
    if isinstance(voice.text, list):
        return _process_text_list(voice.text)
    else:
        return _process_single_text(voice.text)

def _generate_filenames(base_filename: str, text_count: int) -> list[str]:
    """生成文件名列表"""
    if text_count == 1:
        return [base_filename]
    
    base_name = base_filename.rsplit('.', 1)[0]  # 去掉扩展名
    return [f"{base_name}_{i+1:03d}.mp3" for i in range(text_count)]

async def _process_voice_texts(tts, voice, save_dir: str, english_name=None, action_index=None) -> bool:
    """处理单个voice的所有文本片段，合并为单个mp3文件"""
    # 使用新的文件名生成方式
    base_filename = gen_file_name_from_text(voice.text, english_name, action_index)
    final_path = os.path.join(save_dir, base_filename)
    
    # 如果文件已存在，跳过生成
    if os.path.exists(final_path):
        L.debug(f"文件已存在，跳过生成: {base_filename}")
        return True
    
    try:
        text_parts = _process_voice_text(voice)
        
        # 如果只有一个文本片段，直接生成
        if len(text_parts) == 1:
            return await _generate_voice_file(tts, text_parts[0], final_path)
        
        # 多个文本片段需要合并
        temp_files = []
        audio_segments = []
        
        # 为每个文本片段生成临时音频文件
        for i, text in enumerate(text_parts):
            print(f"Text Part {i+1}: {text}")
            print(f"Length: {len(text.encode('utf-8'))} bytes")
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            temp_files.append(temp_file.name)
            
            # 生成语音文件
            success = await _generate_voice_file(tts, text, temp_file.name)
            if not success:
                # 清理临时文件
                for temp_path in temp_files:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                return False
            
            # 加载音频片段
            audio_segment = AudioSegment.from_mp3(temp_file.name)
            audio_segments.append(audio_segment)
        
        # 合并音频片段
        final_audio = audio_segments[0]
        
        # 获取文本间隔时间（秒）
        interval_seconds = getattr(voice, 'text_interval', 0) or 0
        
        if interval_seconds > 0:
            # 创建静音片段
            silence = AudioSegment.silent(duration=int(interval_seconds * 1000))  # 转换为毫秒
            
            # 在片段间插入静音
            for audio_segment in audio_segments[1:]:
                final_audio = final_audio + silence + audio_segment
        else:
            # 直接连接，不插入静音
            for audio_segment in audio_segments[1:]:
                final_audio = final_audio + audio_segment
        
        # 导出最终音频文件
        final_audio.export(final_path, format="mp3")
        L.debug(f"成功合并音频文件: {base_filename}")
        
        # 清理临时文件
        for temp_path in temp_files:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return True
        
    except Exception as e:
        L.error(f"处理语音文本失败: {str(e)}")
        return False

async def file_tts(file=None):
    """处理文件转换为TTS"""
    # 1. 加载和解析JSON文件
    data, error = load_and_parse_json(file)
    if error:
        L.error(error)
        return {"error": error}

    # 2. 解析动作数据
    actions_list, error = parse_actions(data)
    if error:
        L.error(error)
        return {"error": error}

    # 3. 加载中英文映射
    cn_to_en_mapping = load_cn_to_en_mapping()
    
    # 4. 从文件路径提取key
    english_name = None
    if file and cn_to_en_mapping:
        try:
            # 提取文件路径中的key部分
            # 移除 settings.DATA_DIR 和 ".json"
            file_key = file.replace(settings.DATA_DIR + "/", "").replace(".json", "")
            english_name = cn_to_en_mapping.get(file_key)
            if english_name:
                L.debug(f"找到英文映射: {file_key} -> {english_name}")
            else:
                L.warning(f"未找到英文映射: {file_key}")
        except Exception as e:
            L.error(f"提取文件key失败: {str(e)}")

    # 5. 初始化TTS和目录
    tts = TTSManager.create_tts(tts_type=TTSType.DoubaoLM)
    save_dir = "/usr/local/src/seven_ai/aivoicechat/assets/sound"
    
    # 确保保存目录存在
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    # 6. 处理每个动作的语音数据
    for action_index, action in enumerate(actions_list, 1):
        for voice in action.voice.voices:
            if not hasattr(voice, 'text') or not voice.text:
                L.warning("语音数据中缺少文本内容")
                continue
            
            # 传递英文名称和动作索引
            await _process_voice_texts(tts, voice, save_dir, english_name, action_index)

    return actions_list


if __name__ == "__main__":
    import asyncio
    
    async def main():
        files = get_files()
        for file in files:
            print("file:", file)
            result = await file_tts(file)
    
    asyncio.run(main())
