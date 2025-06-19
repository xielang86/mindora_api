import ctypes
import os
import subprocess
import resource
import threading
import time
import sys
import traceback
import psutil
import gc
from typing import List, Dict, Any
from aivc.config.config import L, settings

# 模块级别的 ctypes 定义，完全按照 flask_server.py
RKLLM_Handle_t = ctypes.c_void_p
userdata = ctypes.c_void_p(None)

LLMCallState = ctypes.c_int
LLMCallState.RKLLM_RUN_NORMAL = 0
LLMCallState.RKLLM_RUN_WAITING = 1
LLMCallState.RKLLM_RUN_FINISH = 2
LLMCallState.RKLLM_RUN_ERROR = 3

RKLLMInputMode = ctypes.c_int
RKLLMInputMode.RKLLM_INPUT_PROMPT = 0
RKLLMInputMode.RKLLM_INPUT_TOKEN = 1
RKLLMInputMode.RKLLM_INPUT_EMBED = 2
RKLLMInputMode.RKLLM_INPUT_MULTIMODAL = 3

RKLLMInferMode = ctypes.c_int
RKLLMInferMode.RKLLM_INFER_GENERATE = 0
RKLLMInferMode.RKLLM_INFER_GET_LAST_HIDDEN_LAYER = 1
RKLLMInferMode.RKLLM_INFER_GET_LOGITS = 2

class RKLLMExtendParam(ctypes.Structure):
    _fields_ = [
        ("base_domain_id", ctypes.c_int32),
        ("embed_flash", ctypes.c_int8),
        ("enabled_cpus_num", ctypes.c_int8),
        ("enabled_cpus_mask", ctypes.c_uint32),
        ("reserved", ctypes.c_uint8 * 106)
    ]

class RKLLMParam(ctypes.Structure):
    _fields_ = [
        ("model_path", ctypes.c_char_p),
        ("max_context_len", ctypes.c_int32),
        ("max_new_tokens", ctypes.c_int32),
        ("top_k", ctypes.c_int32),
        ("n_keep", ctypes.c_int32),
        ("top_p", ctypes.c_float),
        ("temperature", ctypes.c_float),
        ("repeat_penalty", ctypes.c_float),
        ("frequency_penalty", ctypes.c_float),
        ("presence_penalty", ctypes.c_float),
        ("mirostat", ctypes.c_int32),
        ("mirostat_tau", ctypes.c_float),
        ("mirostat_eta", ctypes.c_float),
        ("skip_special_token", ctypes.c_bool),
        ("is_async", ctypes.c_bool),
        ("img_start", ctypes.c_char_p),
        ("img_end", ctypes.c_char_p),
        ("img_content", ctypes.c_char_p),
        ("extend_param", RKLLMExtendParam),
    ]

class RKLLMLoraAdapter(ctypes.Structure):
    _fields_ = [
        ("lora_adapter_path", ctypes.c_char_p),
        ("lora_adapter_name", ctypes.c_char_p),
        ("scale", ctypes.c_float)
    ]

class RKLLMEmbedInput(ctypes.Structure):
    _fields_ = [
        ("embed", ctypes.POINTER(ctypes.c_float)),
        ("n_tokens", ctypes.c_size_t)
    ]

class RKLLMTokenInput(ctypes.Structure):
    _fields_ = [
        ("input_ids", ctypes.POINTER(ctypes.c_int32)),
        ("n_tokens", ctypes.c_size_t)
    ]

class RKLLMMultiModelInput(ctypes.Structure):
    _fields_ = [
        ("prompt", ctypes.c_char_p),
        ("image_embed", ctypes.POINTER(ctypes.c_float)),
        ("n_image_tokens", ctypes.c_size_t),
        ("n_image", ctypes.c_size_t),
        ("image_width", ctypes.c_size_t),
        ("image_height", ctypes.c_size_t)
    ]

class RKLLMInputUnion(ctypes.Union):
    _fields_ = [
        ("prompt_input", ctypes.c_char_p),
        ("embed_input", RKLLMEmbedInput),
        ("token_input", RKLLMTokenInput),
        ("multimodal_input", RKLLMMultiModelInput)
    ]

class RKLLMInput(ctypes.Structure):
    _fields_ = [
        ("input_mode", ctypes.c_int),
        ("input_data", RKLLMInputUnion)
    ]

