import gradio as gr
import json
import os
from aivc.sop.common.common import LightMode
from aivc.config.config import settings,L

KEY = "rDpnG2BvetY2PhJYdtyL"

def verify_key(key):
    """验证key是否正确"""
    return key == KEY

def save_json_data(filepath, data):
    """保存JSON文件数据"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, "保存成功"
    except Exception as e:
        return False, f"保存失败: {str(e)}"

def load_json_data(filepath):
    """加载JSON文件数据"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return None
    except Exception as e:
        L.debug(f"Error loading JSON file {filepath}: {e}")
        return None

def populate_template1(data):
    """填充模板1数据 - 共享配置"""
    result = {
        'video_filename': '',
        'bgm_filename': '',
        'light_mode': '',
        'light_rgb': '',
        'fragrance_count': 0,
        'processes': []
    }

    if not data:
        return result

    L.debug(f"Processing template1 data with {len(data)} processes")

    # 只取第一个流程的配置作为共享配置
    process_names = list(data.keys())
    if process_names:
        first_process_name = process_names[0]
        actions = data.get(first_process_name, {})
        # 提取display配置
        if actions.get('display') and actions['display'].get('filename'):
            result['video_filename'] = actions['display']['filename']
            L.debug(f"Found shared video: {result['video_filename']}")
        # 提取bgm配置
        if actions.get('bgm') and actions['bgm'].get('filename'):
            result['bgm_filename'] = actions['bgm']['filename']
            L.debug(f"Found shared bgm: {result['bgm_filename']}")
        # 提取light配置
        if actions.get('light') and actions['light'] is not None:
            light_mode = actions['light'].get('mode') if actions['light'] else None
            _mode_labels = {
                "Off": "关闭灯光",
                "Breathing": "呼吸模式", 
                "Shadowing": "拖影模式",
                "Gradient": "渐变模式",
                "Static": "静态模式"
            }
            if light_mode:
                if light_mode in _mode_labels:
                    result['light_mode'] = f"{light_mode}（{_mode_labels[light_mode]}）"
                else:
                    result['light_mode'] = light_mode
                L.debug(f"Found shared light mode: {result['light_mode']}")
            if actions['light'].get('rgb'):
                result['light_rgb'] = actions['light']['rgb']
                L.debug(f"Found shared light rgb: {result['light_rgb']}")
        # 提取fragrance配置
        if actions.get('fragrance') and actions['fragrance'] is not None:
            fragrance = actions['fragrance']
            if fragrance.get('count') is not None:
                result['fragrance_count'] = fragrance['count']
                L.debug(f"Found shared fragrance count: {result['fragrance_count']}")

    # 保持JSON中的流程顺序
    L.debug(f"Process names in order: {process_names}")

    for process_name in process_names:
        actions = data.get(process_name)
        if isinstance(actions, dict):
            voice_config = actions.get('voice')
            if voice_config and voice_config.get('voices'):
                voices_list = voice_config['voices']
                if voices_list and len(voices_list) > 0:
                    first_voice = voices_list[0]
                    text_content = first_voice.get('text', '')
                    if isinstance(text_content, list):
                        combined_text = '\n'.join(text_content)
                    else:
                        combined_text = text_content or ''
                    text_interval = first_voice.get('text_interval')
                    if text_interval is None:
                        text_interval = 0
                    wait_time = first_voice.get('wait_time')
                    if wait_time is None:
                        wait_time = 0
                    process_info = {
                        'name': process_name,
                        'text_interval': text_interval,
                        'wait_time': wait_time,
                        'text': combined_text
                    }
                    result['processes'].append(process_info)

    L.debug(f"Template1 result: video={result['video_filename']}, bgm={result['bgm_filename']}, processes={len(result['processes'])}")
    return result

def populate_template2(data):
    """填充模板2数据 - 独立配置"""
    result = {'processes': []}
    
    if not data:
        return result
    
    L.debug(f"Processing template2 data with {len(data)} processes")
    
    _mode_labels = {
        "Off": "关闭灯光",
        "Breathing": "呼吸模式",
        "Shadowing": "拖影模式", 
        "Gradient": "渐变模式",
        "Static": "静态模式"
    }
    
    # 保持JSON中的流程顺序
    process_names = list(data.keys())
    L.debug(f"Template2 process names in order: {process_names}")
    
    # 按原始JSON中的顺序处理每个流程
    for process_name in process_names:
        actions = data.get(process_name)
        if isinstance(actions, dict):
            # 提取voice配置
            voice_config = actions.get('voice')
            combined_text = ''
            text_interval = 0
            wait_time = 0
            
            if voice_config and voice_config.get('voices'):
                voices_list = voice_config['voices']
                if voices_list and len(voices_list) > 0:
                    first_voice = voices_list[0]
                    
                    # 处理text字段
                    text_content = first_voice.get('text', '')
                    if isinstance(text_content, list):
                        combined_text = '\n'.join(text_content)
                    else:
                        combined_text = text_content or ''
                    
                    # 修复：正确处理null值
                    text_interval = first_voice.get('text_interval')
                    if text_interval is None:
                        text_interval = 0
                    
                    wait_time = first_voice.get('wait_time')
                    if wait_time is None:
                        wait_time = 0
            
            # 提取其他独立配置
            display_config = actions.get('display')
            bgm_config = actions.get('bgm')
            light_config = actions.get('light')
            fragrance_config = actions.get('fragrance')
            
            # 处理灯光模式
            light_mode = ''
            if light_config and light_config.get('mode'):
                mode = light_config['mode']
                if mode in _mode_labels:
                    light_mode = f"{mode}（{_mode_labels[mode]}）"
                else:
                    light_mode = mode
            
            process_info = {
                'name': process_name,
                'text_interval': text_interval,
                'wait_time': wait_time,
                'text': combined_text,
                'video_filename': display_config.get('filename', '') if display_config else '',
                'bgm_filename': bgm_config.get('filename', '') if bgm_config else '',
                'light_mode': light_mode,
                'light_rgb': light_config.get('rgb', '') if light_config else '',
                'fragrance_count': fragrance_config.get('count', 0) if fragrance_config else 0
            }
            result['processes'].append(process_info)
    
    L.debug(f"Template2 result: {len(result['processes'])} processes")
    return result

