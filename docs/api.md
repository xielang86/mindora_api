# 目录

- [接口地址](#接口地址)
- [语音聊天](#语音聊天)
  - [请求数据格式](#语音聊天请求数据格式)
    - [VCReqData结构](#vcreqdata结构) 
  - [响应数据格式](#语音聊天响应数据格式)
    - [VCRespData结构](#vcrespdata结构)
  - [数据格式定义](#数据格式定义)
  - [id生成](#id生成)
  - [时间戳生成](#时间戳生成)
- [文字到语音聊天接口](#文字到语音聊天接口)  
  - [请求数据格式](#文字聊天请求数据格式)
  - [响应数据格式](#文字聊天响应数据格式)
- [COMMAND接口](#command接口)
  - [请求数据格式](#command请求数据格式)
  - [命令列表](#命令列表)
  - [响应数据格式](#command响应数据格式)
- [心跳](#心跳)
  - [请求数据格式](#心跳请求数据格式)
  - [响应数据格式](#心跳响应数据格式)
- [状态上报接口](#状态上报接口)
  - [上行接口：报告状态 (report-state)](#上行接口报告状态-report-state)
    - [接口说明](#接口说明)
    - [数据结构说明](#数据结构说明)
  - [下行接口：执行指令 (execute-command)](#下行接口执行指令-execute-command)
    - [接口说明](#接口说明-1)
    - [数据结构说明](#数据结构说明-1)

# 接口地址

| 项目 | 说明  |
|:------------- |:---------------| 
| 协议      | websocket |   
| 地址      | ws://114.55.90.104:9001/ws |   

# 语音聊天

## 语音聊天请求数据格式

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------| 
| version      | 版本号 |   字符串| 1.0|是 | 
| method      | 请求方法 |  字符串 | voice-chat| 是 | 
| conversation_id      | 会话id，websocket建联时赋值，websocket重连时更换 |  字符串 | get_conversation_id()函数生成| 是 | 
| message_id      | 消息id，发送一次消息更新一次 |  字符串 | get_message_id()函数生成| 是 | 
| token      | 认证字段，待定 |  字符串 | 待定| 是 | 
| timestamp      | 时间戳 |  字符串 | get_rfc3339_with_timezone()函数生成| 是 | 
| data      | 数据 |  VCReqData数据结构 | 见VCReqData定义| 是 | 

####  VCReqData结构
| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------| 
| content_type      | 数据格式 |   字符串|audio\|image\|text |是 | 
| content      | 数据 |   字符串|audio或image采用base64编码,text明码 |是 | 
| tts_audio_format      | 数据 |   字符串|pcm / ogg_opus / mp3，默认为 pcm |否 | 

#### 请求示例
```
{
  "version": "1.0",
  "method": "voice-chat",
  "conversation_id": "04025a30-2ec4-44cb-918b-d7e7298563f5",
  "message_id": "20241031-013946-4611e877-c5de-4773-91bd-b57e459a0e4b",
  "token": "20241031-013946-f674310c-0c7f-440e-901a-075c6c28b552",
  "timestamp": "2024-10-31T09:49:09.761387+08:00",
  "data": {
    "content_type": "audio",
    "content": "JQIkA4MBxv+p/xT/Sv3U/Ir/yQLtBOgDqv9O/Hz7oP0QAZAC9gKeAngAXf5o/Fr9NgGlA/kCOADx/Tb+P/96/7b/OgFdAzUCwv1Z+iv7jADABaYFfwFH/E36T/wj/2EBRQM0BMwCm/4C+xv7JP4OAWwDPQRXAg==",
    "tts_audio_format":"ogg_opus"
  }
}
```

## 响应数据格式

**注：单次请求一般是有多个返回，收到后按序播放即可**

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------| 
| version      | 版本号 |   字符串| 1.0|是 | 
| method      | 请求方法 |  字符串 | voice-chat| 是 | 
| conversation_id      | 会话id |  字符串 | 回传请求字段| 是 | 
| message_id      | 消息id |  字符串 | 回传请求字段| 是 | 
| code      | 返回码，0表示成功，其他表示失败 |  字符串 | 0| 是 | 
| message      | 返回成功或者错误消息 |  字符串 | success| 是 | 
| data      | 数据 |  VCRespData数据结构 | 见VCRespData定义| 是 | 

#### VCRespData结构
| 参数 | 说明  | 数据格式|值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------| 
| action      | 行动指令 |   字符串| take_photo|否 | 
| text      | 文字内容 |   字符串| |否 | 
| audio_data      | 音频数据 |   字符串|base64编码 |否 | 
| audio_format      | 数据格式 |   字符串|pcm或mp3 |否 | 
| sample_rate      | 采样率 |   int|16000 |否 | 
| channels      | 声道 |   int|1 |否 | 
| sample_format      | 格式 |   字符串|S16LE |否 | 
| bitrate      | 码率 |   int|256000 |否 | 
| stream_seq      | 流顺序号，-1表示流已经结束 |   int|0 |是 | 

#### 响应示例
```
{
  "version": "1.0",
  "method": "voice-chat",
  "conversation_id": "04025a30-2ec4-44cb-918b-d7e7298563f5",
  "message_id": "20241031-013946-4611e877-c5de-4773-91bd-b57e459a0e4b",
  "code": 0,
  "message": "success",
  "data": {
    "action": "take_photo",
    "text": "好的，我看一下",
    "sample_rate": 16000,
    "channels": 1,
    "sample_format": "S16LE",
    "bitrate": 256000,
    "audio_data": "AAAAAAAP//AAD8////9//1/ywAMQAPAAwA+v/9/xUACAABAPf/8f/z//b/",
    "audio_format": "pcm",
    "stream_seq":1
  }
}
```

#### 数据格式定义
```
class VCMethod(str, Enum):
    VOICE_CHAT = "voice-chat"
    TEXT_CHAT = "text-chat"
    TEXT_TO_SPEECH = "text-to-speech"
    PING = "ping"

class ContentType(str, Enum):
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"

class VCReqData(BaseModel):
    content_type: Optional[str] = ContentType.AUDIO.value  # audio|image|text
    content: Optional[str] = "" # audio|image base64 encoded data | 明码文字
    tts_audio_format: Optional[str] = "pcm" # pcm|ogg_opus|mp3

DataT = TypeVar("DataT")

class Req(BaseModel, Generic[DataT]):
    version: str = "1.0"
    method: VCMethod 
    conversation_id: str
    message_id: str
    token: Optional[str] = ""
    timestamp: Optional[str] = ""
    data: Optional[DataT] = None

class VCRespData(BaseModel):
    action: Optional[str] = None
    text: Optional[str] = ""
    audio_filename: Optional[str] = None
    audio_format: Optional[str] = "pcm"
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    sample_format: Optional[str] = None
    bitrate: Optional[int] = None
    audio_data: Optional[str] = None
    stream_seq: int = 0

class Resp(BaseModel, Generic[DataT]):
    version: Optional[str] = ""
    method: Optional[VCMethod] = ""
    conversation_id: Optional[str] = ""
    message_id: Optional[str] = ""
    code: int = 0
    message: str = "success"
    data: Optional[DataT] = None

```

#### id生成
```
import uuid
from datetime import datetime

def get_id() -> str:
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')[:-3]
    return f"{timestamp}-{uuid.uuid4().hex}"

def get_conversation_id() -> str:
    return uuid.uuid4().hex

def get_message_id() -> str:
    return get_id()
```

#### 时间戳生成
```
from datetime import datetime
import pytz
def get_rfc3339_with_timezone():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz).isoformat()
```


# 文字到语音聊天接口

## 文字聊天请求数据格式

请求数据格式与[语音聊天请求数据格式](#语音聊天请求数据格式)相同，主要区别如下：

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------| 
| data.content_type      | 数据格式 |   字符串| text |是 | 
| data.content      | 数据 |   字符串| 明码文字 |是 | 

#### 请求示例
```
{
  "version": "1.0",
  "method": "text-to-speech",
  "conversation_id": "04025a30-2ec4-44cb-918b-d7e7298563f5",
  "message_id": "20241031-013946-4611e877-c5de-4773-91bd-b57e459a0e4b",
  "token": "20241031-013946-f674310c-0c7f-440e-901a-075c6c28b552",
  "timestamp": "2024-10-31T09:49:09.761387+08:00",
  "data": {
    "content_type": "text",
    "content": "你好",
  }
}
```

## 响应数据格式

响应数据格式与[语音聊天响应数据格式](#语音聊天响应数据格式)完全相同

#### 响应示例
```
{
  "version": "1.0",
  "method": "voice-chat",
  "conversation_id": "04025a30-2ec4-44cb-918b-d7e7298563f5",
  "message_id": "20241031-013946-4611e877-c5de-4773-91bd-b57e459a0e4b",
  "code": 0,
  "message": "success",
  "data": {
    "text": "xxx",
    "sample_rate": 16000,
    "channels": 1,
    "sample_format": "S16LE",
    "bitrate": 256000,
    "audio_data": "AAAAAAAP//AAD8////9//1/ywAMQAPAAwA+v/9/xUACAABAPf/8f/z//b/",
    "audio_format": "ogg_opus",
    "stream_seq": 1
  }
}
```

# COMMAND接口

## COMMAND请求数据格式 

请求数据格式与[语音聊天请求数据格式](#语音聊天请求数据格式)相同，主要区别如下：

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------| 
| method      | 请求方法 |  字符串 | commond| 是 | 
| data.content_type      | 数据格式 |   字符串| text |否 | 
| data.content      | [具体命令](#命令列表)   |   字符串| 无 |是 | 

## 命令列表

| Command                                             | 功能                                              |
|----------------------------------------------------------|----------------------------------------------------------|
| meditation.mindfulness.breathing_exercises.natural | 冥想 > 正念冥想 > 呼吸练习 > 自然呼吸 |
| meditation.mindfulness.breathing_exercises.abdominal | 冥想 > 正念冥想 > 呼吸练习 > 腹式呼吸 |
| meditation.mindfulness.breathing_exercises.box | 冥想 > 正念冥想 > 呼吸练习 > 箱式呼吸法 |
| meditation.mindfulness.breathing_exercises.ocean | 冥想 > 正念冥想 > 呼吸练习 > 海洋呼吸法 |
| meditation.mindfulness.breathing_exercises.4_7_8 | 冥想 > 正念冥想 > 呼吸练习 > 4-7-8呼吸法 |
| meditation.mindfulness.scanning.full_body | 冥想 > 正念冥想 > 扫描 > 经典全身扫描(呼吸扫描) |
| meditation.mindfulness.scanning.pain_relief | 冥想 > 正念冥想 > 扫描 > 缓解疼痛(身体疗愈) |
| meditation.mindfulness.scanning.localized_relaxation | 冥想 > 正念冥想 > 扫描 > 快速局部放松 |
| meditation.mindfulness.scanning.energy_ball | 冥想 > 正念冥想 > 扫描 > 能量球扫描(解压咒语) |
| meditation.mindfulness.awareness.five_senses | 冥想 > 正念冥想 > 觉察 > 五感grounding |
| meditation.mindfulness.awareness.sitting | 冥想 > 正念冥想 > 觉察 > 静坐冥想 |
| meditation.mindfulness.awareness.sound | 冥想 > 正念冥想 > 觉察 > 声音觉察 |
| meditation.mindfulness.imagination.safe_place | 冥想 > 正念冥想 > 想象 > 安全岛构建 |
| meditation.mindfulness.imagination.light_bath | 冥想 > 正念冥想 > 想象 > 光明沐浴 |
| meditation.mindfulness.imagination.thoughts_as_clouds | 冥想 > 正念冥想 > 想象 > 念头云观察 |
| meditation.mindfulness.emotions.labeling | 冥想 > 正念冥想 > 情绪 > 情绪标记法 |
| meditation.mindfulness.emotions.rain_recognition | 冥想 > 正念冥想 > 情绪 > RAIN冥想(认可) |
| meditation.mindfulness.emotions.gratitude | 冥想 > 正念冥想 > 情绪 > 慈心冥想(感恩) |
| meditation.mindfulness.emotions.scan | 冥想 > 正念冥想 > 情绪 > 情绪扫描 |
| meditation.mindfulness.emotions.overcoming_fear | 冥想 > 正念冥想 > 情绪 > 克服恐惧 |
| sleep.yoga_nidra.deep_sleep | 助眠>Yoga Nidra>快速深睡 |
| sleep.yoga_nidra.peaceful_sleep | 助眠>Yoga Nidra>安心入睡 |
| sleep.yoga_nidra.warm_slumber | 助眠>Yoga Nidra>温暖入眠 |
| sleep.yoga_nidra.mind_body_cleanse | 助眠>Yoga Nidra>净化身心 |
| sleep.yoga_nidra.moonlight_power | 助眠>Yoga Nidra>月光赋能 |
| sleep.yoga_nidra.dream_wish | 助眠>Yoga Nidra>环梦祈愿 |
| sleep.training.stress_release | 助眠>睡眠训练>卸下压力 |
| sleep.training.unwind | 助眠>睡眠训练>告别忙碌 |
| sleep.training.clear_mind | 助眠>睡眠训练>清空大脑 |
| sleep.training.soothe_tension | 助眠>睡眠训练>舒缓紧绷 |
| sleep.training.inner_peace | 助眠>睡眠训练>回归内在 |
| sleep.training.whole_self | 助眠>睡眠训练>完整的你 |
| sleep.training.self_care | 助眠>睡眠训练>自我滋养 |
| sleep.dreamscapes.voyager_1 | 助眠>梦境漫游>旅行者一号 |
| sleep.dreamscapes.beach | 助眠>梦境漫游>海滩 |
| sleep.dreamscapes.wheat_field | 助眠>梦境漫游>麦田 |
| sleep.dreamscapes.fireplace | 助眠>梦境漫游>炉火 |
| sleep.dreamscapes.courtyard | 助眠>梦境漫游>庭院 |
| sleep.dreamscapes.counting_sheep | 助眠>梦境漫游>牧羊 |
| sleep.recovery.insomnia | 助眠>睡眠修复>失眠 |
| sleep.recovery.after_nightmare | 助眠>睡眠修复>噩梦惊醒 |
| sleep.recovery.back_to_sleep | 助眠>睡眠修复>再次入睡 |
| sleep.natural.nap | 助眠>自然安眠>小憩 |
| sleep.natural.mind_unwind | 助眠>自然安眠>睡前释放思绪 |
| sleep.natural.sweet_dreams | 助眠>自然安眠>美好入睡 |

#### 请求示例
```
{
  "version": "1.0",
  "method": "commond",
  "conversation_id": "04025a30-2ec4-44cb-918b-d7e7298563f5",
  "message_id": "20241031-013946-4611e877-c5de-4773-91bd-b57e459a0e4b",
  "token": "20241031-013946-f674310c-0c7f-440e-901a-075c6c28b552",
  "timestamp": "2024-10-31T09:49:09.761387+08:00",
  "data": {
    "content_type": "text",
    "content": "meditation.mindfulness.breathing_exercises.natural",  # 冥想 > 正念冥想 > 呼吸练习 > 自然呼吸
  }
}
```

## 响应数据格式

响应数据格式与[语音聊天响应数据格式](#语音聊天响应数据格式)完全相同

#### 响应示例
```
{
  "version": "1.0",
  "method": "commond",
  "conversation_id": "04025a30-2ec4-44cb-918b-d7e7298563f5",
  "message_id": "20241031-013946-4611e877-c5de-4773-91bd-b57e459a0e4b",
  "code": 0,
  "message": "success",
  "data": {
    "text": "xxx",
    "sample_rate": 16000,
    "channels": 1,
    "sample_format": "S16LE",
    "bitrate": 256000,
    "audio_data": "AAAAAAAP//AAD8////9//1/ywAMQAPAAwA+v/9/xUACAABAPf/8f/z//b/",
    "audio_format": "ogg_opus",
    "stream_seq": 1
  }
}
```


# 心跳

## 心跳请求数据格式

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------| 
| version      | 版本号 |   字符串| 1.0|是 | 
| method      | 请求方法 |  字符串 | ping| 是 | 

#### 请求示例
```
{
  "version": "1.0",
  "method": "ping"
}
```

### 响应数据格式
| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------| 
| version      | 版本号 |   字符串| 1.0|是 | 
| method      | 请求方法 |  字符串 | pong| 是 | 

#### 响应示例
```
{
  "version": "1.0",
  "method": "pong"
}
```



# 状态上报接口

## 上行接口：报告状态 (`report-state`)

### 接口说明

机器人每隔 2 秒通过此接口向服务端报告当前感知到的环境信息（前提是检测到人脸），包括抓拍的图片和录制的音频数据。

### 请求方法

`report-state`

### 数据发送频率

每 2 秒一次

### 数据格式

JSON

### 请求数据格式

基础数据结构请参考[语音聊天请求数据格式](#请求数据格式)。主要区别如下：

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| method      | 请求方法 |  字符串 | report-state| 是 |
| data      | 数据 |  PerceptionReqData 数据结构 | 见下方定义 | 是 |

#### PerceptionReqData 结构

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| images      | 图片数据 | ImageDataPayload 结构 |  | 是 |
| audio      | 音频数据 | AudioDataPayload 结构 |  | 否 |
| scene_exec_status      | 执行状态 | SceneExecStatus 结构 |  | 否 |

#### SceneExecStatus 结构

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| command      | 命令 |   string  | 无 | 是 |
| scene      | 场景名 |   int  | 无 | 是 |
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


## 下行接口：执行指令 (`execute-command`)

### 接口说明

服务端通过此接口向机器人发送指令，包括当前场景信息以及需要机器人执行的硬件动作。

### 方法

`execute-command`

### 数据接收频率

实时，根据服务端分析结果推送

### 数据格式

JSON

### 响应数据格式

基础数据结构请参考[语音聊天响应数据格式](#响应数据格式)。主要区别如下：

| 参数 | 说明  | 数据格式|缺省值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| method      | 请求方法 |  字符串 | execute-command| 是 |
| data      | 数据 |  ActionRespData 数据结构 | 见 ActionRespData 定义 | 是 |

#### ActionRespData 结构

| 参数 | 说明  | 数据格式|值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| cmd      | 当前命令 |   字符串| 见command格式 |是 |
| scene      | 当前场景 |   字符串| 例如：Awake、LightSleep、DeepSleep |是 |
| actions      | 硬件动作指令 |   Actions 对象 | 见 Actions 定义 |是 |

#### Actions 定义

| 参数 | 说明  | 数据格式|可选值|是否必填|
|:------------- |:---------------| :---------------|  :---------------| :---------------|
| fragrance      | 香氛控制 |   FragranceAction 对象 |  [FragranceAction 定义](#fragranceaction-定义) | 否 |
| light      | 灯光控制 |   LightAction 对象 |  [LightAction 定义](#lightaction-定义) | 否 |
| voice      | 人声控制 |   VoiceSequence 对象 |  [VoiceSequence 定义](#voicesequence-定义) | 否 |
| bgm      | 背景音乐 |   BGMAction 对象 |  [BGMAction 定义](#bgmaction-定义) | 否 |
| display      | 屏幕显示	 |   DisplayAction 对象 |  [DisplayAction 定义](#displayaction-定义) | 否 |
| skip_photo_capture| 是否跳过拍照	 |   bool | 为True时不拍照 | 否 |
| action_feature| 说明字段	 |   字符串 | 附加说明信息 | 否 |


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
    action_feature: Optional[str] = None
    skip_photo_capture: Optional[bool] = False

class ActionRespData(BaseModel):
    cmd: str
    scene: str  
    scene_seq: Optional[int] = None
    actions: Actions
```