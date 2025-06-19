from enum import Enum
from dataclasses import dataclass, asdict
import json
from typing import List, Optional, Literal, Union
from pydantic import BaseModel

class AbNormalState(Enum):
    # 异常状态
    USING_PHONE = ("USING_PHONE", 400)
    SITTING_UP = ("SITTING_UP", 401)
    LEAVING = ("LEAVING", 402)

    def __init__(self, name: str, code: int):
        self._name = name
        self._code = code

    @property
    def name(self) -> str:
        return self._name

    @property
    def code(self) -> int:
        return self._code
    
    @property
    def all_states(self) -> List[str]:
        return [state.name for state in AbNormalState]
    
    @classmethod
    def is_abnormal(cls, name:str) -> bool:
        return name in [abnormal.name for abnormal in AbNormalState]
    
class SleepType(Enum):
  Awake = 0
  HalfSleep = 1
  LightSleep = 2
  DeepSleep = 3

  def __str__(self):
    return self.name

  def to_dict(self):
      return self.name


class PoseType(Enum):
  LieFlat = 1
  HalfLie = 2
  LieSide = 3
  LieFaceDown = 4
  SitDown = 5
  Stand = 6
  Other = 16


class SleepStatus(str, Enum):
    Awake = "Awake"
    HalfSleep = "HalfSleep"
    LightSleep = "LightSleep"
    DeepSleep = "DeepSleep"

class BodyPoseType(str, Enum):
    Stand = "Stand"
    Sit = "Sit"
    Lie = "Lie"
    SitDown = "SitDown"

class HeadPoseType(str, Enum):
    Normal = "Normal"
    Bow = "Bow"
    TiltLeft = "TiltLeft"
    TiltRight = "TiltRight"

class HandPoseType(str, Enum):
    BodySide = "BodySide"
    RaisedUp = "RaisedUp"
    Forward = "Forward"

class EyeStatus(str, Enum):
    Open = "Open"
    Closed = "Closed"

class MouthStatus(str, Enum):
    Open = "Open"
    Closed = "Closed"

class FootStatus(str, Enum):
    OnLoad = "OnLoad"
    OffLoad = "OffLoad"

class ActionStatus(str, Enum):
    MotionLess = "MotionLess"
    Moving = "Moving"
  
@dataclass
class PoseResult:
  pose_type: PoseType
  pose_prob: float

  leftEyeClosed: bool
  rightEyeClosed: bool
  eyeCloseProb: float

@dataclass
class PoseInfo:
    body: Optional[str] = None
    body_prob: Optional[float] = None
    head: Optional[str] = None
    head_prob: Optional[float] = None
    left_hand: Optional[str] = None
    left_hand_prob: Optional[float] = None
    right_hand: Optional[str] = None
    right_hand_prob: Optional[float] = None
    left_eye: Optional[str] = None
    left_eye_prob: Optional[float] = None
    right_eye: Optional[str] = None
    right_eye_prob: Optional[float] = None
    mouth: Optional[str] = None
    mouth_prob: Optional[float] = None
    foot: Optional[str] = None
    foot_prob: Optional[float] = None

@dataclass
class RecentAction:
    face_action: str
    face_prob: float
    body_action: str
    body_prob: float
    arm_action: str
    arm_prob: float

@dataclass
class SleepResult:
    sleep_type: Optional[SleepType] = None
    sleep_prob: Optional[float] = None
    duration: Optional[int] = None
    timestamp: Optional[float] = None
    pose_info: Optional[PoseInfo] = None
    recent_action: Optional[RecentAction] = None

    def to_dict(self):
        data = asdict(self)
        data['sleep_type'] = self.sleep_type.to_dict()  # 使用 to_dict 方法转换 Enum
        return data

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_dict(cls, data: dict):
        try:
            # 处理 sleep_type
            sleep_type = SleepType[data.get('sleep_type')] if data.get('sleep_type') else None
            
            # 处理 pose_info
            pose_info_data = data.get('pose_info', {})
            if pose_info_data:
                # 过滤掉 PoseInfo 不接受的参数
                valid_fields = {
                    k: v for k, v in pose_info_data.items() 
                    if k in PoseInfo.__dataclass_fields__
                }
                pose_info = PoseInfo(**valid_fields)
            else:
                pose_info = None
            
            # 处理 recent_action
            recent_action_data = data.get('recent_action', {})
            if recent_action_data:
                recent_action = RecentAction(**recent_action_data)
            else:
                recent_action = None
            
            return cls(
                sleep_type=sleep_type,
                sleep_prob=data.get('sleep_prob'),
                duration=data.get('duration'),
                timestamp=data.get('timestamp'),
                pose_info=pose_info,
                recent_action=recent_action
            )
        except Exception as e:
            print(f"Error parsing sleep result data: {e}")
            # 发生异常时返回一个包含基本信息的对象
            return cls(
                sleep_type=None,
                sleep_prob=None,
                duration=None,
                timestamp=None,
                pose_info=None,
                recent_action=None
            )

