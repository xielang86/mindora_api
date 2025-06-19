import pyaudio
import webrtcvad
import asyncio
import logging
import traceback
from typing import  AsyncGenerator
from pathlib import Path
from aivc.utils.id import get_message_id
import concurrent.futures
import struct 
import queue
import threading
import io
import pydub
import tempfile
import pydub.playback  
import soundfile as sf  
import sounddevice as sd  # 添加新的导入
import numpy as np
import wave  # 添加新的导入

logger = logging.getLogger(__name__)

class AudioHandler:
    # 更新音频配置
    RATE = 16000
    CHANNELS = 1
    FORMAT = pyaudio.paInt16  # PCM S16LE format
    CHUNK = 480  # 调整为30ms帧长度 (16000 * 0.03 = 480)，这是webrtcvad支持的帧长度

    def __init__(self, vad_aggressiveness=3, vad_frame_duration=30):
        self.audio = pyaudio.PyAudio()
        # 允许配置VAD攻击性级别：0-3，数字越大越敏感
        self.vad = webrtcvad.Vad(vad_aggressiveness)
        self.vad_frame_duration = vad_frame_duration  # 帧持续时间，单位毫秒（可以是10, 20, 30）
        self.sample_rate = self.RATE
        # 确保CHUNK大小符合VAD要求
        self.chunk_size = int(self.RATE * self.vad_frame_duration / 1000)
        # 创建数据目录
        self.data_dir = Path("data")
        self.send_dir = self.data_dir / "send"
        self.recv_dir = self.data_dir / "recv"
        self.send_dir.mkdir(parents=True, exist_ok=True)
        self.recv_dir.mkdir(parents=True, exist_ok=True)
        self._active = False
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="audio")
        self.current_playing_message_id = None
        self.play_stream = None
        self.play_queue = queue.Queue()   
        self.discarded_messages = set()   # 需要丢弃的消息ID
        self.latest_message_id = None  # 跟踪最新的消息ID
        self.playing_message = None  # 当前正在播放的消息信息
        self.message_buffers = {}  # 存储每个消息ID的音频片段
        self.play_thread = None
        self.play_thread_active = False
        self._start_play_thread()
        self.current_audio_format = None  # 添加当前音频格式跟踪
        self.current_play_counter = 0  # 添加计数器来跟踪当前播放
        self.play_event = threading.Event()
        self.play_event.set()
        self.current_playback = None  # 添加变量跟踪当前播放对象
        self.audio_input = None  # 添加音频输入流属性
        self.stream = None  # 添加音频流属性
    
    # 添加函数来确保音频数据长度符合VAD要求
    def _frame_generator(self, audio_data):
        """将音频数据分割成适合VAD处理的帧"""
        frame_duration_ms = 30  # 使用30ms帧
        frame_size = int(self.RATE * frame_duration_ms / 1000)  # 每帧的采样点数
        
        # 确保数据长度是帧大小的整数倍
        frames_count = len(audio_data) // (2 * frame_size)  # 2是因为每个样本占2字节
        
        for i in range(frames_count):
            start = i * frame_size * 2
            end = (i + 1) * frame_size * 2
            yield audio_data[start:end]

    def _start_play_thread(self):
        if self.play_thread is None or not self.play_thread.is_alive():
            self.play_thread_active = True
            self.play_thread = threading.Thread(target=self._play_thread_worker, name="audio_player")
            self.play_thread.daemon = True
            self.play_thread.start()

    def _play_thread_worker(self):
        while self.play_thread_active:
            try:
                audio_data, message_id, stream_seq, audio_format = self.play_queue.get(timeout=0.1)
                logger.info(f"Playing audio stream_seq:{stream_seq} message_id:{message_id} audio_format:{audio_format}")
                
                # 根据音频格式选择播放方式
                if audio_format == 'mp3':
                    logger.info(f"Playing MP3 audio message_id:{message_id}")
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                        tmp_file.write(audio_data)
                        tmp_file.flush()
                        audio = pydub.AudioSegment.from_mp3(tmp_file.name)
                        # 转换为numpy数组
                        samples = np.array(audio.get_array_of_samples())
                        # 如果是立体声,转换为mono
                        if audio.channels == 2:
                            samples = samples.reshape((-1, 2))
                        try:
                            self.current_playback = sd.play(samples, audio.frame_rate)
                        except Exception as e:
                            logger.error(f"Error playing MP3: {e}")
                            
                elif audio_format == 'ogg_opus':
                    try:
                        # 直接读取并播放opus数据
                        data_io = io.BytesIO(audio_data)
                        data, samplerate = sf.read(data_io)
                        sd.play(data, samplerate)
                        sd.wait()  # 等待播放完成
                    except Exception as e:
                        logger.error(f"Error playing OGG/OPUS audio: {e}")
                        
                else:
                    # PCM格式的处理
                    if not self.play_stream:
                        self.play_stream = self._create_stream(audio_format=audio_format)
                        self.playing_message = message_id

                    if self.playing_message == message_id and self.play_stream:
                        try:
                            logger.info(f"Playing PCM audio stream_seq:{stream_seq} message_id:{message_id}")
                            self.play_stream.write(audio_data)
                        except OSError as e:
                            logger.error(f"Error writing to audio stream: {e}")
                            self._stop_current_playback()
                            continue

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in play thread: {e} stack: {traceback.format_exc()}")
                self._stop_current_playback()

    def save_audio(self, pcm_data: bytes, filename: str, is_send: bool = True, file_extension:str="pcm") -> None:
        save_dir = self.send_dir if is_send else self.recv_dir
        filepath = save_dir / f"{filename}{file_extension}"
        with open(filepath, "wb") as f:
            f.write(pcm_data)
        
    def get_audio_level(self, data: bytes) -> float:
        # 将字节转换为短整数
        shorts = struct.unpack(f'{len(data)//2}h', data)
        # 计算均方根值作为音量指标
        return (sum(s**2 for s in shorts) / len(shorts))**0.5

    async def detect_voice(self, 
                          min_speech_chunks=10, 
                          volume_threshold=500, 
                          silence_multiplier=2,
                          dynamic_threshold=False) -> AsyncGenerator[tuple[bytes, str], None]:
        """
        检测语音并生成音频数据
        
        Args:
            min_speech_chunks: 识别为有效语音的最小块数
            volume_threshold: 音量阈值，超过此值被视为有效语音
            silence_multiplier: 结束检测的静音时长倍数（相对于min_speech_chunks）
            dynamic_threshold: 是否使用动态音量阈值
        """
        self._active = True
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        silence_counter = 0
        voice_detected = False
        audio_buffer = []
        MIN_CHUNKS = min_speech_chunks
        valid_speech_chunks = 0 
        VOLUME_THRESHOLD = volume_threshold
        
        # 用于动态音量阈值计算
        background_noise_levels = []
        
        try:
            while self._active:
                if not hasattr(self, 'stream') or not self.stream.is_active():
                    break
                    
                try:
                    data = await asyncio.get_event_loop().run_in_executor(
                        self._executor,
                        lambda: self.stream.read(self.chunk_size, exception_on_overflow=False)
                    )
                    
                    if not data:
                        logger.warning("Empty audio data received")
                        continue
                    
                    # 确保数据长度符合VAD要求
                    if len(data) != self.chunk_size * 2:  # 每个样本2字节
                        logger.warning(f"Unexpected data length: {len(data)}, expected: {self.chunk_size * 2}")
                        continue
                    
                    try:
                        is_speech = self.vad.is_speech(data, self.sample_rate)
                        audio_level = self.get_audio_level(data)
                    except Exception as e:
                        logger.error(f"VAD error: {e}, data length: {len(data)}")
                        continue
                    
                    # 更新动态阈值计算
                    if dynamic_threshold and not voice_detected:
                        if len(background_noise_levels) < 30:  # 收集30帧背景噪音
                            background_noise_levels.append(audio_level)
                        else:
                            # 动态阈值为背景噪音平均值的3倍
                            avg_noise = sum(background_noise_levels) / len(background_noise_levels)
                            VOLUME_THRESHOLD = max(volume_threshold, avg_noise * 3)
                            background_noise_levels.pop(0)  # 移除最老的样本
                    
                    if is_speech and audio_level > VOLUME_THRESHOLD:
                        silence_counter = 0
                        voice_detected = True
                        audio_buffer.append(data)
                        valid_speech_chunks += 1
                        logger.debug(f"语音检测: 音量={audio_level:.2f}, 阈值={VOLUME_THRESHOLD:.2f}, 有效帧={valid_speech_chunks}")
                    elif voice_detected:
                        silence_counter += 1
                        audio_buffer.append(data)

                        logger.debug(f"静音检测: 音量={audio_level:.2f}, 静音计数={silence_counter}/{MIN_CHUNKS*silence_multiplier}")

                        if silence_counter > MIN_CHUNKS * silence_multiplier: 
                            audio_data = b''.join(audio_buffer)
                            if valid_speech_chunks >= MIN_CHUNKS:
                                message_id = get_message_id()
                                if self.playing_message:
                                    self.discarded_messages.add(self.playing_message)
                                try:
                                    with open(self.send_dir / f"{message_id}.pcm", "wb") as f:
                                        f.write(audio_data)
                                    
                                    yield audio_data, message_id
                                except Exception as e:
                                    logger.error(f"Error saving audio: {e}\n{traceback.format_exc()}")
                            audio_buffer = []
                            voice_detected = False
                            silence_counter = 0
                            valid_speech_chunks = 0 
                        
                except IOError as e:
                    logger.warning(f"Audio input overflow occurred: {e}")
                    await asyncio.sleep(0.1)
                    continue
                except Exception as e:
                    logger.error(f"Error reading audio: {e}\n{traceback.format_exc()}")
                    await asyncio.sleep(0.1)  # 避免死循环
                    
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Voice detection stopped")
        finally:
            self.close()

    def _create_audio_input(self):
        """创建音频输入流"""
        return self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

    async def record_fixed_duration(self, duration=5, rate=16000, channels=1, chunk=1024):
        """
        录制固定时长的音频
        
        Args:
            duration: 录制时长（秒）
            rate: 采样率
            channels: 声道数
            chunk: 缓冲区大小
        """
        format = pyaudio.paInt16  # 16位格式
        
        # 创建内存流来保存音频数据
        frames = []
        
        try:
            stream = self.audio.open(
                format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk
            )
            
            # 计算需要读取的次数
            for _ in range(0, int(rate / chunk * duration)):
                data = stream.read(chunk, exception_on_overflow=False)
                frames.append(data)
                
            stream.stop_stream()
            stream.close()
            
            # 使用 BytesIO 构建 WAV 文件
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(self.audio.get_sample_size(format))
                wf.setframerate(rate)
                wf.writeframes(b''.join(frames))
                
            return wav_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error in recording audio: {e}")
            raise

    def close(self):
        self._active = False
        self.play_thread_active = False

        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)

        self._stop_current_playback()
        
        for resource in (self.stream, self._executor, self.audio):
            if resource:
                try:
                    if hasattr(resource, 'stop_stream'):
                        resource.stop_stream()
                    elif hasattr(resource, 'shutdown'):
                        resource.shutdown(wait=False)
                    elif hasattr(resource, 'terminate'):
                        resource.terminate()
                except Exception as e:
                    logger.error(f"Error closing {type(resource)}: {e}")
        
        self.stream = None
        self._executor = None
        self.audio = None

        if self.audio_input:
            self.audio_input.stop_stream()
            self.audio_input.close()

    def _stop_current_playback(self):
        if self.current_playback:
            sd.stop()
            self.current_playback = None
            
        if self.play_stream:
            try:
                self.play_stream.stop_stream()
                self.play_stream.close()
            except Exception as e:
                logger.error(f"Error stopping playback: {e}")
            finally:
                self.play_stream = None
                self.playing_message = None
                self.current_audio_format = None  
                
        while not self.play_queue.empty():
            try:
                self.play_queue.get_nowait()
            except Exception as e:
                logger.error(f"Error clearing play queue: {e}")
                break

    def _create_stream(self, audio_format='pcm'):
        if audio_format == 'pcm':
            return self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True
            )
        elif audio_format in ['mp3', 'ogg_opus']:
            # MP3和OPUS格式不需要创建流
            return None

    def play_audio(self, 
                audio_data: bytes, 
                message_id: str, 
                stream_seq: int, 
                audio_format: str = 'pcm') -> None:
        if audio_format is None:
            file_extension = '.pcm'
        else:
            file_extension = '.' + audio_format
        self.save_audio(audio_data, f"{message_id}_{stream_seq}", False, file_extension)
        
        # 如果是新消息的第一个音频片段，立即停止当前播放
        logger.info(f"Playing audio stream_seq:{stream_seq} message_id:{message_id}  playing_message:{self.playing_message}")
        if stream_seq == 1 and message_id != self.playing_message:
            logger.info(f"Stopping current playback and starting new message: {message_id}")
            self._stop_current_playback()
            self.playing_message = message_id
            
        # 如果消息被标记为丢弃，则不处理
        if message_id in self.discarded_messages:
            return

        try:
            # 直接将音频数据放入队列，无需转换
            self.play_queue.put((audio_data, message_id, stream_seq, audio_format))
        except Exception as e:
            logger.error(f"Error processing audio data: {e}")

    def __del__(self):
        self.close()