class RKLLMLoraParam(ctypes.Structure):
    _fields_ = [
        ("lora_adapter_name", ctypes.c_char_p)
    ]

class RKLLMPromptCacheParam(ctypes.Structure):
    _fields_ = [
        ("save_prompt_cache", ctypes.c_int),
        ("prompt_cache_path", ctypes.c_char_p)
    ]

class RKLLMInferParam(ctypes.Structure):
    _fields_ = [
        ("mode", RKLLMInferMode),
        ("lora_params", ctypes.POINTER(RKLLMLoraParam)),
        ("prompt_cache_params", ctypes.POINTER(RKLLMPromptCacheParam)),
        ("keep_history", ctypes.c_int)
    ]

class RKLLMResultLastHiddenLayer(ctypes.Structure):
    _fields_ = [
        ("hidden_states", ctypes.POINTER(ctypes.c_float)),
        ("embd_size", ctypes.c_int),
        ("num_tokens", ctypes.c_int)
    ]

class RKLLMResultLogits(ctypes.Structure):
    _fields_ = [
        ("logits", ctypes.POINTER(ctypes.c_float)),
        ("vocab_size", ctypes.c_int),
        ("num_tokens", ctypes.c_int)
    ]

class RKLLMResult(ctypes.Structure):
    _fields_ = [
        ("text", ctypes.c_char_p),
        ("token_id", ctypes.c_int),
        ("last_hidden_layer", RKLLMResultLastHiddenLayer),
        ("logits", RKLLMResultLogits)
    ]

# 模块级全局变量
_rkllm_lib = None
_model_handle = None
_global_text = []
_global_state = -1
_split_byte_data = bytes(b"")
_inference_lock = threading.Lock()
_is_loaded = False
_callback = None

# 定义回调函数，完全按照 flask_server.py
def callback_impl(result, userdata, state):
    global _global_text, _global_state
    if state == LLMCallState.RKLLM_RUN_FINISH:
        _global_state = state
    elif state == LLMCallState.RKLLM_RUN_ERROR:
        _global_state = state
        L.error("RKNN run error")
    elif state == LLMCallState.RKLLM_RUN_NORMAL:
        _global_state = state
        _global_text.append(result.contents.text.decode('utf-8'))

# 创建回调函数指针，完全按照 flask_server.py
callback_type = ctypes.CFUNCTYPE(None, ctypes.POINTER(RKLLMResult), ctypes.c_void_p, ctypes.c_int)
_callback = callback_type(callback_impl)

