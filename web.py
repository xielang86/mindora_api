import gradio as gr
import json
import os
from web_detail import create_detail_components, format_actions, format_actions_template2, show_detail_view, KEY, verify_key, format_actions_and_save, format_actions_template2_and_save, check_file_completion
from aivc.config.config import settings,L
from aivc.sop.common.data import load_directory_data


def render_tree(data, level=0, parent_path=[]):
    """递归渲染目录树"""
    html = ""
    indent = "  " * level
    
    for item in data:
        name = item.get("name", "未命名")
        children = item.get("children", [])
        current_path = parent_path + [name]
        
        if children:
            # 有子项的节点 - 默认展开
            html += f'{indent}<details open>\n'
            html += f'{indent}  <summary style="cursor: pointer; padding: 5px; margin: 2px 0; background-color: #f0f0f0; border-radius: 3px; font-weight: bold;">{name}</summary>\n'
            html += f'{indent}  <div style="margin-left: 20px; padding: 5px; border-left: 2px solid #ddd;">\n'
            html += render_tree(children, level + 2, current_path)
            html += f'{indent}  </div>\n'
            html += f'{indent}</details>\n'
        else:
            # 叶子节点 - 检查完成度并显示进度条
            # 构建完整路径用于检查文件
            full_path_name = " > ".join(current_path)
            completion = check_file_completion(full_path_name)
            percentage = completion['percentage']
            
            # 根据完成度设置颜色
            if percentage >= 80:
                progress_color = "#28a745"  # 绿色
                status_emoji = "✅"
            elif percentage >= 50:
                progress_color = "#ffc107"  # 黄色
                status_emoji = "⚠️"
            else:
                progress_color = "#dc3545"  # 红色
                status_emoji = "❌"
            
            escaped_name = name.replace("'", "\\'").replace('"', '\\"')
            html += f'{indent}<div style="padding: 8px 10px; margin: 3px 0; background-color: #f9f9f9; border-radius: 4px; border-left: 3px solid #007bff; position: relative;">\n'
            
            # 项目名称和链接
            html += f'{indent}  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">\n'
            html += f'{indent}    <a href="?key={KEY}&name={escaped_name}" style="text-decoration: none; color: #007bff; font-weight: 500; flex: 1;">{name}</a>\n'
            html += f'{indent}    <span style="font-size: 16px; margin-left: 8px;">{status_emoji}</span>\n'
            html += f'{indent}  </div>\n'
            
            # 进度条
            html += f'{indent}  <div style="width: 100%; background-color: #e9ecef; border-radius: 10px; height: 12px; overflow: hidden; margin-bottom: 4px;">\n'
            html += f'{indent}    <div style="width: {percentage}%; height: 100%; background-color: {progress_color}; border-radius: 10px; transition: width 0.3s ease;"></div>\n'
            html += f'{indent}  </div>\n'
            
            # 完成度文字和详细信息
            html += f'{indent}  <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: #666;">\n'
            html += f'{indent}    <span>完成度: {percentage}%</span>\n'
            
            # 显示缺失的项目 - 根据新的权重调整显示逻辑
            missing_items = []
            details = completion['details']
            if not details.get('file_exists', False):
                missing_items.append("文件")
            elif not details.get('valid_json', False):
                missing_items.append("JSON")
            else:
                if not details.get('has_processes', False):
                    missing_items.append("流程")
                # 语音内容最重要，优先显示
                if not details.get('has_valid_voices', False):
                    missing_items.append("⚠️语音")
                # 其他配置权重较低
                if not details.get('has_valid_bgm', False):
                    missing_items.append("音乐")
                if not details.get('has_valid_fragrance', False):
                    missing_items.append("香氛")
                if not details.get('has_valid_light', False):
                    missing_items.append("灯光")
                if not details.get('has_valid_display', False):
                    missing_items.append("视频")
            
            if missing_items:
                missing_text = "缺失: " + "、".join(missing_items[:3])
                if len(missing_items) > 3:
                    missing_text += "..."
                html += f'{indent}    <span style="color: #dc3545; font-size: 10px;">{missing_text}</span>\n'
            else:
                html += f'{indent}    <span style="color: #28a745; font-size: 10px;">✓ 完整</span>\n'
            
            html += f'{indent}  </div>\n'
            html += f'{indent}</div>\n'
    
    return html

