import json
from typing import Dict
from aivc.sop.mindfulness.mf1.common import Mindfulness1StateType
from aivc.sop.common.common import (
    Actions, VoiceSequence, VoiceAction,BgmAction, MediaAction
)


states_dict: Dict[Mindfulness1StateType, Actions] = {
    Mindfulness1StateType.PREPARE: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="欢迎来到潮汐,我很荣幸能够引导你,开始为期7天的,正念入门之旅", wait_time=2, filename="fe1e55f5ea883aa1fc7ed2fb499a2eb8.mp3"),
                VoiceAction(action="play", text="正念是一套规则,能够帮助我们,接触心智的本质,激发生命潜力", wait_time=2, filename="669f4df6c6992cb86e1ca91abc4d6d4b.mp3"),
                VoiceAction(action="play", text="本系列的设计目的,就是帮你打开这道正面之门", wait_time=2, filename="13d3f3703a07a20c40dc7bce527a85a1.mp3"),
                VoiceAction(action="play", text="我将要带给你最基础,也最经典的方法观呼吸", wait_time=2, filename="037986d9ab8bb961c266c884af22edfa.mp3"),
                VoiceAction(action="play", text="顾名思义,观呼吸指的是在静坐练习中,把注意力安放在呼吸上,一旦走神了,就用呼吸作为绳子,再把他拉回当下", wait_time=2, filename="b64b5d89f77a189dc1adcadb70c4bf63.mp3"),
                VoiceAction(action="play", text="这听上去似乎很简单,但是一旦开始练习,就会有各种各样的问题冒出来", wait_time=2, filename="39b4d1e085cb46ea86513fb000504484.mp3"),
                VoiceAction(action="play", text="比如,有的人很快会感到不耐烦", wait_time=2, filename="2b027dde07ee568d939bcefdd61e0a2c.mp3"),
                VoiceAction(action="play", text="有的人,总是觉得自己做的不够好,感到自责或者生气", wait_time=2, filename="0a53ce179c2b5399ee3eba5c5f2195d9.mp3"),
                VoiceAction(action="play", text="你我性格上的弱点,或者说隐藏面,都会在静坐过程中,被不断揭露出来", wait_time=2, filename="454eab853634492a9ce93dda4efb6126.mp3"),
                VoiceAction(action="play", text="这可能会吓你一跳,也可能是醍醐灌顶", wait_time=2, filename="22144aed774ee4b8bc44bc850bba283d.mp3"),
                VoiceAction(action="play", text="因为,这也许是你人生中第一次，允许自己,看到心智的真正面貌，并试着学习不去评判他", wait_time=2, filename="aacb808e26d6e30d204e3df62280d266.mp3"),
                VoiceAction(action="play", text="在冥想的初期,我们处理的,就是这些新的基本问题", wait_time=2, filename="0b94d6a771e5b4e9923932131693caf6.mp3"),
                VoiceAction(action="play", text="与自己形象的投射,以念头和情绪的关系", wait_time=2, filename="a83ad4c136d06646a02502be96e1ab7c.mp3"),
                VoiceAction(action="play", text="因此让我们耐心一点,在7节课中循序渐进", wait_time=2, filename="89eea38db262e467ce19aa3dfd1a1386.mp3"),
                VoiceAction(action="play", text="第一天，我会带你找到适合自己的坐姿", wait_time=2, filename="c7533fd4229330bcc9ed312e6cfbc99d.mp3"),
                VoiceAction(action="play", text="第二天，我们会正式学习,将注意力维持在呼吸上，并在接下来的每节课,从不同的角度,去观察自己的认知模式,提高注意力", wait_time=2, filename="a009707a1a9efb6abe1f0460d1053241.mp3"),
                VoiceAction(action="play", text="一开始的冥想时间,也许只有5分钟,而且我还会说很多话", wait_time=2, filename="dbe4b53ac874560d17b222ca2618550a.mp3"),
                VoiceAction(action="play", text="逐渐当你掌握规则后,我会给你越来越多自我觉察的空间", wait_time=2, filename="3aebb4717303767e182ebabe39a1316e.mp3"),
                VoiceAction(action="play", text="这将是一段有趣的,也许改变你人生的旅程", wait_time=2, filename="a3acd781cd26b39dc00c99f54165d1fc.mp3"),
                VoiceAction(action="play", text="而你所需要做的,仅仅是,找到一个不被打扰的地方,闭上眼睛,然后让内心一点点打开", wait_time=2, filename="cad2bc2cb08c64e84579f36ba1ad8254.mp3"),
                VoiceAction(action="play", text="我在第一天的课程中等你", wait_time=2, filename="4f7190f33b809e5d0c64dba6ea2f840b.mp3")
            ]
        ),        
        bgm=BgmAction(
            action=MediaAction.PLAY,
            filename="冥想.mp3",
            volume=50
        ),
    ),
    
    Mindfulness1StateType.MEDITATION_1: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="今天我们的任务非常简单", wait_time=1.8, filename="7800fe7c99760577bbc4cdab9b1328fe.mp3"),
                VoiceAction(action="play", text="就是找到适合你的静坐姿势,然后和自己安静的独处一会儿", wait_time=1.8, filename="617bf5896371e35138fb9e7f7c4bccdc.mp3"),
                VoiceAction(action="play", text="你可以选择简易的盘腿坐姿,或者坐在一把舒适的椅子上", wait_time=1.8, filename="552855753ec74ccb912f8de8d2a1fbe5.mp3"),
                VoiceAction(action="play", text="对于初学者来说,让身体能够坐直是最重要的，你可以做出自己的选择", wait_time=1.8, filename="aee41a76667fbc45399e44dcc4b91829.mp3"),
                VoiceAction(action="play", text="如果你是坐在椅子上的,那么请检查你的双脚,能否扎实的踩在地面", wait_time=1.8, filename="bf4c391dc86f6b985aa0cb7224689b55.mp3"),
                VoiceAction(action="play", text="让腹部微微的内收,稍微用上一点力气,因为当我们收腹时,身体自然会做的挺拔一些", wait_time=1.8, filename="06a6363e2a2fe714e466d2265708560d.mp3"),
                VoiceAction(action="play", text="请将掌心向上,安放在膝头或大腿前侧", wait_time=1.8, filename="2148947bd6507a7af2d477146d9754c4.mp3"),
                VoiceAction(action="play", text="让双臂自然下垂", wait_time=1.8, filename="5a36115ce79d24ac6f6b277b3cb6ac8e.mp3"),
                VoiceAction(action="play", text="想象你的手肘,变得微微沉重一点", wait_time=1.8, filename="2e0d283999b2f358438732a1fec94b7d.mp3"),
                VoiceAction(action="play", text="放松肩膀", wait_time=1.8, filename="d907f68ab46dfc2d7f31def76c38d322.mp3"),
                VoiceAction(action="play", text="让下颌微收", wait_time=1.8, filename="e69d1950a7d8dd61d3463e34037abfcb.mp3"),
                VoiceAction(action="play", text="当你准备好以后,可以轻轻的闭上双眼", wait_time=1.8, filename="bb037e491717c7fba06febc79d82caf5.mp3"),
                VoiceAction(action="play", text="让我们一起,先来做3个深呼吸", wait_time=1.8, filename="e446b80a8fc02d6da72a3dbef87fc8c1.mp3"),
                VoiceAction(action="play", text="深呼吸，是开始冥想练习的好习惯", wait_time=1.8, filename="7a15b7458bb8d3ef5aa422722e81271d.mp3"),
                VoiceAction(action="play", text="请从鼻腔慢慢的吸气,再用鼻子缓缓的呼气", wait_time=1.8, filename="efa1c4994c5373e6bf26ba41a125dd49.mp3"),
                VoiceAction(action="play", text="均匀深长的吸气打开胸腔，呼气时用腹部微微内收", wait_time=1.8, filename="0b5ab9eee12574cda14e9527a8b25aa4.mp3"),
                VoiceAction(action="play", text="把所有的气体都排出体外", wait_time=1.8, filename="6c62f2337f2fc13e100aa58a4dfae33f.mp3"),
                VoiceAction(action="play", text="再做最后一次", wait_time=4, filename="a01f2fbd62a5113fdba4ae9ba3a54561.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_3: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="放松你的双眉，双眉之间的肌肉", wait_time=2, filename="6bcf9f7cdbfad6f62ec325d9aa1f7236.mp3"),
                VoiceAction(action="play", text="放松双眼", wait_time=2, filename="86f77165c429c1160b3e3f1df1ab3d93.mp3"),
                VoiceAction(action="play", text="放松咬合关节", wait_time=2, filename="cc711b040a052ba10a0b19f6f26ceda0.mp3"),
                VoiceAction(action="play", text="允许你的两排牙齿微微的张开一点,大约可以容纳一粒米通过的距离", wait_time=2, filename="387106902324b110efd7ba840a6f8d6d.mp3"),
                VoiceAction(action="play", text="允许整个面部表情再柔和一些", wait_time=2, filename="69f7046a6652b6d4327d7badd7ab0c80.mp3"),
                VoiceAction(action="play", text="现在，请让注意力,来到盆骨与座椅的接触面上", wait_time=2, filename="6aa5eb3465266760f199715da906abca.mp3"),
                VoiceAction(action="play", text="感受身体的重量和重心,让注意力来到双脚与大地的接触面", wait_time=2, filename="efa27afd75de8f0644e56a7b8684332a.mp3"),
                VoiceAction(action="play", text="感受大地所给予你的支持", wait_time=4, filename="da20afcb79240c9be520428ec1613f66.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_4: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="在接下来的练习中,请尽量的保持身体静止", wait_time=2, filename="16dde6a2c7bdde4f6ac5f27afe834f9c.mp3"),
                VoiceAction(action="play", text="如果需要,也可以简单的调整坐姿,但请你密切关注,身体活动所带来的感受", wait_time=2, filename="664b56678feea123fb07acf06905dc40.mp3"),
                VoiceAction(action="play", text="现在我想请你把注意力逐渐的放到呼吸上", wait_time=2, filename="a786cfa8bdbf42b0f9ada8d41d71d63c.mp3"),
                VoiceAction(action="play", text="注意空气，是如何经过你的鼻腔流入身体，又是如何经过鼻腔而流出的", wait_time=5.5, filename="8e717c309879d9199c2e5f5421933e2c.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_5: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="注意吸气时,你鼻腔感到微微凉爽,呼气温暖、湿润", wait_time=5, filename="2ef1e4d2a0e427bdcd694ad42c35dbd5.mp3"),
                VoiceAction(action="play", text="注意吸气和呼气之间,那短暂的暂停", wait_time=5, filename="86296aae1be81b437322d1a5b0f9f461.mp3"),
                VoiceAction(action="play", text="请既不用改变,也无需去控制呼吸,只是简单的跟随每一次呼吸的自然节奏", wait_time=14, filename="2c63e25bcf0f205cbba5955b1834a329.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_6: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="吸气时想象你的脊柱,向天空的方向延展", wait_time=2, filename="74d08d5af05953c4fd6984305c6595ee.mp3"),
                VoiceAction(action="play", text="从脊柱的最底端开始,随着每一次吸气,一节一节的向上生长", wait_time=2, filename="ad4aea019eba21273458998d2d3fc384.mp3"),
                VoiceAction(action="play", text="从腰椎", wait_time=2, filename="9c80b9bacdd1bf124d0dbfe03ee6b8c0.mp3"),
                VoiceAction(action="play", text="胸椎", wait_time=2, filename="6e1b92bb6dda145c62bba0bc752606ae.mp3"),
                VoiceAction(action="play", text="颈椎", wait_time=2, filename="058110452731601f5385f293e144b97d.mp3"),
                VoiceAction(action="play", text="一路向上延伸到头顶", wait_time=2, filename="f6d7a5f752e25c81725d5299235bbce3.mp3"),
                VoiceAction(action="play", text="让注意力停留在头顶片刻,去感受你的头顶变得越来越柔软,越来越开放", wait_time=6, filename="c9f1e17eb12d074b865ee5cd723664ae.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_7: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="现在随着每次呼气,让身体更加的放松", wait_time=2, filename="cddb76d9343e83eed784e5eb6ebc650c.mp3"),
                VoiceAction(action="play", text="再一次从头顶向下,顺着脊柱逐步的放松身体", wait_time=2, filename="eb52493325ba55a560f22d306fe38bc8.mp3"),
                VoiceAction(action="play", text="放松面部", wait_time=2, filename="51eca0dcdfb0c0b6a9f6be2c9939fc6a.mp3"),
                VoiceAction(action="play", text="放松脖颈", wait_time=2, filename="c28324ef7fc55dba710fa6e84a575bc5.mp3"),
                VoiceAction(action="play", text="放松双肩", wait_time=2, filename="0b4f7bf0dcf2136d78361fa1c4736a3e.mp3"),
                VoiceAction(action="play", text="双臂", wait_time=2, filename="1b26a0713f870db702ea39ef7858c8b0.mp3"),
                VoiceAction(action="play", text="呼气", wait_time=2, filename="f449961589c329b730e563ef6c028bbb.mp3"),
                VoiceAction(action="play", text="放松胸腔", wait_time=2, filename="5cb629ec02710406d68afb9f0bd4221c.mp3"),
                VoiceAction(action="play", text="放松腹部", wait_time=2, filename="0f305b959b069f0a3732d8dc97ca9233.mp3"),
                VoiceAction(action="play", text="放松你的双腿,双脚", wait_time=4, filename="de687d4fe456af446f210d9c6c0d65b7.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_8: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="如果你在身体中,发现任何紧绷的部位，请有意识的用呼气去放松那里", wait_time=9, filename="2a3c3fcde53e16f3565af1a9b1ed836b.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_9: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="现在请感受你的整个身体", wait_time=2, filename="0f30b7e451933cd36b6fa55033383a10.mp3"),
                VoiceAction(action="play", text="感受此刻你的坐姿中,所蕴含的庄严与稳定感", wait_time=8, filename="7f6d74391357721135ed6c204fdb686e.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_10: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="我希望你能将最后一分钟看作完全只属于你个人的空间", wait_time=2, filename="c4d477ee3247a5f03c47273985ed8fd9.mp3"),
                VoiceAction(action="play", text="安静的,和你内心里的庄严感相伴", wait_time=44, filename="303a489833e8b7eb8017288cc858dd50.mp3")
            ]
        )
    ),

    Mindfulness1StateType.MEDITATION_11: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="很好,恭喜你完成了第一节正念入门冥想课", wait_time=2, filename="89dcbd8d1f624693374cf7a151caf1c4.mp3"),
                VoiceAction(action="play", text="请花一点时间观察一下你此刻的感受,和刚刚开始练习前,有什么不同", wait_time=2, filename="eb3da4360b3c2229d61f9311652fb9b2.mp3"),
                VoiceAction(action="play", text="也许你发现了，只是刚刚这短短几分钟的练习,就对你产生了显著的影响,让你更加的清醒和放松", wait_time=2, filename="d4930b9d6accdd95301755692a8e9c50.mp3"),
                VoiceAction(action="play", text="在刚才的练习中,我们训练身体保持一种挺拔稳定的坐姿,并体验由内向外的尊严感,之后,我们使用均匀而悠长的呼吸节奏把心智安放到当下,在其中放松", wait_time=2, filename="07ca12a0c6ec9b5a62a5b2964b006b45.mp3"),
                VoiceAction(action="play", text="我希望你在练习以外的时间,也能记得不断提醒自己,保持自信而挺拔的姿态,随时回到悠长稳定的呼吸中", wait_time=4.5, filename="93fbde5ae6ce4f72d9c15ebb450a8e66.mp3")
            ]
        )
    ),
    
    Mindfulness1StateType.END: Actions(
        action_feature="",
        voice=VoiceSequence(
            voices=[
                VoiceAction(action="play", text="当你准备好后,请慢慢的睁开双眼", wait_time=2, filename="ede4429db184a05208ac2ff47d92aecb.mp3"),
                VoiceAction(action="play", text="我们明天第2节课中再见。", wait_time=2, filename="53aa15a77e024b4ae936a906aa16f3d7.mp3")
            ]
        )
    )
}

