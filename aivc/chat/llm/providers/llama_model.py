import subprocess
import threading
import time
import os
import requests
from typing import Optional
from aivc.config.config import settings, L
import atexit
import signal


class LlamaModel:
    _instance: Optional['LlamaModel'] = None
    _lock = threading.Lock()
    _process: Optional[subprocess.Popen] = None
    _is_running: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._log_file = None  # 初始化日志文件句柄
            self._start_server()
            # 注册清理函数
            atexit.register(self._cleanup)
    
    def _start_server(self):
        """启动 llama-server"""
        if self._is_running:
            L.info("Llama server is already running")
            return
            
        try:
            # 检查模型文件是否存在
            if not os.path.exists(settings.CHAT_MODEL_CMD):
                L.error(f"Llama server executable not found: {settings.CHAT_MODEL_CMD}")
                return
                
            if not os.path.exists(settings.CHAT_MODEL):
                L.error(f"Llama model file not found: {settings.CHAT_MODEL}")
                return
            
            # 构建启动命令
            cmd = [
                settings.CHAT_MODEL_CMD,
                "-m", settings.CHAT_MODEL,
                "-b", "128000",
                "-t", "3",
                "--temp", "0.7",
                "--top-k", "20",
                "--top-p", "0.8",
                "--repeat-penalty", "1.05",
                "--samplers", "penalties;temperature;top_k;top_p",
                "-ub", "32",
                "--port", str(settings.LLAMA_SERVER_PORT),
                "--host", settings.LLAMA_SERVER_HOST,
            ]
            
            L.info(f"Starting llama-server with command: {' '.join(cmd)}")
            L.info(f"Llama server logs will be written to: {settings.LLAMA_SERVER_LOG}")
            start_time = time.time()
            
            # 打开日志文件
            log_file = open(settings.LLAMA_SERVER_LOG, 'a', encoding='utf-8')
            log_file.write(f"\n{'='*60}\n")
            log_file.write(f"Llama server started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"Command: {' '.join(cmd)}\n")
            log_file.write(f"{'='*60}\n")
            log_file.flush()
            
            # 启动进程，将输出重定向到日志文件
            self._process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,  # 将 stderr 也重定向到 stdout
                cwd=os.path.dirname(settings.CHAT_MODEL_CMD)
            )
            
            # 保存日志文件句柄以便后续关闭
            self._log_file = log_file
            
            # 等待服务器启动
            if self._wait_for_server():
                self._is_running = True
                load_time = int((time.time() - start_time) * 1000)
                L.info(f"Llama server started successfully in {load_time}ms on port {settings.LLAMA_SERVER_PORT}")
            else:
                L.error("Failed to start llama server")
                self._cleanup()
                
        except Exception as e:
            L.error(f"Error starting llama server: {str(e)}")
            self._cleanup()
    
    def _wait_for_server(self, timeout: int = 60) -> bool:
        """等待服务器启动完成"""
        start_time = time.time()
        health_url = f"http://{settings.LLAMA_SERVER_HOST}:{settings.LLAMA_SERVER_PORT}/health"
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(health_url, timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            
            # 检查进程是否还在运行
            if self._process and self._process.poll() is not None:
                stdout, stderr = self._process.communicate()
                L.error(f"Llama server process exited with code {self._process.returncode}")
                L.error(f"Stdout: {stdout.decode()}")
                L.error(f"Stderr: {stderr.decode()}")
                return False
                
            time.sleep(1)
        
        return False
    
    def is_healthy(self) -> bool:
        """检查服务器是否健康"""
        if not self._is_running or not self._process:
            return False
            
        try:
            health_url = f"http://{settings.LLAMA_SERVER_HOST}:{settings.LLAMA_SERVER_PORT}/health"
            response = requests.get(health_url, timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_server_url(self) -> str:
        """获取服务器URL"""
        return f"http://{settings.LLAMA_SERVER_HOST}:{settings.LLAMA_SERVER_PORT}"
    
    def _cleanup(self):
        """清理资源"""
        if self._process:
            try:
                L.info("Stopping llama server...")
                
                # 尝试优雅关闭
                self._process.terminate()
                
                # 等待进程结束
                try:
                    self._process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    L.warning("Llama server did not stop gracefully, forcing kill")
                    self._process.kill()
                    self._process.wait()
                
                L.info("Llama server stopped")
            except Exception as e:
                L.error(f"Error stopping llama server: {str(e)}")
            finally:
                self._process = None
                self._is_running = False
        
        # 关闭日志文件
        if hasattr(self, '_log_file') and self._log_file:
            try:
                self._log_file.write(f"\nLlama server stopped at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                self._log_file.close()
                self._log_file = None
            except Exception as e:
                L.error(f"Error closing llama server log file: {str(e)}")
    
    def restart(self):
        """重启服务器"""
        L.info("Restarting llama server...")
        self._cleanup()
        time.sleep(2)  # 等待端口释放
        self._start_server()