def get_memory_info():
    """获取当前进程的内存使用信息"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        'rss': memory_info.rss / 1024 / 1024,  # MB
        'vms': memory_info.vms / 1024 / 1024,  # MB
        'percent': process.memory_percent(),
        'available': psutil.virtual_memory().available / 1024 / 1024  # MB
    }

def log_memory_usage(stage: str):
    """记录内存使用情况"""
    try:
        mem_info = get_memory_info()
        L.info(f"[{stage}] Memory usage - RSS: {mem_info['rss']:.1f}MB, "
               f"VMS: {mem_info['vms']:.1f}MB, "
               f"Percent: {mem_info['percent']:.1f}%, "
               f"Available: {mem_info['available']:.1f}MB")
    except Exception as e:
        L.warning(f"Failed to get memory info at {stage}: {str(e)}")

class RKNNModelLoader:
    """简化的单例，完全按照 flask_server.py 的结构"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RKNNModelLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 不再需要 _setup_ctypes，所有定义都在模块级别
        pass
        
    @classmethod
    def get_instance(cls):
        return cls()

    def load_library(self):
        """加载 RKNN 动态库"""
        global _rkllm_lib
        if _rkllm_lib is not None:
            return True
        try:
            log_memory_usage("Before loading RKNN library")
            _rkllm_lib = ctypes.CDLL(settings.RKNN_LLM_LIB)
            log_memory_usage("After loading RKNN library")
            return True
        except Exception as e:
            L.error(f"Failed to load RKNN library: {str(e)}")
            return False

    def init_model(self, model_path: str, target_platform: str = "rk3576"):
        """初始化 RKNN 模型，完全按照 flask_server.py"""
        global _is_loaded, _model_handle, _rkllm_lib
        
        if _is_loaded:
            L.info("RKNN model already loaded")
            log_memory_usage("Model already loaded")
            return True
        
        # 记录初始内存状态
        L.info(f"Starting RKNN model initialization for: {model_path}")
        log_memory_usage("Before model initialization")
        
        # 强制垃圾回收，确保内存测量准确
        gc.collect()
        log_memory_usage("After garbage collection")
                
        try:
            # 加载库
            if not self.load_library():
                return False
            
            # 设置频率
            command = f"sudo bash fix_freq_{target_platform}.sh"
            try:
                subprocess.run(command, shell=True, check=False)
            except:
                L.warning(f"Failed to run frequency fix command: {command}")
            
            # 设置资源限制
            try:
                resource.setrlimit(resource.RLIMIT_NOFILE, (102400, 102400))
            except:
                L.warning("Failed to set resource limit")
            
            log_memory_usage("Before creating model parameters")
            
            # 初始化模型参数，完全按照 flask_server.py
            rkllm_param = RKLLMParam()
            rkllm_param.model_path = bytes(model_path, 'utf-8')
            rkllm_param.max_context_len = 4096
            rkllm_param.max_new_tokens = -1
            rkllm_param.skip_special_token = True
            rkllm_param.n_keep = -1
            rkllm_param.top_k = 1
            rkllm_param.top_p = 0.9
            rkllm_param.temperature = 0.8
            rkllm_param.repeat_penalty = 1.1
            rkllm_param.frequency_penalty = 0.0
            rkllm_param.presence_penalty = 0.0
            rkllm_param.mirostat = 0
            rkllm_param.mirostat_tau = 5.0
            rkllm_param.mirostat_eta = 0.1
            rkllm_param.is_async = False
            rkllm_param.img_start = "".encode('utf-8')
            rkllm_param.img_end = "".encode('utf-8')
            rkllm_param.img_content = "".encode('utf-8')
            
            # 扩展参数
            rkllm_param.extend_param.base_domain_id = 0
            rkllm_param.extend_param.enabled_cpus_num = 4
            rkllm_param.extend_param.enabled_cpus_mask = (1 << 4)|(1 << 5)|(1 << 6)|(1 << 7)
            
            # 初始化句柄
            _model_handle = RKLLM_Handle_t()
            
            log_memory_usage("Before setting up library functions")
            
            # 设置库函数，完全按照 flask_server.py
            self.rkllm_init = _rkllm_lib.rkllm_init
            self.rkllm_init.argtypes = [ctypes.POINTER(RKLLM_Handle_t), ctypes.POINTER(RKLLMParam), callback_type]
            self.rkllm_init.restype = ctypes.c_int
            
            self.rkllm_run = _rkllm_lib.rkllm_run
            self.rkllm_run.argtypes = [RKLLM_Handle_t, ctypes.POINTER(RKLLMInput), ctypes.POINTER(RKLLMInferParam), ctypes.c_void_p]
            self.rkllm_run.restype = ctypes.c_int
            
            self.rkllm_destroy = _rkllm_lib.rkllm_destroy
            self.rkllm_destroy.argtypes = [RKLLM_Handle_t]
            self.rkllm_destroy.restype = ctypes.c_int
            
            log_memory_usage("Before calling rkllm_init (model loading)")
            L.info("Loading RKNN model... This may take some time and memory.")
            
            # 初始化模型 - 这里是内存使用的关键点
            start_time = time.time()
            result = self.rkllm_init(ctypes.byref(_model_handle), ctypes.byref(rkllm_param), _callback)
            end_time = time.time()
            
            if result != 0:
                L.error(f"Failed to initialize RKNN model, error code: {result}")
                log_memory_usage("After failed model initialization")
                return False
            
            log_memory_usage("After successful model loading")
            L.info(f"Model loading completed in {end_time - start_time:.2f} seconds")
            
            # 设置推理参数
            self.rkllm_infer_params = RKLLMInferParam()
            ctypes.memset(ctypes.byref(self.rkllm_infer_params), 0, ctypes.sizeof(RKLLMInferParam))
            self.rkllm_infer_params.mode = RKLLMInferMode.RKLLM_INFER_GENERATE
            self.rkllm_infer_params.lora_params = None
            self.rkllm_infer_params.keep_history = 0
            
            _is_loaded = True
            
            # 最终内存状态
            log_memory_usage("Final memory state after complete initialization")
            
            # 计算模型加载占用的内存（简单估算）
            try:
                final_memory = get_memory_info()
                L.info(f"RKNN model initialized successfully")
                L.info(f"Model file: {model_path}")
                L.info(f"Current process memory usage: {final_memory['rss']:.1f}MB RSS, {final_memory['vms']:.1f}MB VMS")
                
                # 获取模型文件大小进行对比
                if os.path.exists(model_path):
                    model_file_size = os.path.getsize(model_path) / 1024 / 1024
                    L.info(f"Model file size on disk: {model_file_size:.1f}MB")
                
            except Exception as e:
                L.warning(f"Failed to calculate memory usage: {str(e)}")
            
            return True
            
        except Exception as e:
            L.error(f"Failed to initialize RKNN model: {str(e)} traceback: {traceback.format_exc()}")
            log_memory_usage("After model initialization error")
            return False
    
    def run_inference(self, prompt: str) -> str:
        """运行推理，完全按照 flask_server.py 的实现"""
        global _global_text, _global_state, _is_loaded, _model_handle
        
        if not _is_loaded:
            raise Exception("RKNN model not loaded")
        
        with _inference_lock:
            try:
                # 重置全局状态
                _global_text = []
                _global_state = -1
                
                # 创建输入
                rkllm_input = RKLLMInput()
                rkllm_input.input_mode = RKLLMInputMode.RKLLM_INPUT_PROMPT
                rkllm_input.input_data.prompt_input = ctypes.c_char_p(prompt.encode('utf-8'))
                
                # 创建推理线程，完全按照 flask_server.py
                def run_model():
                    self.rkllm_run(_model_handle, ctypes.byref(rkllm_input), ctypes.byref(self.rkllm_infer_params), None)
                
                model_thread = threading.Thread(target=run_model)
                model_thread.start()
                
                # 等待推理完成并收集结果，完全按照 flask_server.py
                rkllm_output = ""
                model_thread_finished = False
                while not model_thread_finished:
                    while len(_global_text) > 0:
                        rkllm_output += _global_text.pop(0)
                        time.sleep(0.005)

                    model_thread.join(timeout=0.005)
                    model_thread_finished = not model_thread.is_alive()
                    
                    if _global_state == LLMCallState.RKLLM_RUN_ERROR:
                        raise Exception("RKNN inference error")
                
                model_thread.join()
                return rkllm_output
                
            except Exception as e:
                L.error(f"RKNN inference failed: {str(e)} traceback: {traceback.format_exc()}")
                raise e
    
    def run_inference_stream(self, prompt: str):
        """流式推理，改进超时控制和资源清理"""
        global _global_text, _global_state, _is_loaded, _model_handle
        
        if not _is_loaded:
            raise Exception("RKNN model not loaded")
        
        # 使用更短的锁超时，避免长时间阻塞
        lock_acquired = _inference_lock.acquire(timeout=5.0)
        if not lock_acquired:
            L.error("Failed to acquire inference lock within 5 seconds")
            raise Exception("RKNN inference lock timeout - another request may be stuck")
        
        try:
            # 重置全局状态
            _global_text = []
            _global_state = -1
            
            # 创建输入
            rkllm_input = RKLLMInput()
            rkllm_input.input_mode = RKLLMInputMode.RKLLM_INPUT_PROMPT
            rkllm_input.input_data.prompt_input = ctypes.c_char_p(prompt.encode('utf-8'))
            
            # 使用标志控制推理线程
            inference_running = threading.Event()
            inference_error = threading.Event()
            inference_completed = threading.Event()
            
            def run_model():
                try:
                    inference_running.set()
                    result = self.rkllm_run(_model_handle, ctypes.byref(rkllm_input), ctypes.byref(self.rkllm_infer_params), None)
                    if result != 0:
                        L.error(f"RKNN inference failed with code: {result}")
                        inference_error.set()
                except Exception as e:
                    L.error(f"RKNN model thread error: {str(e)}")
                    inference_error.set()
                finally:
                    inference_running.clear()
                    inference_completed.set()
            
            model_thread = threading.Thread(target=run_model, daemon=True)
            model_thread.start()
            
            # 等待推理开始
            if not inference_running.wait(timeout=5.0):
                L.error("RKNN inference failed to start within 5 seconds")
                # 确保线程清理
                inference_error.set()
                model_thread.join(timeout=2.0)
                raise Exception("RKNN inference failed to start")
            
            # 流式返回结果，添加更严格的超时控制
            start_time = time.time()
            last_output_time = start_time
            no_output_timeout = 30  # 30秒没有输出则超时
            max_inference_time = 300  # 最大推理时间5分钟
            
            model_thread_finished = False
            total_chunks_yielded = 0
            
            while not model_thread_finished:
                current_time = time.time()
                
                # 检查是否有错误
                if inference_error.is_set():
                    L.error("RKNN inference encountered an error, breaking loop")
                    break
                
                # 检查总时间超时
                if current_time - start_time > max_inference_time:
                    L.error(f"RKNN inference total timeout after {max_inference_time}s")
                    inference_error.set()  # 设置错误标志，帮助线程退出
                    break
                
                # 检查输出超时（只有在已经有输出后才检查）
                if total_chunks_yielded > 0 and current_time - last_output_time > no_output_timeout:
                    L.error(f"RKNN inference no output timeout after {no_output_timeout}s")
                    inference_error.set()  # 设置错误标志
                    break
                
                # 处理输出
                has_output = False
                while len(_global_text) > 0:
                    try:
                        chunk = _global_text.pop(0)
                        last_output_time = current_time
                        has_output = True
                        total_chunks_yielded += 1
                        yield chunk
                    except IndexError:
                        # 并发访问可能导致的索引错误
                        break
                
                # 检查线程状态
                model_thread.join(timeout=0.01)
                model_thread_finished = not model_thread.is_alive()
                
                # 检查推理状态
                if _global_state == LLMCallState.RKLLM_RUN_ERROR:
                    L.error("RKNN inference error state detected")
                    break
                elif _global_state == LLMCallState.RKLLM_RUN_FINISH:
                    model_thread_finished = True
                
                # 如果没有输出且线程还在运行，短暂休眠
                if not has_output and not model_thread_finished:
                    time.sleep(0.01)
            
            # 强制清理：确保线程结束
            if model_thread.is_alive():
                L.warning("RKNN inference thread still running, forcing cleanup...")
                inference_error.set()  # 尝试通过错误标志让线程退出
                model_thread.join(timeout=3.0)
                if model_thread.is_alive():
                    L.error("RKNN inference thread failed to cleanup properly - this may affect future requests")
            
            # 处理剩余的输出
            remaining_chunks = 0
            while len(_global_text) > 0 and remaining_chunks < 100:  # 防止无限循环
                try:
                    chunk = _global_text.pop(0)
                    remaining_chunks += 1
                    yield chunk
                except IndexError:
                    break
            
            if remaining_chunks >= 100:
                L.warning("Too many remaining chunks, may indicate a problem")
                
        except Exception as e:
            L.error(f"RKNN stream inference failed: {str(e)} traceback: {traceback.format_exc()}")
            # 确保错误情况下也清理状态
            _global_text = []
            _global_state = -1
            raise e
        finally:
            # 最终清理：确保锁被释放和状态被重置
            try:
                # 清理全局状态
                _global_text = []
                _global_state = -1
            except:
                pass
            finally:
                _inference_lock.release()
                L.debug("RKNN inference lock released")

    def destroy(self):
        """销毁模型"""
        global _is_loaded, _global_text, _model_handle
        
        if _is_loaded:
            try:
                log_memory_usage("Before model destruction")
                
                self.rkllm_destroy(_model_handle)
                _is_loaded = False
                # 清理内存
                _global_text = []
                _model_handle = None
                
                # 强制垃圾回收
                gc.collect()
                
                log_memory_usage("After model destruction and cleanup")
                L.info("RKNN model destroyed")
            except Exception as e:
                L.error(f"Failed to destroy RKNN model: {str(e)}")
    
    def run_inference_stream_with_timeout(self, prompt: str, timeout: int = 60):
        """流式推理，使用传入的超时参数"""
        global _global_text, _global_state, _is_loaded, _model_handle
        
        if not _is_loaded:
            raise Exception("RKNN model not loaded")
        
        # 使用传入的超时参数计算锁超时
        lock_timeout = min(timeout / 2, 5.0)
        lock_acquired = _inference_lock.acquire(timeout=lock_timeout)
        if not lock_acquired:
            L.error(f"Failed to acquire inference lock within {lock_timeout}s")
            raise Exception("RKNN inference lock timeout - another request may be stuck")
        
        try:
            # 重置全局状态
            _global_text = []
            _global_state = -1
            
            # 创建输入
            rkllm_input = RKLLMInput()
            rkllm_input.input_mode = RKLLMInputMode.RKLLM_INPUT_PROMPT
            rkllm_input.input_data.prompt_input = ctypes.c_char_p(prompt.encode('utf-8'))
            
            # 使用标志控制推理线程
            inference_running = threading.Event()
            inference_error = threading.Event()
            inference_completed = threading.Event()
            
            def run_model():
                try:
                    inference_running.set()
                    result = self.rkllm_run(_model_handle, ctypes.byref(rkllm_input), ctypes.byref(self.rkllm_infer_params), None)
                    if result != 0:
                        L.error(f"RKNN inference failed with code: {result}")
                        inference_error.set()
                except Exception as e:
                    L.error(f"RKNN model thread error: {str(e)}")
                    inference_error.set()
                finally:
                    inference_running.clear()
                    inference_completed.set()
            
            model_thread = threading.Thread(target=run_model, daemon=True)
            model_thread.start()
            
            # 等待推理开始
            start_timeout = min(timeout / 4, 5.0)
            if not inference_running.wait(timeout=start_timeout):
                L.error(f"RKNN inference failed to start within {start_timeout}s")
                inference_error.set()
                model_thread.join(timeout=2.0)
                raise Exception("RKNN inference failed to start")
            
            # 使用传入的超时参数
            start_time = time.time()
            last_output_time = start_time
            no_output_timeout = timeout  # 使用传入的超时参数
            max_inference_time = timeout  # 使用传入的超时参数
            
            model_thread_finished = False
            total_chunks_yielded = 0
            
            while not model_thread_finished:
                current_time = time.time()
                
                # 检查是否有错误
                if inference_error.is_set():
                    L.error("RKNN inference encountered an error, breaking loop")
                    break
                
                # 检查总时间超时
                if current_time - start_time > max_inference_time:
                    L.error(f"RKNN inference total timeout after {max_inference_time}s")
                    inference_error.set()
                    break
                
                # 检查输出超时（只有在已经有输出后才检查）
                if total_chunks_yielded > 0 and current_time - last_output_time > no_output_timeout:
                    L.error(f"RKNN inference no output timeout after {no_output_timeout}s")
                    inference_error.set()
                    break
                
                # 处理输出
                has_output = False
                while len(_global_text) > 0:
                    try:
                        chunk = _global_text.pop(0)
                        last_output_time = current_time
                        has_output = True
                        total_chunks_yielded += 1
                        yield chunk
                    except IndexError:
                        break
                
                # 检查线程状态
                model_thread.join(timeout=0.01)
                model_thread_finished = not model_thread.is_alive()
                
                # 检查推理状态
                if _global_state == LLMCallState.RKLLM_RUN_ERROR:
                    L.error("RKNN inference error state detected")
                    break
                elif _global_state == LLMCallState.RKLLM_RUN_FINISH:
                    model_thread_finished = True
                
                # 如果没有输出且线程还在运行，短暂休眠
                if not has_output and not model_thread_finished:
                    time.sleep(0.01)
            
            # 强制清理：确保线程结束
            if model_thread.is_alive():
                L.warning("RKNN inference thread still running, forcing cleanup...")
                inference_error.set()
                cleanup_timeout = min(timeout / 4, 3.0)
                model_thread.join(timeout=cleanup_timeout)
                if model_thread.is_alive():
                    L.error("RKNN inference thread failed to cleanup properly - this may affect future requests")
            
            # 处理剩余的输出
            remaining_chunks = 0
            while len(_global_text) > 0 and remaining_chunks < 100:
                try:
                    chunk = _global_text.pop(0)
                    remaining_chunks += 1
                    yield chunk
                except IndexError:
                    break
            
            if remaining_chunks >= 100:
                L.warning("Too many remaining chunks, may indicate a problem")
                
        except Exception as e:
            L.error(f"RKNN stream inference failed: {str(e)} traceback: {traceback.format_exc()}")
            _global_text = []
            _global_state = -1
            raise e
        finally:
            try:
                _global_text = []
                _global_state = -1
            except:
                pass
            finally:
                _inference_lock.release()
                L.debug("RKNN inference lock released")