if __name__ == "__main__":
    # Test serialization (optional)
    # Ensure Actions class has a to_dict method or that __dict__ is sufficient for serialization
    try:
        serializable_dict = {state.name: action.to_dict() for state, action in states_dict.items()}
    except AttributeError: # Fallback if to_dict is not defined, common for simple data classes
        serializable_dict = {state.name: action.__dict__ for state, action in states_dict.items()}
        
    # Save to JSON file
    with open('mindfulness_meditation1_config.json', 'w', encoding='utf-8') as f:
        json.dump(serializable_dict, default=lambda x: x.__dict__, indent=2, ensure_ascii=False, fp=f)
    print("Config saved to mindfulness_meditation1_config.json")

    # Test state iteration (optional)
    current_state = Mindfulness1StateType.PREPARE # Start with the first state from config.md
    print("Starting test state iteration...")
    while current_state:
        print(f"Current state: {current_state.name_cn} (Order: {current_state.order})")
        if current_state in states_dict and states_dict[current_state].voice:
            for voice_action in states_dict[current_state].voice.voices:
                print(f"  - Playing: {voice_action.text} (Wait: {voice_action.wait_time}s, File: {voice_action.filename})")
        
        if current_state == Mindfulness1StateType.END:
            print("Reached END state. Sequence complete.")
            break
        
        next_state = Mindfulness1StateType.get_next_state(current_state.order)
        if not next_state:
            print(f"No next state after {current_state.name_cn}. Sequence might be incomplete or this is the intended end.")
            break
        current_state = next_state
    print("Test state iteration finished.")