@dataclass
class ApiResponse:
    status_code: int
    user_id: str
    conversation_id: Optional[str]
    message_id: Optional[str]
    message: str
    sleep_status: str
    data: SleepResult

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)

    def to_dict(self):
        sleep_result = self.data.to_dict() if isinstance(self.data, SleepResult) else self.data
        return {
            'status_code': self.status_code,
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'message_id': self.message_id,
            'message': self.message,
            'sleep_status': self.sleep_status,
            'data': sleep_result
        }

    @classmethod
    def from_dict(cls, data: dict):
        try:
            sleep_result_data = data['data']
            sleep_result = SleepResult.from_dict(sleep_result_data)
        except (KeyError, TypeError) as e:
            print(f"Error parsing sleep result data: {e}")
            sleep_result = data['data']

        return cls(
            status_code=data['status_code'],
            user_id=data['user_id'],
            conversation_id=data.get('conversation_id'),
            message_id=data.get('message_id'),
            message=data['message'],
            sleep_status=data['sleep_status'],
            data=sleep_result
        )

class ImageDataPayload(BaseModel):
    format: str = "jpeg"
    data: List[str]

class AudioDataPayload(BaseModel):
    format: str = "wav"
    encoding: str = "pcm_s16le"
    sample_rate: int = 16000
    channels: int = 1
    sample_format: str = "s16"
    data: str

class SceneExecStatus(BaseModel):
    command: Optional[str] = None
    scene: Optional[str] = None
    scene_seq: Optional[int] = None
    status: Optional[str] = None # IN_PROGRESS,COMPLETED
    
class ReportReqData(BaseModel):
    images: ImageDataPayload
    audio: Optional[AudioDataPayload] = None
    scene_exec_status: Optional[SceneExecStatus] = None

class FragranceStatus(str, Enum):
    ON = "on"
    OFF = "off"

class DisplayType(str, Enum):
    TEXT = "text"
    VIDEO = "video"

class DisplayStyle(str, Enum):
    NORMAL = "normal"
    BOLD = "bold"
    BLINK = "blink"

class MediaAction(str, Enum):
    PLAY = "play"
    STOP = "stop"
    FADE_OUT = "fade_out"

class AudioFormat(str, Enum):
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"

class VideoFormat(str, Enum):
    MP4 = "mp4"
    MOV = "mov"

class FragranceAction(BaseModel):
    status: FragranceStatus
    level: Optional[int] = None  # 1-10
    count: Optional[int] = None  # 喷香次数

class LightMode(str, Enum):
    OFF = "Off"        # 关闭灯光
    BREATHING = "Breathing"    # 呼吸模式
    SHADOWING = "Shadowing"    # 拖影模式
    GRADIENT = "Gradient"      # 渐变模式
    STATIC = "Static"      # 静态模式
    
class LightAction(BaseModel):
    mode: LightMode  # 使用已有的LightMode枚举
    rgb: Optional[str] = None  # "rgb(255, 255, 255)"

class VoiceAction(BaseModel):
    action: str  # "play", "stop"
    volume: Optional[int] = None  # 0-100
    audio_data: Optional[str] = None  # base64 encoded
    audio_format: Optional[str] = None  # e.g., "mp3", "wav"
    filename: Optional[str] = None  # e.g., "sleep_guide.mp3"
    wait_time: Optional[float] = None  # seconds to wait after playing     
    text_interval: Optional[float] = None  # seconds to wait between text segments
    repeat: Optional[int] = None  # repeat times for single audio, 0 means infinite 
    text: Optional[Union[str, List[str]]] = None  # text to speech - can be a single string or a list of strings

class VoiceSequence(BaseModel): 
    voices: list[VoiceAction]  # sequence of voice actions 
    repeat: Optional[int] = None  # repeat times for whole sequence, 0 means infinite     
    
class BgmAction(BaseModel):
    action: Optional[MediaAction] = None
    volume: Optional[int] = None  # -100 - 100
    audio_data: Optional[str] = None  # base64 encoded
    audio_format: Optional[AudioFormat] = None
    filename: Optional[str] = None  # e.g., "night_rain.mp3"

class DisplayAction(BaseModel):
    display_type: Optional[DisplayType] = None
    action: Optional[MediaAction] = None
    content: Optional[str] = None
    style: Optional[DisplayStyle] = None
    video_data: Optional[str] = None  # base64 encoded
    video_format: Optional[VideoFormat] = None
    filename: Optional[str] = None  # e.g., "sleep.mp4"

class Actions(BaseModel):
    fragrance: Optional[FragranceAction] = None
    light: Optional[LightAction] = None
    voice: Optional[VoiceSequence] = None
    bgm: Optional[BgmAction] = None
    display: Optional[DisplayAction] = None
    action_feature: Optional[str] = None
    skip_photo_capture: Optional[bool] = False

class ActionRespData(BaseModel):
    cmd:str
    scene: str  
    scene_seq: Optional[int] = None
    actions: Actions

class SleepSignals(BaseModel):
    posture: Optional[Literal["sitting", "lying", "semi-reclined", "standing"]] = None
    eyes: Optional[Literal["open", "closed"]] = None
    handActivity: Optional[Literal["active_device_use","passive_device_placement", "reading", "eating", "none"]] = None

class PersonStatus(BaseModel):
    personPresent: Optional[bool] = None
    sleepSignals: Optional[SleepSignals] = None
    sleeping: Optional[bool] = None