def create_detail_components():
    """创建详情页面的UI组件"""
    # 在函数开始时初始化所有变量
    video_filename = None
    bgm_filename = None
    light_mode = None
    light_rgb = None
    fragrance_count = None
    
    # 创建Tab容器
    with gr.Tabs(visible=False) as detail_tabs:
        # 模板1 - 流程共享配置
        with gr.Tab("模板1 - 共享配置") as template1_tab:
            # —— 视频 和 音乐 (并排显示) ——
            submit_actions_top = gr.Button("🚀 提交", variant="primary", visible=True)
            
            # 添加保存状态提示
            save_status_top = gr.Markdown("", visible=True)
            actions_output_top = gr.JSON(label="Actions JSON", visible=False)
            
            with gr.Row() as media_config_row:
                with gr.Column():
                    video_filename = gr.Textbox(
                        label="🎬 视频文件名", 
                        visible=True, 
                        interactive=True,
                        value=""
                    )
                with gr.Column():
                    bgm_filename = gr.Textbox(
                        label="🎵 音乐文件名", 
                        visible=True, 
                        interactive=True,
                        value=""
                    )
            
            # —— 灯光 和 香氛 (并排显示) ——
            with gr.Row() as light_fragrance_config_row:
                with gr.Column():
                    _mode_labels = {
                        "Off": "关闭灯光",
                        "Breathing": "呼吸模式",
                        "Shadowing": "拖影模式",
                        "Gradient": "渐变模式",
                        "Static": "静态模式"
                    }
                    light_mode = gr.Dropdown(
                        choices=[f"{m.value}（{_mode_labels.get(m.value, '')}）" for m in LightMode],
                        label="💡 灯光模式",
                        visible=True,
                        allow_custom_value=True,
                        value=None
                    )
                    light_rgb = gr.Textbox(
                        label="💡 RGB 值",
                        placeholder="例如: rgb(255, 255, 255)",
                        visible=True
                    )
                with gr.Column():
                    fragrance_count = gr.Number(label="🌸 香氛次数", visible=True)

            # —— 流程 ——
            voice_section = gr.Markdown("### 🗣️ 流程", visible=True)
            
            # 创建多个流程组件（支持30个）
            voice_procs = []
            text_intervals = []  
            proc_intervals = []
            voice_texts = []
            proc_headers = []
            
            for i in range(30):
                proc_header = gr.HTML(
                    f'''<div style="
                        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                        color: #0c4a6e; 
                        padding: 10px 16px; 
                        border-radius: 8px; 
                        margin: 15px 0 10px 0; 
                        font-weight: 600; 
                        font-size: 16px; 
                        text-align: center;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        border: 2px solid #0ea5e9;
                    ">
                        🎯 序号 {i+1}
                    </div>''',
                    visible=True
                )
                proc_headers.append(proc_header)
                
                with gr.Row():
                    voice_proc = gr.Textbox(label="流程名", visible=True)
                    text_interval = gr.Number(label="文字间隔时间 (s)", visible=True)
                    proc_interval = gr.Number(label="流程间隔时间 (s)", visible=True)
                voice_text = gr.Textbox(label="文字内容", lines=4, max_lines=1000, visible=True)
                
                voice_procs.append(voice_proc)
                text_intervals.append(text_interval)
                proc_intervals.append(proc_interval)
                voice_texts.append(voice_text)
            
            submit_actions = gr.Button("🚀 提交", variant="primary", visible=True)
            
            # 添加保存状态提示
            save_status = gr.Markdown("", visible=True)
            actions_output = gr.JSON(label="Actions JSON", visible=False)

        # 模板2 - 独立配置
        with gr.Tab("模板2 - 独立配置") as template2_tab:
            submit_actions_top_t2 = gr.Button("🚀 提交", variant="primary", visible=True)
            
            # 添加保存状态提示
            save_status_top_t2 = gr.Markdown("", visible=True)
            actions_output_top_t2 = gr.JSON(label="Actions JSON", visible=False)
            
            # 创建30个独立流程配置
            t2_voice_procs = []
            t2_voice_texts = []
            t2_text_intervals = []
            t2_proc_intervals = []
            t2_video_filenames = []
            t2_bgm_filenames = []
            t2_light_modes = []
            t2_light_rgbs = []
            t2_fragrance_counts = []
            t2_proc_headers = []
            
            for i in range(30):
                proc_header = gr.HTML(
                    f'''<div style="
                        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                        color: #0c4a6e; 
                        padding: 10px 16px; 
                        border-radius: 8px; 
                        margin: 15px 0 10px 0; 
                        font-weight: 600; 
                        font-size: 16px; 
                        text-align: center;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        border: 2px solid #0ea5e9;
                    ">
                        🎯 序号 {i+1}
                    </div>''',
                    visible=True
                )
                t2_proc_headers.append(proc_header)
                
                with gr.Row():
                    voice_proc = gr.Textbox(label="流程名", visible=True)
                    text_interval = gr.Number(label="文字间隔时间 (s)", visible=True)
                    proc_interval = gr.Number(label="流程间隔时间 (s)", visible=True)
                voice_text = gr.Textbox(label="文字内容", lines=3, max_lines=1000, visible=True)
                
                # 媒体配置
                with gr.Row():
                    video_filename_t2 = gr.Textbox(label="🎬 视频文件名", visible=True)
                    bgm_filename_t2 = gr.Textbox(label="🎵 音乐文件名", visible=True)
                
                # 灯光和香氛配置
                with gr.Row():
                    with gr.Column():
                        light_mode_t2 = gr.Dropdown(
                            choices=[f"{m.value}（{_mode_labels.get(m.value, '')}）" for m in LightMode],
                            label="💡 灯光模式",
                            visible=True,
                            allow_custom_value=True,
                            value=None
                        )
                        light_rgb_t2 = gr.Textbox(
                            label="💡 RGB 值",
                            placeholder="例如: rgb(255, 255, 255)",
                            visible=True
                        )
                    with gr.Column():
                        fragrance_count_t2 = gr.Number(label="🌸 香氛次数", visible=True)
                
                t2_voice_procs.append(voice_proc)
                t2_voice_texts.append(voice_text)
                t2_text_intervals.append(text_interval)
                t2_proc_intervals.append(proc_interval)
                t2_video_filenames.append(video_filename_t2)
                t2_bgm_filenames.append(bgm_filename_t2)
                t2_light_modes.append(light_mode_t2)
                t2_light_rgbs.append(light_rgb_t2)
                t2_fragrance_counts.append(fragrance_count_t2)
            
            submit_actions_t2 = gr.Button("🚀 提交", variant="primary", visible=True)
            
            # 添加保存状态提示
            save_status_t2 = gr.Markdown("", visible=True)
            actions_output_t2 = gr.JSON(label="Actions JSON", visible=False)
    
    # 验证所有关键组件是否正确创建
    if any(comp is None for comp in [video_filename, bgm_filename, light_mode, light_rgb, fragrance_count]):
        raise ValueError("Components not created properly!")
    
    # 返回组件引用，添加保存状态组件
    return {
        'detail_tabs': detail_tabs,
        'submit_actions_top': submit_actions_top,
        'save_status_top': save_status_top,
        'actions_output_top': actions_output_top,
        'media_config_row': media_config_row,
        'video_filename': video_filename,
        'bgm_filename': bgm_filename,
        'light_fragrance_config_row': light_fragrance_config_row,
        'light_mode': light_mode,
        'light_rgb': light_rgb,
        'fragrance_count': fragrance_count,
        'voice_section': voice_section,
        'proc_headers': proc_headers,
        'voice_procs': voice_procs,
        'text_intervals': text_intervals,
        'proc_intervals': proc_intervals,
        'voice_texts': voice_texts,
        'submit_actions': submit_actions,
        'save_status': save_status,
        'actions_output': actions_output,
        # 模板2组件
        'submit_actions_top_t2': submit_actions_top_t2,
        'save_status_top_t2': save_status_top_t2,
        'actions_output_top_t2': actions_output_top_t2,
        't2_proc_headers': t2_proc_headers,
        't2_voice_procs': t2_voice_procs,
        't2_voice_texts': t2_voice_texts,
        't2_text_intervals': t2_text_intervals,
        't2_proc_intervals': t2_proc_intervals,
        't2_video_filenames': t2_video_filenames,
        't2_bgm_filenames': t2_bgm_filenames,
        't2_light_modes': t2_light_modes,
        't2_light_rgbs': t2_light_rgbs,
        't2_fragrance_counts': t2_fragrance_counts,
        'submit_actions_t2': submit_actions_t2,
        'save_status_t2': save_status_t2,
        'actions_output_t2': actions_output_t2
    }

