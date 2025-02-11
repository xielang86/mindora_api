import json
from typing import Dict
from aivc.common.sleep_common import (
    StateType, Actions, VoiceSequence, VoiceAction,
    BgmAction, MediaAction, LightAction, LightMode,
    FragranceAction, FragranceStatus
)

states_dict: Dict[StateType, Actions] = {
    StateType.PREPARE: Actions(
        action_feature="(半躺 || 躺姿 ) AND 存在 AND !(手持)",
        voice=VoiceSequence(
            voices=[
                VoiceAction(
                    action="play",
                    text="请找到一个不易被打扰的地方，选择一个让你感到舒适的姿势。",
                    wait_time=1.5,
                    filename="PREPARE_0e4469908950edf80d00d50388e22b72.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="你可以选择倚靠着沙发或椅背。",
                    wait_time=1.5,
                    filename="PREPARE_fb554feefb09a53a8bb55c6320e7cdb1.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="接下的时间里，你将不再需要思索工作或者生活。",
                    wait_time=1.5,
                    filename="PREPARE_b28c329834ff637ff3a73c5e01bd7d52.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="请跟随我的动作，我将引导你获得内心的平静",
                    wait_time=1.5,
                    filename="PREPARE_2e60034d42489d4b7b411366b9295356.mp3"
                )
            ]
        ),
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="bo_asmr.mp3",
            volume=50
        ),
        light=LightAction(
            mode=LightMode.STATIC,
            rgb="255, 147, 41"
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.ON,
            count=1
        )
    ),
    
    StateType.POSTURE: Actions(
        action_feature="(半躺 || 躺姿 ) AND 存在 AND !(手持)",
        voice=VoiceSequence(
            voices=[
                VoiceAction(
                    action="play",
                    text="现在，请将你的肩膀慢慢放松。",
                    wait_time=2,
                    filename="POSTURE_b929bab873c406f9fcecc3abdd324ec1.mp3"
                ),
                VoiceAction(
                    action="play", 
                    text="双手自然的垂下，掌心向上，放在大腿的前侧。",
                    wait_time=2,
                    filename="POSTURE_c08908db7c842e01fbd8f965dfa85d89.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="然后轻轻的闭上双眼，感受周围的变化",
                    wait_time=2,
                    filename="POSTURE_06d311023745d1a866490c0d0ce42f44.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="体验臀部与座椅的接触，双脚与地面的接触",
                    wait_time=2,
                    filename="POSTURE_080ed47b54f21a0b6709de6484d1dc1e.mp3"
                ),
                VoiceAction(
                    action="play", 
                    text="此刻你的身体正被椅子和下方的大地稳稳的承托着",
                    wait_time=2,
                    filename="POSTURE_e444af1a781082ba399ff9eaebb507eb.mp3"
                )
            ]
        ),
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="bo_1036.mp3", 
            volume=45
        ),
        light=LightAction(
            mode=LightMode.STATIC,
            rgb="255, 147, 41"
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.ON,
            count=1
        )
    ),
    
    StateType.BREATHING: Actions(
        action_feature="(半躺 || 躺姿 ) AND 存在 AND !(手持)",
        voice=VoiceSequence(
           voices=[
                VoiceAction(
                    action="play",
                    text="现在，让我们做几组深呼吸。用鼻子深深吸气",
                    wait_time=3,
                    filename="BREATHING_a291d037d81ddc94e0fc33bcf729dea9.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="用嘴巴缓缓呼气",
                    wait_time=3,
                    filename="BREATHING_4dc3129193b03d217cddf651ba366fe6.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="深深的吸气",
                    wait_time=3,
                    filename="BREATHING_a7c0c188a373ea0a69c1f46f17eaeb31.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="缓缓的呼气",
                    wait_time=3,
                    filename="BREATHING_36c798c145115acc2b01ca8339fa4981.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="继续保持深呼吸",
                    wait_time=3,
                    filename="BREATHING_9685385b968f6512da7ee169fe861b9c.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="用鼻子吸气",
                    wait_time=3,
                    filename="BREATHING_7663c2e11fd2cc1179d6850a99db75aa.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="用嘴巴呼气。",
                    wait_time=3,
                    filename="BREATHING_d460b7c6cb07b406dcdbde371afca1bc.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="感觉呼吸渐渐慢下来，变得越来越深长",
                    wait_time=8,
                    filename="BREATHING_bb6957ab273cbdf11a4aae3244e3f5cc.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="感觉身体的每一寸肌肉正随着每一次的呼吸，慢慢的放松下来。",
                    wait_time=8,
                    filename="BREATHING_7941fd6f49d176f0dd2ee7bb0a93afcd.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="你做的很好",
                    wait_time=3,
                    filename="BREATHING_bd7ce9ce5e10201cdfe0b9bd4f634a5e.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="现在让我们将呼吸，调节成我们日常呼吸的节奏",
                    wait_time=3,
                    filename="BREATHING_b361ddc8c2ca77b5493c7469c6e9b3d6.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="用鼻子吸气。",
                    wait_time=3,
                    filename="BREATHING_9dce53484234ed669c45bcd4edb04d22.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="用鼻子呼气。",
                    wait_time=3,
                    filename="BREATHING_5049ad4ccc4a737f2361b13a47090613.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="吸气时",
                    wait_time=6,
                    filename="BREATHING_6e8fe98a2b2102f12ced5ea46aea85af.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="感觉气流经过鼻腔、喉咙、胸腔，一直到腹部。",
                    wait_time=6,
                    filename="BREATHING_e55fb3e213cba1408e0ef40c547ae640.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="呼气时，感受气流从嘴巴缓缓呼出的过程。",
                    wait_time=6,
                    filename="BREATHING_4cb6818bd595b5516cc6e7b4757809cd.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="此刻你只需要将自己的注意力放在呼吸上。",
                    wait_time=6,
                    filename="BREATHING_b270ed55b5b4dc2123ec0797ef450cb5.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="感觉你的思绪随着每一次又深又长的呼吸，一点点的释放出去。",
                    wait_time=6,
                    filename="BREATHING_91003bd2e4ec5844b6c9f5d1c5da573f.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="用鼻子均匀的呼吸，让鼻子将空气带到你的胸部，去感受，胸部是如何收缩和扩张的。",
                    wait_time=6,
                    filename="BREATHING_7585a88baebd17e29d5c36a74a2f2bd8.mp3"
                ),
            ]
        ),
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="bo_1036.mp3",  
            volume=45
        ),
        light=LightAction(
            mode=LightMode.GRADIENT,
            rgb="255, 147, 41"
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.ON,
            level=5,  # 假设每2分钟喷一次对应level=5
        )
    ),
    
    StateType.RELAX_1: Actions(
        action_feature="(半躺 || 躺姿 ) AND 存在 AND !(手持)",
        voice=VoiceSequence(
        voices=[
                VoiceAction(
                    action="play",
                    text="现在，继续将注意力，带到腹部",
                    wait_time=8,
                    filename="RELAX_1_f493e41a829211386884d7e1ae27abdf.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="仔细的体会一下，你的腹部是怎样跟随着呼吸上下起伏的。",
                    wait_time=8,
                    filename="RELAX_1_1c8f90b4f914a54f9e8b0ce67fc0952b.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="你可以将一只手，轻轻的放在腹部，让手跟随着腹部一起上下起伏。",
                    wait_time=8,
                    filename="RELAX_1_274cce17599bfbe6d9a887aa46cbe2b8.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="接下来的时间",
                    wait_time=4,
                    filename="RELAX_1_c49ec684c3c07d6a15f0f234bb0b0251.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="将注意力持续的保持在这个部位，仔细的体会，呼吸给身体带来的感觉。",
                    wait_time=4,
                    filename="RELAX_1_225bebee5a4a2dfa4ed8cb756f13f99e.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="感觉自己就像是一杯，被摇晃过的水，正随着呼吸一点点的平静摇晃，一点点的平静下来。",
                    wait_time=8,
                    filename="RELAX_1_55e1498701aa227d2fd8d5ac46ef5d2d.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="在这个过程中",
                    wait_time=4,
                    filename="RELAX_1_ad1e671152487bb40daede8cc38eaf9a.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="或许杂乱的思绪仍然会不时浮现出来",
                    wait_time=4,
                    filename="RELAX_1_11e6a3fa3caa2c265564202c09a2164f.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="给你带来干扰，让注意力从身体上悄然游走",
                    wait_time=4,
                    filename="RELAX_1_0e56b97ebb717c43c9edbbd4a876742e.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="没关系。这是非常自然的现象。",
                    wait_time=8,
                    filename="RELAX_1_3b2a13dc2c6f2ecbf02a52b8adaf1908.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="你只需要在发现注意力出现游走的时候，重新将注意力，带回到腹部，感受呼吸给腹部带来的起伏就好。",
                    wait_time=8,
                    filename="RELAX_1_1230b134033f975c74a4c63d45ea6d12.mp3"
                ),
            ]
        ),
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="bo_1036.mp3",
            volume=35
        ),
        light=LightAction(
            mode=LightMode.GRADIENT,
            rgb="255, 147, 41"
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.ON,
            count=1
        )
    ),
    
    StateType.RELAX_2: Actions(
        action_feature="(半躺 || 躺姿 ) AND 存在 AND !(手持)",
        voice=VoiceSequence(
            voices=[
                VoiceAction(
                    action="play",
                    text="很好，就像这样，你可以将手放回大腿上，继续保持舒缓的呼吸。",
                    wait_time=8,
                    filename="RELAX_2_06728bad68a989b8f735dac2b86102c0.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="让我们慢慢的将意识带回到当下所处的空间。",
                    wait_time=8,
                    filename="RELAX_2_02971319602ea73cb3309270c2ca5be3.mp3"
                ),
            ]
        ),
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="hailang_776.mp3",
            volume=25
        ),
        light=LightAction(
            mode=LightMode.GRADIENT,
            rgb="255, 147, 41"
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.ON,
            count=1
        )
    ),    
    StateType.SLEEP_READY: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(
                    action="play",
                    text="现在，如果你感到放松，甚至已经感觉到困倦，我们可以选择平躺下来",
                    wait_time=8,
                    filename="SLEEP_READY_af5dbd5a079133dd483b998db2ea2c73.mp3"
                ),
                VoiceAction(
                    action="play",
                    text="就在这样安心的，放松的，进入到睡梦中去吧。",
                    wait_time=8,
                    filename="SLEEP_READY_88a2a7c12cb7637af4df21ff704ee849.mp3"
                )
            ]
        ),
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="hailang_776.mp3",
            volume=25
        ),
        light=LightAction(
            mode=LightMode.GRADIENT,
            rgb="255, 147, 41"
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.ON,
            count=1
        )
    ),
    
    StateType.LIGHT_SLEEP: Actions(
        action_feature="",
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="hailang_776.mp3",
            volume=20
        ),
        light=LightAction(
            mode=LightMode.GRADIENT,
            rgb="255, 147, 41"
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.ON,
            count=1
        )
    ),
    
    StateType.DEEP_SLEEP: Actions(
        action_feature="",
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="hailang_776.mp3",
            volume=20
        ),
        light=LightAction(
            mode=LightMode.GRADIENT,
            rgb="255, 147, 41"
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.OFF
        )
    ),
    
    StateType.STOP: Actions(
        bgm=BgmAction(
            action=MediaAction.STOP
        ),
        light=LightAction(
            mode=LightMode.OFF
        ),
        fragrance=FragranceAction(
            status=FragranceStatus.OFF
        )
    ),

    StateType.USING_PHONE: Actions(
        action_feature= "",
        voice=VoiceSequence(
            voices=[
                VoiceAction(
                    action="play",
                    text="请放下手中的事物，让我们继续关注到当下的感受中",
                    filename="USING_PHONE_5c1692d9968a8340c6156cc36537ab47.mp3"
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
                    text="怎么坐起来了呢？让我们调整一个舒适的姿势重新躺下吧",
                    filename="SITTING_UP_90ea96bb8643a72940f0b8e4c334fa02.mp3"
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