def display_directory(request: gr.Request):
    """显示目录结构"""
    url_params = dict(request.query_params)
    provided_key = url_params.get('key', '')
    
    if not verify_key(provided_key):
        return "❌ 错误：无效的API Key，请在URL中添加正确的key参数 (例如: ?key=your_key)"
    
    # 如果带 name 参数，则渲染空白详情页
    if 'name' in url_params:
        item_name = url_params.get('name', '')
        return f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 2px;">
            <div style="display: flex; align-items: center; margin-bottom: 2px;">
            <h1 style="color: #333; margin: 0;">{item_name}</h1>
            <a href="?key={KEY}" style="text-decoration: none; color: #007bff; margin-left: 15px;">🔙 返回目录</a>
            </div>
        </div>
        """
    
    # 加载并渲染目录
    directory_data = load_directory_data()
    tree_html = render_tree(directory_data)
    
    return f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h3 style="color: #333; margin-bottom: 20px;">📁 目录结构</h3>
        {tree_html}
    </div>
    """

def load_json_for_edit(request: gr.Request):
    """加载JSON用于编辑"""
    # 从URL参数中获取key
    url_params = dict(request.query_params)
    provided_key = url_params.get('key', '')
    
    if not verify_key(provided_key):
        return "❌ 错误：无效的API Key"
    
    try:
        with open(settings.DIR_JSON_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"加载失败: {str(e)}"

def save_json_edit(json_text, request: gr.Request):
    """保存编辑的JSON"""
    # 从URL参数中获取key
    url_params = dict(request.query_params)
    provided_key = url_params.get('key', '')
    
    if not verify_key(provided_key):
        return "❌ 错误：无效的API Key", gr.update()
    
    try:
        # 验证JSON格式
        data = json.loads(json_text)
        
        # 保存文件
        with open(settings.DIR_JSON_PATH, 'w', encoding='utf-8') as f:
            f.write(json_text)
        
        # 重新显示目录
        tree_html = render_tree(data)
        updated_display = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h3 style="color: #333; margin-bottom: 20px;">📁 目录结构</h3>
            {tree_html}
        </div>
        """
        
        return "✅ 保存成功", updated_display
    except json.JSONDecodeError as e:
        return f"❌ JSON格式错误: {str(e)}", gr.update()
    except Exception as e:
        return f"❌ 保存失败: {str(e)}", gr.update()

def show_item_detail(item_name, request: gr.Request):
    """显示项目详情页面"""
    # 从URL参数中获取key
    url_params = dict(request.query_params)
    provided_key = url_params.get('key', '')
    
    if not verify_key(provided_key):
        return "❌ 错误：无效的API Key"
    
    return f"""
     """

def find_item_path(data, target_name, current_path=[]):
    """递归查找项目的完整路径"""
    for item in data:
        name = item.get("name", "未命名")
        children = item.get("children", [])
        new_path = current_path + [name]
        
        if name == target_name:
            return new_path
        
        if children:
            result = find_item_path(children, target_name, new_path)
            if result:
                return result
    
    return None

def initial_view(request: gr.Request):
    html = display_directory(request)
    params = dict(request.query_params)
    if 'name' in params:
        # 详情页：显示详情页面
        item_name = params.get('name', '')
        directory_data = load_directory_data()
        item_path = find_item_path(directory_data, item_name)
        
        if not item_path:
            item_path = [item_name]
        
        detail_result = show_detail_view(item_path)
        
        # 现在应该是400个值（修正后的总数）
        if len(detail_result) >= 400:
            return detail_result
        else:
            return tuple([gr.update() for _ in range(400)])
    
    # 首页：显示目录和编辑按钮，同时返回所有组件的默认更新
    outputs = [
        html,
        gr.update(visible=True),   # edit_btn
        gr.update(visible=False),  # save_btn
        gr.update(visible=False),  # cancel_btn
        gr.update(visible=False),  # detail_tabs
    ]
    
    # 添加模板1共享配置的默认值 - 移除debug_info
    outputs.extend([
        gr.update(value=''),       # video_filename
        gr.update(value=''),       # bgm_filename
        gr.update(value=None),     # light_mode
        gr.update(value=''),       # light_rgb
        gr.update(value=0),        # fragrance_count
    ])
    
    # 添加模板1流程组件的默认值（30个流程 × 4个字段）
    for i in range(30):
        outputs.extend([
            gr.update(value=''),   # voice_proc
            gr.update(value=0),    # text_interval
            gr.update(value=0),    # proc_interval
            gr.update(value='')    # voice_text
        ])
    
    # 添加模板2组件的默认值（30个流程 × 9个字段）
    for i in range(30):
        outputs.extend([
            gr.update(value=''),                    # voice_proc
            gr.update(value=''),                    # voice_text
            gr.update(value=0),                     # text_interval
            gr.update(value=0),                     # proc_interval
            gr.update(value=''),                    # video_filename
            gr.update(value=''),                    # bgm_filename
            gr.update(value=''),                    # light_mode
            gr.update(value=''),                    # light_rgb
            gr.update(value=0)                      # fragrance_count
        ])
    
    return tuple(outputs)

def get_filepath_from_url(request: gr.Request):
    """从URL参数中获取文件路径"""
    params = dict(request.query_params)
    item_name = params.get('name', '')
    if item_name:
        directory_data = load_directory_data()
        item_path = find_item_path(directory_data, item_name)
        
        if isinstance(item_path, list) and len(item_path) > 1:
            # 使用">"连接路径，而不是" > "
            filename = ">".join(item_path).replace(" ", "") + ".json"
        else:
            filename = item_name.replace(" ", "") + ".json"

        filepath = os.path.join(settings.DATA_DIR, filename)

        # 如果文件不存在，使用改进的匹配逻辑
        if not os.path.exists(filepath):
            if os.path.exists(settings.DATA_DIR):
                files = os.listdir(settings.DATA_DIR)
                
                # 构建目标路径
                if isinstance(item_path, list) and len(item_path) > 1:
                    target_normalized = ">".join(item_path).replace(" ", "")
                else:
                    target_normalized = item_name.replace(" ", "")
                
                # 寻找完全匹配的文件
                for f in files:
                    if f.endswith('.json'):
                        file_base = f[:-5]  # 移除.json
                        if file_base == target_normalized:
                            return os.path.join(settings.DATA_DIR, f)
                
                # 如果没有完全匹配，检查层级结构匹配
                if isinstance(item_path, list) and len(item_path) > 1:
                    target_parts = item_path
                else:
                    target_parts = [item_name]
                
                for f in files:
                    if f.endswith('.json'):
                        file_base = f[:-5]  # 移除.json
                        file_parts = [part.strip() for part in file_base.split(">")]
                        
                        # 只有层级数量和内容都完全匹配才认为是有效匹配
                        if len(file_parts) == len(target_parts):
                            match_count = 0
                            for target_part, file_part in zip(target_parts, file_parts):
                                if target_part.replace(" ", "") == file_part.replace(" ", ""):
                                    match_count += 1
                            
                            if match_count == len(target_parts):
                                return os.path.join(settings.DATA_DIR, f)
        
        return filepath
    return ""

# 创建Gradio界面
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=3):
            directory_display = gr.HTML(label="目录结构")
    
        with gr.Column(scale=1):
            edit_btn = gr.Button("📝 编辑目录", variant="primary")
            with gr.Row():
                save_btn = gr.Button("💾 保存", variant="secondary", visible=False)
                cancel_btn = gr.Button("❌ 取消", variant="secondary", visible=False)
    
    json_editor = gr.Code(
        label="JSON编辑器", 
        language="json", 
        visible=False,
        lines=20
    )
    
    # 创建详情页面组件
    detail_components = create_detail_components()
    
    # 页面加载时初始化视图
    demo.load(
        initial_view,
        outputs=[
            directory_display, edit_btn, save_btn, cancel_btn,
            detail_components['detail_tabs'],
            # 模板1共享配置 - 移除debug_info
            detail_components['video_filename'],
            detail_components['bgm_filename'],
            detail_components['light_mode'],
            detail_components['light_rgb'],
            detail_components['fragrance_count'],
            # 模板1流程配置
            *detail_components['voice_procs'],
            *detail_components['text_intervals'],
            *detail_components['proc_intervals'],
            *detail_components['voice_texts'],
            # 模板2配置
            *detail_components['t2_voice_procs'],
            *detail_components['t2_voice_texts'],
            *detail_components['t2_text_intervals'],
            *detail_components['t2_proc_intervals'],
            *detail_components['t2_video_filenames'],
            *detail_components['t2_bgm_filenames'],
            *detail_components['t2_light_modes'],
            *detail_components['t2_light_rgbs'],
            *detail_components['t2_fragrance_counts']
        ]
    )
    
    # 编辑按钮点击 - 显示编辑器
    def show_editor(request: gr.Request):
        json_content = load_json_for_edit(request)
        return (
            gr.update(visible=False),  # 隐藏目录显示
            gr.update(visible=True, value=json_content),  # 显示编辑器
            gr.update(visible=False),  # 隐藏编辑按钮
            gr.update(visible=True),   # 显示保存按钮
            gr.update(visible=True),   # 显示取消按钮
        )
    
    edit_btn.click(
        show_editor,
        outputs=[directory_display, json_editor, edit_btn, save_btn, cancel_btn]
    )
    
    # 保存按钮点击
    def save_and_show_directory(json_text, request: gr.Request):
        status, updated_display = save_json_edit(json_text, request)
        return (
            gr.update(visible=True, value=updated_display),  # 显示更新的目录
            gr.update(visible=False),  # 隐藏编辑器
            gr.update(visible=True),   # 显示编辑按钮
            gr.update(visible=False),  # 隐藏保存按钮
            gr.update(visible=False),  # 隐藏取消按钮
        )
    
    save_btn.click(
        save_and_show_directory,
        inputs=[json_editor],
        outputs=[directory_display, json_editor, edit_btn, save_btn, cancel_btn]
    )
    
    # 取消按钮点击
    def cancel_edit(request: gr.Request):
        updated_display = display_directory(request)
        return (
            gr.update(visible=True, value=updated_display),  # 显示目录
            gr.update(visible=False),  # 隐藏编辑器
            gr.update(visible=True),   # 显示编辑按钮
            gr.update(visible=False),  # 隐藏保存按钮
            gr.update(visible=False),  # 隐藏取消按钮
        )
    
    cancel_btn.click(
        cancel_edit,
        outputs=[directory_display, json_editor, edit_btn, save_btn, cancel_btn]
    )
    
    # 模板1提交按钮事件 - 修正参数顺序，添加保存反馈
    def handle_template1_submit(request: gr.Request, fr_count, l_mode, l_rgb, vid_fn, bgm_fn, *proc_inputs):
        L.debug(f"DEBUG: handle_template1_submit called with {len(proc_inputs)} proc_inputs")
        
        filepath = get_filepath_from_url(request)
        if filepath:
            result = format_actions_and_save(filepath, fr_count, l_mode, l_rgb, vid_fn, bgm_fn, *proc_inputs)
            
            # 提取保存反馈信息
            save_feedback = result.get("save_feedback", {})
            feedback_message = save_feedback.get("message", "操作完成")
            
            return result, feedback_message
        else:
            result = format_actions(fr_count, l_mode, l_rgb, vid_fn, bgm_fn, *proc_inputs)
            return result, "⚠️ **预览模式** - 未找到文件路径，未执行保存操作"
    
    # 重新组织模板1的输入参数顺序 - 确保是：voice_proc, text_interval, proc_interval, voice_text 的循环
    template1_inputs = []
    for i in range(30):
        template1_inputs.extend([
            detail_components['voice_procs'][i],      # 流程名
            detail_components['text_intervals'][i],   # 文字间隔时间
            detail_components['proc_intervals'][i],   # 流程间隔时间  
            detail_components['voice_texts'][i]       # 文字内容
        ])
    
    detail_components['submit_actions'].click(
        handle_template1_submit,
        inputs=[
            detail_components['fragrance_count'], 
            detail_components['light_mode'], detail_components['light_rgb'],
            detail_components['video_filename'], detail_components['bgm_filename'],
            *template1_inputs
        ],
        outputs=[detail_components['actions_output'], detail_components['save_status']]
    )
    
    detail_components['submit_actions_top'].click(
        handle_template1_submit,
        inputs=[
            detail_components['fragrance_count'], 
            detail_components['light_mode'], detail_components['light_rgb'],
            detail_components['video_filename'], detail_components['bgm_filename'],
            *template1_inputs
        ],
        outputs=[detail_components['actions_output_top'], detail_components['save_status_top']]
    )
    
    # 模板2提交按钮事件 - 修正参数顺序，添加保存反馈
    def handle_template2_submit(request: gr.Request, *proc_inputs):
        L.debug(f"DEBUG: handle_template2_submit called with {len(proc_inputs)} proc_inputs")
        
        filepath = get_filepath_from_url(request)
        if filepath:
            result = format_actions_template2_and_save(filepath, *proc_inputs)
            
            # 提取保存反馈信息
            save_feedback = result.get("save_feedback", {})
            feedback_message = save_feedback.get("message", "操作完成")
            
            return result, feedback_message
        else:
            result = format_actions_template2(*proc_inputs)
            return result, "⚠️ **预览模式** - 未找到文件路径，未执行保存操作"
    
    # 确保模板2的输入参数顺序正确
    t2_inputs = []
    for i in range(30):
        t2_inputs.extend([
            detail_components['t2_voice_procs'][i],
            detail_components['t2_voice_texts'][i],
            detail_components['t2_text_intervals'][i],
            detail_components['t2_proc_intervals'][i],
            detail_components['t2_video_filenames'][i],
            detail_components['t2_bgm_filenames'][i],
            detail_components['t2_light_modes'][i],
            detail_components['t2_light_rgbs'][i],
            detail_components['t2_fragrance_counts'][i]
        ])
    
    detail_components['submit_actions_t2'].click(
        handle_template2_submit,
        inputs=t2_inputs,
        outputs=[detail_components['actions_output_t2'], detail_components['save_status_t2']]
    )
    
    detail_components['submit_actions_top_t2'].click(
        handle_template2_submit,
        inputs=t2_inputs,
        outputs=[detail_components['actions_output_top_t2'], detail_components['save_status_top_t2']]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=9002, 
        share=False,
        show_api=False
    )