def format_actions(fr_count, l_mode, l_rgb, vid_fn, bgm_fn, *proc_inputs):
    """格式化Actions JSON"""
    L.debug(f"DEBUG: format_actions called with {len(proc_inputs)} proc_inputs")
    L.debug(f"DEBUG: First 12 proc_inputs: {proc_inputs[:12] if len(proc_inputs) >= 12 else proc_inputs}")
    
    actions = {}
    actions['fragrance'] = {'status': 'on', 'count': fr_count}
    
    # 只有当灯光模式不为空时才添加灯光配置
    if l_mode:
        actions['light'] = {'mode': l_mode, 'rgb': l_rgb or ''}
    else:
        actions['light'] = None
    
    actions['display'] = {'filename': vid_fn}
    actions['bgm'] = {'action': 'play', 'filename': bgm_fn}
    
    # 处理30个流程 - 每个流程4个参数：voice_proc, text_interval, proc_interval, voice_text
    voices = []
    for i in range(30):
        base_idx = i * 4
        if base_idx + 3 < len(proc_inputs):
            proc_name = proc_inputs[base_idx]       # 流程名
            text_intv = proc_inputs[base_idx + 1]   # 文字间隔时间
            proc_intv = proc_inputs[base_idx + 2]   # 流程间隔时间
            voice_txt = proc_inputs[base_idx + 3]   # 文字内容
            
            if voice_txt:
                voice_item = {
                    'text': voice_txt,
                    'wait_time': proc_intv or 0,
                    'process_name': proc_name,
                    'text_interval': text_intv or 0
                }
                voices.append(voice_item)
    
    voice_sequence = {'voices': voices, 'repeat': None}
    actions['voice'] = voice_sequence
    actions['action_feature'] = f"多流程执行（{len(voices)}个流程）"
    actions['skip_photo_capture'] = False
    return actions

