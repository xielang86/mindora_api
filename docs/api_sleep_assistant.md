

# 智能机器人睡眠助手接口文档

**版本:** 1.0
**最后更新日期:** 2025-1-17

## 概述

本文档定义了智能机器人用于场景感知和接收指令的 WebSocket 接口。机器人周期性地向服务端报告其感知到的环境信息（图像和音频），并接收服务端根据分析结果下发的指令，以控制机器人硬件设备。

## WebSocket 连接

| 项目 | 说明  |
|:------------- |:---------------| 
| 协议      | websocket |   
| 地址      | ws://114.55.90.104:9001/ws |  

本接口基于 WebSocket 协议进行双向通信。机器人和服务器需要先建立 WebSocket 连接才能进行数据交换。

## 上行接口：报告机器人状态 (`report-state`)

### 接口说明

机器人每隔 2 秒通过此接口向服务端报告当前感知到的环境信息（前提是检测到人脸），包括抓拍的图片和录制的音频数据。

### 请求方法

`report-state`

### 数据发送频率

每 2 秒一次

### 数据格式

JSON

### 请求数据格式

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| version      | 版本号 |   字符串| 1.0|是 |
| method      | 请求方法 |  字符串 | report-state| 是 |
| conversation_id      | 会话ID |  字符串 | 由客户端在连接建立时生成并维护，重连时更新 | 是 |
| message_id      | 消息ID |  字符串 | 每次发送消息时生成新的唯一 ID | 是 |
| token      | 认证令牌 |  字符串 | 用于身份验证，具体规则待定 | 是 |
| timestamp      | 时间戳 |  字符串 |  符合 RFC3339 格式的带时区的时间戳 | 是 |
| data      | 数据 |  PerceptionReqData 数据结构 | 见 PerceptionReqData 定义 | 是 |

#### PerceptionReqData 结构

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| images      | 图片数据 | ImageDataPayload 结构 |  | 是 |
| audio      | 音频数据 | AudioDataPayload 结构 |  | 否 |
| scene_exec_status      | 执行状态 | SceneExecStatus 结构 |  | 否 |

#### SceneExecStatus 结构

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| scene_seq       | 场景序号 |   int | 无 | 是 |
| status         | 执行状态 | 字符串 | IN_PROGRESS (进行中), COMPLETED (完成) | 是 |

#### ImageDataPayload 结构

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| format       | 图片格式 |   字符串 | jpeg | 是 |
| data         | 图片数据列表 | 字符串数组 | 缺省1280*720分辨率 | 是 |

#### AudioDataPayload 结构

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| format       | 音频格式 |   字符串 | wav | 是 |
| encoding     | 音频编码 |   字符串 | pcm_s16le | 是 |
| sample_rate  | 音频采样率 |   整数 | 16000 | 是 |
| channels     | 音频声道数 |   整数 | 1 | 是 |
| sample_format| 音频采样格式 |   字符串 | s16 | 是 |
| data         | 音频数据 |   字符串 |  | 是 |

### 请求示例

```
{
  "version": "1.0",
  "method": "report-state",
  "conversation_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "message_id": "20250117-103000-abcdef01-2345-6789-abcd-ef0123456789",
  "token": "your_authentication_token",
  "timestamp": "2025-01-17T10:30:00.000+08:00",
  "data": {
    "images": {
      "format": "jpeg",
      "data": [
        "base64_encoded_image_1",
        "base64_encoded_image_2"
      ]
    },
    "audio": {
      "format": "wav",
      "encoding": "pcm_s16le",
      "sample_rate": 16000,
      "channels": 1,
      "sample_format": "s16",
      "data": "base64_encoded_audio"
    },
    "scene_exec_status": {
        "scene_seq":6,
        "status":"COMPLETED"
    }
  }
}
```


## 下行接口：执行机器人指令 (`execute-command`)

### 接口说明

服务端通过此接口向机器人发送指令，包括当前场景信息以及需要机器人执行的硬件动作。

### 请求方法

`execute-command`

### 数据接收频率

实时，根据服务端分析结果推送

### 数据格式

JSON

### 响应数据格式

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| version      | 版本号 |   字符串| 1.0|是 |
| method      | 请求方法 |  字符串 | execute-command| 是 |
| conversation_id      | 会话ID |  字符串 | 回传请求字段 | 是 |
| message_id      | 消息ID |  字符串 | 服务端生成并维护的唯一 ID | 是 |
| code      | 状态码 |   整数 | 0 表示成功，其他表示失败 | 是 |
| message      | 状态描述 |   字符串 |  "success" 或具体的错误信息 | 是 |
| data      | 数据 |  ActionRespData 数据结构 | 见 ActionRespData 定义 | 是 |

#### ActionRespData 结构

| 参数 | 说明  | 数据格式|值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| scene      | 当前场景 |   字符串| 例如：Awake、LightSleep、DeepSleep |是 |
| actions      | 硬件动作指令 |   Actions 对象 | 见 Actions 定义 |是 |

#### Actions 定义

| 参数 | 说明  | 数据格式|可选值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| fragrance      | 香氛控制 |   FragranceAction 对象 | 见 FragranceAction 定义 | 否 |
| light      | 灯光控制 |   LightAction 对象 | 见 LightAction 定义 | 否 |
| voice      | 人声控制 |   VoiceSequence 对象 | 见 VoiceSequence 定义 | 否 |
| bgm      | 背景音乐 |   BGMAction 对象 | 见 BGMAction 定义 | 否 |
| display      | 屏幕显示	 |   DisplayAction 对象 | 见 DisplayAction 定义 | 否 |

