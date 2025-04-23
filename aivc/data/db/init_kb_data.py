from aivc.data.db import kb
from aivc.data.db.pg_engine import engine
from sqlmodel import Session
from aivc.model.embed.embed import EmbedModel
from aivc.common.task_class import QuestionType


def init_kb_data():
    with Session(engine) as session:
        categories = [
            {"category_name": QuestionType.ABOUT.value, "answer": """我是第七生命科技的陪伴机器人。"""},
            {"category_name": QuestionType.SUPPORT.value, "answer": """如需帮助，我们提供多种联系方式：
• 官方网站：www.7thlife.com
• 客服邮箱：support@7thlife.com
我们的技术团队将为您提供专业、及时的支持服务。"""},
            {"category_name": QuestionType.SONG.value, "answer": ""},
            {"category_name": QuestionType.TAKE_PHOTO.value, "answer": ""},
            {"category_name": QuestionType.WEATHER.value, "answer": ""},
            {"category_name": QuestionType.SLEEP_ASSISTANT.value, "answer": ""},


            # 音量控制类别
            {"category_name": QuestionType.VOLUME_MAIN_UP.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_MAIN_DOWN.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_MUTE.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_VOICE_UP.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_VOICE_DOWN.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_VOICE_MUTE.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_BACKGROUND_UP.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_BACKGROUND_DOWN.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_BACKGROUND_MUTE.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_MUSIC_UP.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_MUSIC_DOWN.value, "answer": ""},
            {"category_name": QuestionType.VOLUME_MUSIC_MUTE.value, "answer": ""},
            
            # 灯光控制类别
            {"category_name": QuestionType.LIGHT_BRIGHTNESS_UP.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_BRIGHTNESS_DOWN.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_COLOR_GREEN.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_COLOR_RED.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_COLOR_BLUE.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_COLOR_PURPLE.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_COLOR_YELLOW.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_COLOR_WHITE.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_STATE_ON.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_STATE_OFF.value, "answer": ""},
            # 新增灯光模式类别
            {"category_name": QuestionType.LIGHT_MODE_FLOWING_COLOR.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_STARRY_SKY.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_JELLYFISH.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_FLAME.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_WAVES.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_RANDOM.value, "answer": ""},
            
            # 香薰控制类别
            {"category_name": QuestionType.FRAGRANCE_ON.value, "answer": ""},
            {"category_name": QuestionType.FRAGRANCE_OFF.value, "answer": ""},
            
            # 系统控制类别
            {"category_name": QuestionType.SYSTEM_SLEEP.value, "answer": ""},
        ]
        
        category_objects = {}
        for cat in categories:
            category = kb.create_category(
                session=session,
                category_name=cat["category_name"],
                answer=cat["answer"]
            )
            category_objects[cat["category_name"]] = category
            

        questions = []
        about_similar_words = ["技术支持","如何联系","联系方式","怎么联系","联系客服","联系技术支持","联系开发者","联系管理员"]
        for word in about_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SUPPORT.value,
                "vector": EmbedModel().embed(word)
            })

        about_similar_words = [
                "你的名字", "你是什么", "你来自哪里", 
                "你是谁呀", "你叫什么名字", "你是机器人吗",
                "介绍一下你自己", "你能干什么", "你会做什么",
                "我想认识你", "和我说说你吧", "你好厉害啊是谁呀","自我介绍"
            ]
        for word in about_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.ABOUT.value,
                "vector": EmbedModel().embed(word)
            })

        song_similar_words = [
                "唱歌", "唱首歌", "唱个儿歌",
                "给我唱歌", "给我唱个儿歌", "唱首儿歌",
                "会唱歌吗", "你会唱歌吗", "来一首儿歌",
                "想听儿歌", "我要听歌", "给我来首歌",
                "换首歌"]
        for word in song_similar_words:
            questions.append({
                "question": word,
                "category_name": "song",
                "vector": EmbedModel().embed(word)
            })
        
        take_photo_similar_words = [
                "这是什么", "我手里的是什么"
            ]
        for word in take_photo_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.TAKE_PHOTO.value,
                "vector": EmbedModel().embed(word)
            })


        weather_similar_words = [
                "天气怎么样", "晴天", "雨天", "阴天", "天气预报","温度","气温","风向","风速","风力","降水量","气压","紫外线","湿度","大气压强","能见度","云量"]
        for word in weather_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.WEATHER.value,
                "vector": EmbedModel().embed(word)
            })


        sleep_assistant_similar_words = ["我有些累了", "我要睡觉"]
        for word in sleep_assistant_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SLEEP_ASSISTANT.value,
                "vector": EmbedModel().embed(word)
            })

        # 音量控制相关问题
        volume_main_up_similar_words = ["调高音量", "声音大点", "音量调大", "音量调高", "声音调大"]
        for word in volume_main_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MAIN_UP.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_main_down_similar_words = ["调低音量", "声音小点", "音量调小", "音量调低", "声音调小"]
        for word in volume_main_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MAIN_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_mute_similar_words = ["静音", "关闭声音", "不要声音", "声音静音"]
        for word in volume_mute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MUTE.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_voice_up_similar_words = ["语音音量调高", "语音声音大点", "语音调大"]
        for word in volume_voice_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_VOICE_UP.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_voice_down_similar_words = ["语音音量调低", "语音声音小点", "语音调小"]
        for word in volume_voice_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_VOICE_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_voice_mute_similar_words = ["语音静音", "关闭语音声音", "不要语音"]
        for word in volume_voice_mute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_VOICE_MUTE.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 背景音量控制
        volume_background_up_similar_words = ["背景音量调高", "背景声音大点", "背景音乐调大"]
        for word in volume_background_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_BACKGROUND_UP.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_background_down_similar_words = ["背景音量调低", "背景声音小点", "背景音乐调小"]
        for word in volume_background_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_BACKGROUND_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_background_mute_similar_words = ["背景静音", "关闭背景声音", "背景音乐静音"]
        for word in volume_background_mute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_BACKGROUND_MUTE.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 音乐音量控制
        volume_music_up_similar_words = ["音乐音量调高", "音乐声音大点", "音乐调大"]
        for word in volume_music_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MUSIC_UP.value,
                "vector": EmbedModel().embed(word)
            })
            
        volume_music_down_similar_words = ["音乐音量调低", "音乐声音小点", "音乐调小"]
        for word in volume_music_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MUSIC_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
            
        volume_music_mute_similar_words = ["音乐静音", "关闭音乐声音", "不要音乐声音"]
        for word in volume_music_mute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MUSIC_MUTE.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 灯光控制相关问题
        light_brightness_up_similar_words = ["调亮灯光", "灯光亮一点", "把灯调亮", "灯光调亮"]
        for word in light_brightness_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_BRIGHTNESS_UP.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_brightness_down_similar_words = ["调暗灯光", "灯光暗一点", "把灯调暗", "灯光调暗"]
        for word in light_brightness_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_BRIGHTNESS_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 灯光颜色控制
        light_color_green_similar_words = ["灯光变绿色", "把灯调成绿色", "绿色灯光"]
        for word in light_color_green_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_GREEN.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_red_similar_words = ["灯光变红色", "把灯调成红色", "红色灯光"]
        for word in light_color_red_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_RED.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_blue_similar_words = ["灯光变蓝色", "把灯调成蓝色", "蓝色灯光", "蓝光"]
        for word in light_color_blue_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_BLUE.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_purple_similar_words = ["灯光变紫色", "把灯调成紫色", "紫色灯光", "紫光"]
        for word in light_color_purple_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_PURPLE.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_yellow_similar_words = ["灯光变黄色", "把灯调成黄色", "黄色灯光", "黄光"]
        for word in light_color_yellow_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_YELLOW.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_white_similar_words = ["灯光变白色", "把灯调成白色", "白色灯光", "白光", "灯光变成自然光"]
        for word in light_color_white_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_WHITE.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_state_on_similar_words = ["开灯", "打开灯", "开启灯光"]
        for word in light_state_on_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_STATE_ON.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_state_off_similar_words = ["关灯", "关闭灯", "关闭灯光"]
        for word in light_state_off_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_STATE_OFF.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 新增灯光模式相关问题
        light_mode_flowing_color_similar_words = ["流光溢彩模式灯光", "流光溢彩灯光"]
        for word in light_mode_flowing_color_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_FLOWING_COLOR.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_starry_sky_similar_words = ["星空模式灯光", "星空灯光"]
        for word in light_mode_starry_sky_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_STARRY_SKY.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_jellyfish_similar_words = ["水母模式灯光", "水母灯光"]
        for word in light_mode_jellyfish_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_JELLYFISH.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_flame_similar_words = ["火焰模式灯光", "火焰灯光"]
        for word in light_mode_flame_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_FLAME.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_waves_similar_words = ["海浪模式灯光", "海浪灯光"]
        for word in light_mode_waves_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_WAVES.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_random_similar_words = ["切换灯光模式","随机模式灯光", "随机灯光"]
        for word in light_mode_random_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_RANDOM.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 香薰控制相关问题
        fragrance_on_similar_words = ["开香薰", "打开香薰", "开启香薰"]
        for word in fragrance_on_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.FRAGRANCE_ON.value,
                "vector": EmbedModel().embed(word)
            })
        
        fragrance_off_similar_words = ["关香薰", "关闭香薰", "关掉香薰"]
        for word in fragrance_off_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.FRAGRANCE_OFF.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 系统控制相关问题
        system_sleep_similar_words = ["进入睡眠", "系统睡眠", "休眠"]
        for word in system_sleep_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SYSTEM_SLEEP.value,
                "vector": EmbedModel().embed(word)
            })

        for q in questions:
            kb.create_question(
                session=session,
                question=q["question"],
                vector=q["vector"],
                category_id=category_objects[q["category_name"]].id
            )
        print("示例数据初始化完成")


if __name__ == '__main__':
    init_kb_data()