### 更新异常告警机制
1. 日期 2025-04-18
2. [需求文档](https://xcn4jug5893p.feishu.cn/docx/LPaRdb5kfoJs7SxRh2ScPPZAnN1)
3. 更新功能
    - sop流程中准备阶段不做姿势是识别，Actions增加字段skip_photo_capture，当skip_photo_capture为True时不拍照

    ```Python
    class Actions(BaseModel):
        fragrance: Optional[FragranceAction] = None
        light: Optional[LightAction] = None
        voice: Optional[VoiceSequence] = None
        bgm: Optional[BgmAction] = None
        display: Optional[DisplayAction] = None
        action_feature: Optional[str] = None
        skip_photo_capture: Optional[bool] = False
    ```
    - 告警事件
    ```Python
    1. 播放动作增加淡出FADE_OUT
    class MediaAction(str, Enum):
        PLAY = "play"
        STOP = "stop"
        FADE_OUT = "fade_out"
    2. volume可以为负值，表示音量降低多少
    ```