#### FragranceAction 定义

| 参数 | 说明  | 数据格式|可选值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| status      | 状态 |   字符串 | on, off | 是 |
| level      | 浓度等级 |   整数 | 1-10 | 否 |
| count	      | 喷几次 |   整数 | 1-10 | 否 |

#### LightAction 定义

| 参数 | 说明  | 数据格式|可选值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| mode         | 灯光模式 | 字符串 | Off, Breathing, Shadowing, Gradient, Static  | 是 |
| rgb          | RGB 值 | 字符串 | 例如: "rgb(255, 255, 255)" | 是 |

#### VoiceSequence 定义

| 参数 | 说明  | 数据格式|可选值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| voices      | 音频序列 |   VoiceAction数组 | 见 VoiceAction 定义 | 是 |
| repeat      | 整个序列重复次数 |   整数 | >=0, 0表示无限循环 | 否 |

#### VoiceAction 定义

| 参数 | 说明  | 数据格式|可选值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| action      | 动作 |   字符串 | play, stop | 是 |
| volume      | 音量 |   整数 | 0-100 | 否 |
| audio_data      | 音频数据 |   字符串 | base64 编码的音频数据 | 否 |
| audio_format      | 音频格式 |   字符串 | 例如：mp3, wav | 否 |
| filename      | 音频文件名  |   字符串 | 例如：music.mp3 | 否 |
| wait_time      | 播放后等待时间(秒) |   整数 | >=0 | 否 |
| repeat      | 单个音频重复次数 |   整数 | >=0, 0表示无限循环 | 否 |


#### BGMAction 定义

| 参数 | 说明  | 数据格式|可选值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| action      | 动作 |   字符串 | play, stop | 是 |
| volume      | 音量 |   整数 | 0-100 | 否 |
| audio_data      | 音频数据 |   字符串 | base64 编码的音频数据 | 否 |
| audio_format      | 音频格式 |   字符串 | 例如：mp3, wav | 否 |
| filename      | 音频文件名	 |   字符串 | 例如：music.mp3	 | 否 |

#### DisplayAction 定义
| 参数 | 说明  | 数据格式|可选值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| action      | 动作 |   字符串 | play, stop | 是 |
| display_type      | 显示类型 |   字符串 | text, video | 是 |
| content      | 显示内容 |   字符串 | 文本内容 | 否 |
| style      | 显示样式 |   字符串 | normal, bold, blink | 否 |
| video_data      | 视频数据 |   字符串 | base64 编码的视频数据 | 否 |
| video_format      | 视频格式 |   字符串 | 例如：mp4, mov | 否 |
| filename      | 视频文件名 |   字符串 | 例如：sleep.mp4 | 否 |



### 响应示例

```
{
  "version": "1.0",
  "method": "execute-command",
  "conversation_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "message_id": "srv-20241031-103005-abcdef01-2345-6789-abcd-ef0123456789",
  "code": 0,
  "message": "success",
  "data": {
    "scene": "LIGHT_SLEEP",
    "scene_seq": 9, 
    "actions": {
      "fragrance": {
        "status": "on",
        "level": null,
        "count": 1
      },
      "light": {
        "mode": "Static",
        "rgb": "255, 147, 41"
      },
      "voice": {
        "voices": [
          {
            "action": "play",
            "volume": null,
            "audio_data": "<binary data removed>",
            "audio_format": "mp3",
            "filename": null,
            "wait_time": 1.5,
            "repeat": null,
            "text": "请找到一个不易被打扰的地方，选择一个让你感到舒适的姿势。"
          },
          {
            "action": "play",
            "volume": null,
            "audio_data": "<binary data removed>",
            "audio_format": "mp3",
            "filename": null,
            "wait_time": 1.5,
            "repeat": null,
            "text": "你可以选择倚靠着沙发或椅背。"
          },
          {
            "action": "play",
            "volume": null,
            "audio_data": "<binary data removed>",
            "audio_format": "mp3",
            "filename": null,
            "wait_time": 1.5,
            "repeat": null,
            "text": "接下的时间里，你将不再需要思索工作或者生活。请跟随我的动作，我将引导你获得内心的平静。"
          }
        ],
        "repeat": null
      },
      "bgm": {
        "action": "play",
        "volume": 50,
        "audio_data": null,
        "audio_format": null,
        "filename": "bo_asmr.mp3"
      },
      "display": null,
    }
  }
}
```


## 数据格式定义

```
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Generic, TypeVar

class RobotMethod(str, Enum):
    REPORT_STATE = "report-state"
    EXECUTE_COMMAND = "execute-command"

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

class ReportReqData(BaseModel):
    images: ImageDataPayload
    audio: Optional[AudioDataPayload] = None

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
    repeat: Optional[int] = None  # repeat times for single audio, 0 means infinite 
    text: Optional[str] = None  # text to speech

class VoiceSequence(BaseModel): 
    voices: list[VoiceAction]  # sequence of voice actions 
    repeat: Optional[int] = None  # repeat times for whole sequence, 0 means infinite     
    
class BgmAction(BaseModel):
    action: MediaAction
    volume: Optional[int] = None  # 0-100
    audio_data: Optional[str] = None  # base64 encoded
    audio_format: Optional[AudioFormat] = None
    filename: Optional[str] = None  # e.g., "night_rain.mp3"

class DisplayAction(BaseModel):
    display_type: DisplayType
    action: MediaAction
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
    action_feature: Optional[list] = None

class ActionRespData(BaseModel):
    scene: str  
    scene_seq: int
    actions: Actions
```