def format_actions_template2(*proc_inputs):
    """格式化模板2的Actions JSON"""
    L.debug(f"DEBUG: format_actions_template2 called with {len(proc_inputs)} proc_inputs")
    L.debug(f"DEBUG: First 18 proc_inputs: {proc_inputs[:18] if len(proc_inputs) >= 18 else proc_inputs}")
    
    actions = {}
    voices = []
    
    # 处理30个独立流程 - 每个流程9个参数
    for i in range(30):
        base_idx = i * 9  # 每个流程有9个输入参数
        if base_idx + 8 < len(proc_inputs):
            proc_name = proc_inputs[base_idx]       # 流程名
            voice_txt = proc_inputs[base_idx + 1]   # 文字内容
            text_intv = proc_inputs[base_idx + 2]   # 文字间隔时间
            proc_intv = proc_inputs[base_idx + 3]   # 流程间隔时间
            vid_fn = proc_inputs[base_idx + 4]      # 视频文件名
            bgm_fn = proc_inputs[base_idx + 5]      # 音乐文件名
            l_mode = proc_inputs[base_idx + 6]      # 灯光模式
            l_rgb = proc_inputs[base_idx + 7]       # RGB值
            fr_count = proc_inputs[base_idx + 8]    # 香氛次数
            
            L.debug(f"DEBUG: format_actions_template2 Process {i}: name={repr(proc_name)}, voice_txt={repr(voice_txt)[:30]}")
            
            if voice_txt:
                # 只有当文字内容不为空时才添加
                voice_item = {
                    'text': voice_txt,
                    'wait_time': proc_intv or 0,
                    'process_name': proc_name or f"流程{i+1}",
                    'individual_config': {
                        'display': {'filename': vid_fn} if vid_fn else None,
                        'bgm': {'action': 'play', 'filename': bgm_fn} if bgm_fn else None,
                        'light': {'mode': l_mode, 'rgb': l_rgb} if l_mode else None,
                        'fragrance': {'status': 'on', 'count': fr_count} if fr_count is not None else None
                    }
                }
                voices.append(voice_item)
    
    voice_sequence = {'voices': voices, 'repeat': None}
    actions['voice'] = voice_sequence
    actions['action_feature'] = f"独立配置执行（{len(voices)}个流程）"
    actions['skip_photo_capture'] = False
    actions['template_type'] = 'template2'
    return actions

