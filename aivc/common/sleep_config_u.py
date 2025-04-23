import json
from typing import Dict
from aivc.common.sleep_common import (
    StateType, Actions, VoiceSequence, VoiceAction,
)

states_dict: Dict[StateType, Actions] = {
    StateType.USING_PHONE: Actions(
        action_feature= "",
        voice=VoiceSequence(
            voices=[
                VoiceAction(
                    action="play",
                    text="请放下手中的事物，现在你不需要思考任何问题。",
                    filename="use_phone_01.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="如果需要接听重要的电话，我们可以先暂停一下。我会在这里等你。",
                    filename="use_phone_02.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="请将双手自然的垂放在身体两侧，现你不需控制身体做任何动作。",
                    filename="use_phone_03.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="当你闭上眼睛，才能听见心的声音。",
                    filename="use_phone_04.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="你知道吗？手机的蓝光会影响睡眠，还会增加雀斑的形成哦。",
                    filename="use_phone_05.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="亲爱的请放下手机，安心的睡个好觉吧。",
                    filename="use_phone_06.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="相信我，一次完整的冥想体验可比手机有趣多了。",
                    filename="use_phone_07.mp3"
                )               
            ]
        )
    ),

    StateType.SITTING_UP: Actions(
        action_feature= "",
        voice=VoiceSequence(
            voices=[
                VoiceAction(
                    action="play",
                    text="坐起身是想起有什么事情要做吗？不用着急，慢慢来。我在这里等你",
                    filename="sitting_up_01.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="坐姿会让腰部肌肉持续紧张，躺下才能更好的放松身体哦。",
                    filename="sitting_up_02.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="让我们专注当下，重新躺好，慢慢归位回到平和的状态。",
                    filename="sitting_up_03.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="冥想是一个探索的过程，在过程中你可以随时调整姿势，让自己保持在舒适的状态。等你重新躺下，我们再继续探索。",
                    filename="sitting_up_04.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="发生了什么让你感到坐卧不安呢？诉说也是很好的放松，我很愿意陪你聊聊天。不想说也没关系，你只需要静静平躺下来，让身体放松。",
                    filename="sitting_up_05.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="舒适的姿势能够更好的帮助我们放松身心。我会等待你重新平躺下来。",
                    filename="sitting_up_06.mp3"
                )
            ]
        )
    ),

    StateType.LEAVING: Actions(
        action_feature= "",
        voice=VoiceSequence(
            voices=[
                VoiceAction(
                    action="play",
                    text="是突然想起什么重要的事情吗？还需要我继续帮您助眠吗？",
                    filename="LEAVING_9b3345669ed649e825600e6531bd2408.mp3"
                )
            ]
        )
    )
}

if __name__ == "__main__":
    a: StateType = StateType.PREPARE
    print(f"{str(a)}, {a.name}")  # 使用f-string格式化
    serializable_dict = {state.order: action for state, action in states_dict.items()}
    # Save to JSON file
    with open('sleep_config.json', 'w', encoding='utf-8') as f:
        json.dump(serializable_dict, default=lambda x: x.__dict__, indent=2, ensure_ascii=False, fp=f)