def format_actions_and_save(filepath, fr_count, l_mode, l_rgb, vid_fn, bgm_fn, *proc_inputs):
    """格式化Actions JSON并保存到文件"""
    L.debug(f"DEBUG: format_actions_and_save called with {len(proc_inputs)} proc_inputs")
    
    # 构建JSON数据结构，按照样例格式
    json_data = {}
    
    # 处理30个流程 - 每个流程有4个参数：voice_proc, text_interval, proc_interval, voice_text
    for i in range(30):
        base_idx = i * 4
        if base_idx + 3 < len(proc_inputs):
            proc_name = proc_inputs[base_idx]
            text_intv = proc_inputs[base_idx + 1] 
            proc_intv = proc_inputs[base_idx + 2]
            voice_txt = proc_inputs[base_idx + 3]
            
            # 类型检查和转换
            if not isinstance(voice_txt, str):
                voice_txt = str(voice_txt) if voice_txt is not None else ""
            
            if not isinstance(proc_name, str):
                proc_name = str(proc_name) if proc_name is not None else ""
            
            # 确保数值类型正确
            try:
                text_intv = float(text_intv) if text_intv is not None and text_intv != "" else 0
            except (ValueError, TypeError):
                text_intv = 0
                
            try:
                proc_intv = float(proc_intv) if proc_intv is not None and proc_intv != "" else 0
            except (ValueError, TypeError):
                proc_intv = 0
            
            if proc_name and voice_txt:  # 只有当流程名和文字内容都不为空时才添加
                # 处理文字内容 - 按换行符分割成数组
                try:
                    text_lines = [line.strip() for line in voice_txt.split('\n') if line.strip()]
                except AttributeError as e:
                    L.debug(f"ERROR: Failed to split voice_txt: {e}")
                    text_lines = [str(voice_txt)]
                
                # 构建流程数据
                process_data = {
                    "voice": {
                        "voices": [
                            {
                                "action": "play",
                                "text": text_lines,
                                "text_interval": text_intv if text_intv != 0 else None,
                                "wait_time": proc_intv if proc_intv != 0 else None,
                                "repeat": None
                            }
                        ],
                        "repeat": None
                    },
                    "bgm": {
                        "filename": bgm_fn if bgm_fn else ""
                    },
                    "fragrance": {
                        "status": "on",
                        "count": fr_count
                    } if fr_count and fr_count > 0 else None,
                    "light": None,
                    "display": {
                        "filename": vid_fn if vid_fn else ""
                    } if vid_fn else None
                }
                
                # 处理灯光配置
                if l_mode:
                    # 提取模式名称（去掉中文说明）
                    mode_name = l_mode.split("（")[0] if "（" in l_mode else l_mode
                    light_config = {"mode": mode_name}
                    if l_rgb:
                        light_config["rgb"] = l_rgb
                    process_data["light"] = light_config
                
                json_data[proc_name] = process_data
    
    # 保存文件
    success, message = save_json_data(filepath, json_data)
    
    # 构建详细的反馈信息
    if success:
        feedback_message = f"""
✅ **保存成功！**

📁 **文件路径**: {filepath}
📊 **保存流程数**: {len(json_data)} 个
🎯 **模板类型**: 模板1 - 共享配置
⏰ **保存时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**保存的流程列表**:
{chr(10).join([f"• {name}" for name in list(json_data.keys())[:5]])}
{"..." if len(json_data) > 5 else ""}
        """.strip()
    else:
        feedback_message = f"❌ **保存失败**: {message}"
    
    # 同时返回Actions格式用于显示
    actions = format_actions(fr_count, l_mode, l_rgb, vid_fn, bgm_fn, *proc_inputs)
    
    # 在actions中添加保存反馈信息
    actions["save_feedback"] = {
        "success": success,
        "message": feedback_message,
        "filepath": filepath,
        "saved_processes": len(json_data),
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    return actions

def format_actions_template2_and_save(filepath, *proc_inputs):
    """格式化模板2的Actions JSON并保存到文件"""
    L.debug(f"DEBUG: format_actions_template2_and_save called with {len(proc_inputs)} proc_inputs")
    
    json_data = {}
    
    # 处理30个独立流程 - 每个流程9个参数
    for i in range(30):
        base_idx = i * 9  # 每个流程有9个输入参数
        if base_idx + 8 < len(proc_inputs):
            proc_name = proc_inputs[base_idx]
            voice_txt = proc_inputs[base_idx + 1]
            text_intv = proc_inputs[base_idx + 2]
            proc_intv = proc_inputs[base_idx + 3]
            vid_fn = proc_inputs[base_idx + 4]
            bgm_fn = proc_inputs[base_idx + 5]
            l_mode = proc_inputs[base_idx + 6]
            l_rgb = proc_inputs[base_idx + 7]
            fr_count = proc_inputs[base_idx + 8]
            
            # 类型检查和转换
            if not isinstance(voice_txt, str):
                voice_txt = str(voice_txt) if voice_txt is not None else ""
            
            if not isinstance(proc_name, str):
                proc_name = str(proc_name) if proc_name is not None else ""
            
            # 确保数值类型正确
            try:
                text_intv = float(text_intv) if text_intv is not None and text_intv != "" else 0
            except (ValueError, TypeError):
                text_intv = 0
                
            try:
                proc_intv = float(proc_intv) if proc_intv is not None and proc_intv != "" else 0
            except (ValueError, TypeError):
                proc_intv = 0
                
            try:
                fr_count = int(fr_count) if fr_count is not None and fr_count != "" else 0
            except (ValueError, TypeError):
                fr_count = 0
            
            if proc_name and voice_txt:  # 只有当流程名和文字内容都不为空时才添加
                # 处理文字内容 - 按换行符分割成数组
                try:
                    text_lines = [line.strip() for line in voice_txt.split('\n') if line.strip()]
                except AttributeError as e:
                    L.debug(f"ERROR: Failed to split voice_txt: {e}")
                    text_lines = [str(voice_txt)]
                
                # 构建流程数据
                process_data = {
                    "voice": {
                        "voices": [
                            {
                                "action": "play",
                                "text": text_lines,
                                "text_interval": text_intv if text_intv != 0 else None,
                                "wait_time": proc_intv if proc_intv != 0 else None,
                                "repeat": None
                            }
                        ],
                        "repeat": None
                    },
                    "bgm": {
                        "filename": bgm_fn if bgm_fn else ""
                    },
                    "fragrance": {
                        "status": "on", 
                        "count": fr_count
                    } if fr_count and fr_count > 0 else None,
                    "light": None,
                    "display": {
                        "filename": vid_fn if vid_fn else ""
                    } if vid_fn else None
                }
                
                # 处理灯光配置
                if l_mode:
                    # 提取模式名称（去掉中文说明）
                    mode_name = l_mode.split("（")[0] if "（" in l_mode else l_mode
                    light_config = {"mode": mode_name}
                    if l_rgb:
                        light_config["rgb"] = l_rgb
                    process_data["light"] = light_config
                
                json_data[proc_name] = process_data
    
    # 保存文件
    success, message = save_json_data(filepath, json_data)
    
    # 构建详细的反馈信息
    if success:
        feedback_message = f"""
✅ **保存成功！**

📁 **文件路径**: {filepath}
📊 **保存流程数**: {len(json_data)} 个
🎯 **模板类型**: 模板2 - 独立配置
⏰ **保存时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**保存的流程列表**:
{chr(10).join([f"• {name}" for name in list(json_data.keys())[:5]])}
{"..." if len(json_data) > 5 else ""}
        """.strip()
    else:
        feedback_message = f"❌ **保存失败**: {message}"
    
    # 同时返回Actions格式用于显示
    actions = format_actions_template2(*proc_inputs)
    
    # 在actions中添加保存反馈信息
    actions["save_feedback"] = {
        "success": success,
        "message": feedback_message,
        "filepath": filepath,
        "saved_processes": len(json_data),
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    return actions

def show_detail_view(item_path):
    """显示详情页面视图"""
    # 构建层级显示
    L.debug(f"DEBUG: show_detail_view called with item_path={item_path}")

    if isinstance(item_path, list) and len(item_path) > 1:
        breadcrumb = " > ".join(item_path)
    else:
        breadcrumb = item_path[-1] if isinstance(item_path, list) else item_path
    
    # 构建文件路径 - 使用相同的改进匹配逻辑
    if isinstance(item_path, list) and len(item_path) > 1:
        filename = ">".join(item_path).replace(" ", "") + ".json"
    else:
        item_name = item_path[-1] if isinstance(item_path, list) else item_path
        filename = item_name.replace(" ", "") + ".json"

    filepath = os.path.join(settings.DATA_DIR, filename)

    # 检查文件是否存在 - 使用相同的改进匹配逻辑
    if not os.path.exists(filepath):
        # 尝试去掉空格的组合
        alt_filename = breadcrumb.replace(" ", "") + ".json"
        alt_filepath = os.path.join(settings.DATA_DIR, alt_filename)

        if os.path.exists(alt_filepath):
            filepath = alt_filepath
            filename = alt_filename
        else:
            # 更精确的文件匹配
            if os.path.exists(settings.DATA_DIR):
                files = os.listdir(settings.DATA_DIR)
                
                # 将目标路径标准化
                target_normalized = breadcrumb.replace(" ", "")
                
                # 寻找完全匹配的文件
                exact_match = None
                for f in files:
                    if f.endswith('.json'):
                        file_base = f[:-5]  # 移除.json
                        if file_base == target_normalized:
                            exact_match = f
                            break
                
                if exact_match:
                    filepath = os.path.join(settings.DATA_DIR, exact_match)
                    filename = exact_match
                else:
                    # 检查层级结构匹配
                    target_parts = [part.strip() for part in breadcrumb.split(">")]
                    
                    best_match = None
                    best_score = 0
                    
                    for f in files:
                        if f.endswith('.json'):
                            file_base = f[:-5]  # 移除.json
                            file_parts = [part.strip() for part in file_base.split(">")]
                            
                            # 计算匹配度
                            if len(file_parts) == len(target_parts):
                                match_score = 0
                                for i, (target_part, file_part) in enumerate(zip(target_parts, file_parts)):
                                    if target_part.replace(" ", "") == file_part.replace(" ", ""):
                                        match_score += 1
                                
                                # 只有完全匹配所有层级才认为是有效匹配
                                if match_score == len(target_parts) and match_score > best_score:
                                    best_score = match_score
                                    best_match = f
                    
                    if best_match:
                        filepath = os.path.join(settings.DATA_DIR, best_match)
                        filename = best_match
    
    # 加载JSON数据
    json_data = load_json_data(filepath)
    if not json_data:
        json_data = {}
    
    # 填充模板数据
    template1_data = populate_template1(json_data)
    template2_data = populate_template2(json_data)
    
    # 构建详情HTML
    detail_html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 2px;">
        <div style="display: flex; align-items: center; margin-bottom: 2px;">
            <h1 style="color: #333; margin: 0;">{breadcrumb}</h1>
            <a href="?key={KEY}" style="text-decoration: none; color: #007bff; margin-left: 15px;">🔙 返回目录</a>
        </div>
        <p style="color: #666; margin: 5px 0;">文件路径: {filepath}</p>
        <p style="color: #666; margin: 5px 0;">文件存在: {'是' if os.path.exists(filepath) else '否'}</p>
        <p style="color: #666; margin: 5px 0;">加载的流程数: 模板1={len(template1_data['processes'])}, 模板2={len(template2_data['processes'])}</p>
    </div>
    """
    
    all_updates = []

    # 1. 基础组件更新 (5个)
    all_updates.append(detail_html)
    all_updates.append(gr.update(visible=False))  # edit_btn
    all_updates.append(gr.update(visible=False))  # save_btn
    all_updates.append(gr.update(visible=False))  # cancel_btn
    all_updates.append(gr.update(visible=True))   # detail_tabs

    # 2. 模板1共享配置更新 (5个) - 在这里存储filepath
    shared_config_updates = [
        gr.update(value=template1_data['video_filename'] if template1_data['video_filename'] else '', interactive=True),
        gr.update(value=template1_data['bgm_filename'] if template1_data['bgm_filename'] else '', interactive=True),
        gr.update(value=template1_data['light_mode'] if template1_data['light_mode'] else None),
        gr.update(value=template1_data['light_rgb'] if template1_data['light_rgb'] else ''),
        gr.update(value=template1_data['fragrance_count'] if template1_data['fragrance_count'] is not None else 0)
    ]
    
    all_updates.extend(shared_config_updates)

    # 3. 模板1流程配置更新 (30个流程 × 4个字段 = 120个)
    voice_procs_updates = [gr.update(value='') for _ in range(30)]
    text_intervals_updates = [gr.update(value=0) for _ in range(30)]
    proc_intervals_updates = [gr.update(value=0) for _ in range(30)]
    voice_texts_updates = [gr.update(value='') for _ in range(30)]

    for i, process in enumerate(template1_data['processes']):
        if i < 30:
            voice_procs_updates[i] = gr.update(value=process['name'])
            text_intervals_updates[i] = gr.update(value=process['text_interval'])
            proc_intervals_updates[i] = gr.update(value=process['wait_time'])
            voice_texts_updates[i] = gr.update(value=process['text'])

    all_updates.extend(voice_procs_updates)
    all_updates.extend(text_intervals_updates)
    all_updates.extend(proc_intervals_updates)
    all_updates.extend(voice_texts_updates)

    # 4. 模板2流程配置更新 (30个流程 × 9个字段 = 270个)
    t2_voice_procs_updates = [gr.update(value='') for _ in range(30)]
    t2_voice_texts_updates = [gr.update(value='') for _ in range(30)]
    t2_text_intervals_updates = [gr.update(value=0) for _ in range(30)]
    t2_proc_intervals_updates = [gr.update(value=0) for _ in range(30)]
    t2_video_filenames_updates = [gr.update(value='') for _ in range(30)]
    t2_bgm_filenames_updates = [gr.update(value='') for _ in range(30)]
    t2_light_modes_updates = [gr.update(value=None) for _ in range(30)]
    t2_light_rgbs_updates = [gr.update(value='') for _ in range(30)]
    t2_fragrance_counts_updates = [gr.update(value=0) for _ in range(30)]

    for i, process in enumerate(template2_data['processes']):
        if i < 30:
            t2_voice_procs_updates[i] = gr.update(value=process['name'])
            t2_voice_texts_updates[i] = gr.update(value=process['text'])
            t2_text_intervals_updates[i] = gr.update(value=process['text_interval'])
            t2_proc_intervals_updates[i] = gr.update(value=process['wait_time'])
            t2_video_filenames_updates[i] = gr.update(value=process['video_filename'])
            t2_bgm_filenames_updates[i] = gr.update(value=process['bgm_filename'])
            if process['light_mode']:
                t2_light_modes_updates[i] = gr.update(value=process['light_mode'])
            t2_light_rgbs_updates[i] = gr.update(value=process['light_rgb'])
            t2_fragrance_counts_updates[i] = gr.update(value=process['fragrance_count'])

    all_updates.extend(t2_voice_procs_updates)
    all_updates.extend(t2_voice_texts_updates)
    all_updates.extend(t2_text_intervals_updates)
    all_updates.extend(t2_proc_intervals_updates)
    all_updates.extend(t2_video_filenames_updates)
    all_updates.extend(t2_bgm_filenames_updates)
    all_updates.extend(t2_light_modes_updates)
    all_updates.extend(t2_light_rgbs_updates)
    all_updates.extend(t2_fragrance_counts_updates)

    # 确保返回正确数量的更新值 (总共400个)
    expected_count = 400
    actual_count = len(all_updates)
    
    if actual_count != expected_count:
        L.debug(f"Warning: Expected {expected_count} updates, got {actual_count}")
        # 如果数量不匹配，补充或截断
        if actual_count < expected_count:
            all_updates.extend([gr.update() for _ in range(expected_count - actual_count)])
        else:
            all_updates = all_updates[:expected_count]

    return tuple(all_updates)

def get_current_filepath():
    """获取当前文件路径 - 这个函数需要在实际使用时传入正确的路径"""
    return ""

def check_file_completion(item_name):
    """检查文件完成度"""
    # 构建文件路径 - 改进匹配逻辑
    filename = item_name.replace(" ", "") + ".json"
    filepath = os.path.join(settings.DATA_DIR, filename)

    # 如果文件不存在，尝试其他可能的路径
    if not os.path.exists(filepath):
        # 尝试去掉空格和">"的组合
        alt_filename = item_name.replace(">", "").replace(" ", "") + ".json"
        alt_filepath = os.path.join(settings.DATA_DIR, alt_filename)
        if os.path.exists(alt_filepath):
            filepath = alt_filepath
        else:
            # 更精确的文件匹配 - 只匹配完全符合的路径结构
            if os.path.exists(settings.DATA_DIR):
                files = os.listdir(settings.DATA_DIR)
                
                # 将目标路径标准化（去掉空格）
                target_normalized = item_name.replace(" ", "")
                
                # 寻找完全匹配的文件
                exact_match = None
                for f in files:
                    if f.endswith('.json'):
                        # 去掉.json后缀进行比较
                        file_base = f[:-5]  # 移除.json
                        if file_base == target_normalized:
                            exact_match = f
                            break
                
                if exact_match:
                    filepath = os.path.join(settings.DATA_DIR, exact_match)
                else:
                    # 如果没有完全匹配，检查是否有部分匹配但结构相似的文件
                    # 将路径分解为层级结构进行匹配
                    target_parts = [part.strip() for part in item_name.split(">")]
                    
                    best_match = None
                    best_score = 0
                    
                    for f in files:
                        if f.endswith('.json'):
                            file_base = f[:-5]  # 移除.json
                            file_parts = [part.strip() for part in file_base.split(">")]
                            
                            # 计算匹配度：层级数量和内容匹配
                            if len(file_parts) == len(target_parts):
                                match_score = 0
                                for i, (target_part, file_part) in enumerate(zip(target_parts, file_parts)):
                                    if target_part.replace(" ", "") == file_part.replace(" ", ""):
                                        match_score += 1
                                
                                # 只有完全匹配所有层级才认为是有效匹配
                                if match_score == len(target_parts) and match_score > best_score:
                                    best_score = match_score
                                    best_match = f
                    
                    if best_match:
                        filepath = os.path.join(settings.DATA_DIR, best_match)
    
    completion_score = 0
    max_score = 100  # 总分100分
    details = {}
    
    # 1. 检查文件是否存在 (10分)
    if not os.path.exists(filepath):
        details['file_exists'] = False
        return {
            'score': 0,
            'percentage': 0,
            'details': details,
            'filepath': filepath
        }
    else:
        details['file_exists'] = True
        completion_score += 10
    
    # 2. 检查文件是否有有效的JSON内容 (5分)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        details['valid_json'] = True
        completion_score += 5
    except Exception as e:
        details['valid_json'] = False
        details['json_error'] = str(e)
        return {
            'score': completion_score,
            'percentage': completion_score,
            'details': details,
            'filepath': filepath
        }
    
    # 3. 检查是否至少有一个有效的流程（key-value对）(5分)
    if isinstance(json_data, dict) and len(json_data) > 0:
        details['has_processes'] = True
        completion_score += 5
    else:
        details['has_processes'] = False
    
    # 4-8. 检查各个配置项
    has_valid_voices = False
    has_valid_bgm = False
    has_valid_fragrance = False
    has_valid_light = False
    has_valid_display = False
    
    for process_name, process_data in json_data.items():
        if not isinstance(process_data, dict):
            continue
            
        # 检查voices (最重要 - 70分)
        voice_config = process_data.get('voice', {})
        if voice_config and voice_config.get('voices'):
            voices_list = voice_config['voices']
            for voice in voices_list:
                if voice.get('text') and (
                    (isinstance(voice['text'], list) and any(voice['text'])) or
                    (isinstance(voice['text'], str) and voice['text'].strip())
                ):
                    has_valid_voices = True
                    break
        
        # 检查bgm (5分)
        bgm_config = process_data.get('bgm', {})
        if bgm_config and bgm_config.get('filename') and bgm_config['filename'].strip():
            has_valid_bgm = True
        
        # 检查fragrance (5分)
        fragrance_config = process_data.get('fragrance')
        if fragrance_config and fragrance_config.get('count') is not None:
            has_valid_fragrance = True
        
        # 检查light (5分)
        light_config = process_data.get('light')
        if light_config and light_config.get('rgb') and light_config['rgb'].strip():
            has_valid_light = True
        
        # 检查display (5分)
        display_config = process_data.get('display')
        if display_config and display_config.get('filename') and display_config['filename'].strip():
            has_valid_display = True
    
    # 记录检查结果
    details['has_valid_voices'] = has_valid_voices
    details['has_valid_bgm'] = has_valid_bgm
    details['has_valid_fragrance'] = has_valid_fragrance
    details['has_valid_light'] = has_valid_light
    details['has_valid_display'] = has_valid_display
    
    # 计算分数 - 新的权重分配
    if has_valid_voices:
        completion_score += 70  # 语音内容是最重要的
    if has_valid_bgm:
        completion_score += 5   # 音乐文件
    if has_valid_fragrance:
        completion_score += 5   # 香氛设置
    if has_valid_light:
        completion_score += 5   # 灯光设置
    if has_valid_display:
        completion_score += 5   # 视频文件
    
    # 确保分数不超过100
    percentage = min(completion_score, 100)
    
    return {
        'score': completion_score,
        'percentage': percentage,
        'details': details,
        'filepath': filepath
    }
