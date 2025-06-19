from aivc.data.db import kb
from aivc.data.db.pg_engine import engine
from sqlmodel import Session
from aivc.model.embed.embed import EmbedModel
from aivc.common.task_class import QuestionType


def init_kb_data():
    with Session(engine) as session:
        # 创建嵌入模型实例
        # embed_model_v1 = EmbedModel(EmbedModel.V1)
        embed_model_v2 = EmbedModel(EmbedModel.V2)
        
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
            {"category_name": QuestionType.VOLUME_UNMUTE.value, "answer": ""},
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
            {"category_name": QuestionType.NIGHT_LIGHT_ON.value, "answer": ""},
            {"category_name": QuestionType.NIGHT_LIGHT_OFF.value, "answer": ""},
            
            # 新增灯光模式类别
            {"category_name": QuestionType.LIGHT_MODE_FLOWING_COLOR.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_STARRY_SKY.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_JELLYFISH.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_FLAME.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_WAVES.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_RANDOM.value, "answer": ""},
            {"category_name": QuestionType.LIGHT_MODE_NEXT.value, "answer": ""},
            
            # 香薰控制类别
            {"category_name": QuestionType.FRAGRANCE_ON.value, "answer": ""},
            {"category_name": QuestionType.FRAGRANCE_OFF.value, "answer": ""},
            {"category_name": QuestionType.FRAGRANCE_LOWER.value, "answer": ""},
            {"category_name": QuestionType.FRAGRANCE_HIGHER.value, "answer": ""},
            
            # 系统控制类别
            {"category_name": QuestionType.SYSTEM_SLEEP.value, "answer": ""},
            {"category_name": QuestionType.SYSTEM_SHUTDOWN.value, "answer": ""},
            
            # 摄像头控制类别
            {"category_name": QuestionType.CAMERA_ON.value, "answer": ""},
            {"category_name": QuestionType.CAMERA_OFF.value, "answer": ""},
            
            # 麦克风控制类别
            {"category_name": QuestionType.MICROPHONE_ON.value, "answer": ""},
            {"category_name": QuestionType.MICROPHONE_OFF.value, "answer": ""},
            
            # 屏幕控制类别
            {"category_name": QuestionType.SCREEN_BRIGHTNESS_UP.value, "answer": ""},
            {"category_name": QuestionType.SCREEN_BRIGHTNESS_DOWN.value, "answer": ""},
            
            # 冥想功能类别
            {"category_name": QuestionType.MEDITATION_START.value, "answer": ""},
            {"category_name": QuestionType.MEDITATION_STOP.value, "answer": ""},
            
            # 助眠功能类别
            {"category_name": QuestionType.SLEEP_ASSISTANT_START.value, "answer": ""},
            {"category_name": QuestionType.SLEEP_ASSISTANT_STOP.value, "answer": ""},
            
            # 音乐播放控制类别
            {"category_name": QuestionType.MUSIC_PLAY.value, "answer": ""},
            {"category_name": QuestionType.MUSIC_STOP.value, "answer": ""},
            {"category_name": QuestionType.MUSIC_NEXT.value, "answer": ""},
            {"category_name": QuestionType.MUSIC_REPEAT_ALL.value, "answer": ""},
            {"category_name": QuestionType.MUSIC_REPEAT_ONE.value, "answer": ""},
            
            # 闹钟功能类别
            {"category_name": QuestionType.ALARM_START.value, "answer": ""},
            {"category_name": QuestionType.ALARM_STOP.value, "answer": ""},
            {"category_name": QuestionType.ALARM_SET.value, "answer": ""},
            {"category_name": QuestionType.ALARM_CANCEL.value, "answer": ""},
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
        about_similar_words_en = ["Technical support", "How to contact", "Contact information", "How to contact us", "Contact customer service", "Contact technical support", "Contact developer", "Contact administrator"]
        about_similar_words.extend(about_similar_words_en)
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
        about_similar_words_en = [
                "What's your name?", "What are you?", "Where are you from?",
                "Who are you?", "What is your name?", "Are you a robot?",
                "Introduce yourself.", "What can you do?", "What will you do?",
                "I want to know you.", "Tell me about yourself.", "You are so smart, who are you?", "Self-introduction"
            ]
        about_similar_words.extend(about_similar_words_en)
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
        song_similar_words_en = [
                "Sing", "Sing a song", "Sing a children's song",
                "Sing for me", "Sing me a children's song", "Sing a children's song",
                "Can you sing?", "Can you sing?", "Play a children's song",
                "I want to hear a children's song", "I want to listen to music", "Play me a song",
                "Change the song"]
        song_similar_words.extend(song_similar_words_en)
        for word in song_similar_words:
            questions.append({
                "question": word,
                "category_name": "song",
                "vector": EmbedModel().embed(word)
            })
        
        take_photo_similar_words = [
                "这是什么", "我手里的是什么"
            ]
        take_photo_similar_words_en = [
                "What is this?", "What am I holding?"
            ]
        take_photo_similar_words.extend(take_photo_similar_words_en)
        for word in take_photo_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.TAKE_PHOTO.value,
                "vector": EmbedModel().embed(word)
            })


        weather_similar_words = [
                "天气怎么样", "晴天", "雨天", "阴天", "天气预报","温度","气温","风向","风速","风力","降水量","气压","紫外线","湿度","大气压强","能见度","云量"]
        weather_similar_words_en = [
                "How's the weather?", "Sunny day", "Rainy day", "Cloudy day", "Weather forecast", "Temperature", "Air temperature", "Wind direction", "Wind speed", "Wind force", "Precipitation", "Air pressure", "UV index", "Humidity", "Atmospheric pressure", "Visibility", "Cloud cover"]
        weather_similar_words.extend(weather_similar_words_en)
        for word in weather_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.WEATHER.value,
                "vector": EmbedModel().embed(word)
            })


        sleep_assistant_similar_words = ["我有些累了", "我要睡觉"]
        sleep_assistant_similar_words_en = ["I'm a bit tired", "I want to sleep"]
        sleep_assistant_similar_words.extend(sleep_assistant_similar_words_en)
        for word in sleep_assistant_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SLEEP_ASSISTANT.value,
                "vector": EmbedModel().embed(word)
            })

        # 音量控制相关问题
        volume_main_up_similar_words = ["调高音量","调高声音", "音量调高", "声音大点", "音量调大",  "声音调大","音量大点"]
        volume_main_up_similar_words_en = ["Turn up volume", "Increase volume", "Make volume higher", "Volume up", "Make it louder", "Higher volume", "Volume louder"]
        volume_main_up_similar_words.extend(volume_main_up_similar_words_en)
        for word in volume_main_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MAIN_UP.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_main_down_similar_words = ["调低音量", "声音小点", "音量调小", "音量调低", "声音调小"]
        volume_main_down_similar_words_en = ["Decrease volume", "Turn down the volume", "Make it quieter", "Volume down", "Turn it down"]
        volume_main_down_similar_words.extend(volume_main_down_similar_words_en)
        for word in volume_main_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MAIN_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_mute_similar_words = ["静音", "关闭声音", "不要声音", "声音静音", "关闭语音"]
        volume_mute_similar_words_en = ["Mute", "Turn off sound", "No sound", "Audio mute", "Turn off voice"]
        volume_mute_similar_words.extend(volume_mute_similar_words_en)
        for word in volume_mute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MUTE.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_voice_up_similar_words = ["语音音量调高", "语音声音大点", "语音调大"]
        volume_voice_up_similar_words_en = ["Increase voice volume", "Voice louder", "Turn up voice"]
        volume_voice_up_similar_words.extend(volume_voice_up_similar_words_en)
        for word in volume_voice_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_VOICE_UP.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_voice_down_similar_words = ["语音音量调低", "语音声音小点", "语音调小"]
        volume_voice_down_similar_words_en = ["Decrease voice volume", "Voice quieter", "Turn down voice", "Make voice softer"]
        volume_voice_down_similar_words.extend(volume_voice_down_similar_words_en)
        for word in volume_voice_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_VOICE_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_voice_mute_similar_words = ["语音静音", "关闭语音声音", "不要语音"]
        volume_voice_mute_similar_words_en = ["Mute voice", "Turn off voice", "No voice"]
        volume_voice_mute_similar_words.extend(volume_voice_mute_similar_words_en)
        for word in volume_voice_mute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_VOICE_MUTE.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 背景音量控制
        volume_background_up_similar_words = ["背景音量调高", "背景声音大点", "背景音乐调大"]
        volume_background_up_similar_words_en = ["Increase background volume", "Background louder", "Turn up background music"]
        volume_background_up_similar_words.extend(volume_background_up_similar_words_en)
        for word in volume_background_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_BACKGROUND_UP.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_background_down_similar_words = ["背景音量调低", "背景声音小点", "背景音乐调小"]
        volume_background_down_similar_words_en = ["Decrease background volume", "Background quieter", "Turn down background music"]
        volume_background_down_similar_words.extend(volume_background_down_similar_words_en)
        for word in volume_background_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_BACKGROUND_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
        
        volume_background_mute_similar_words = ["背景静音", "关闭背景声音", "背景音乐静音"]
        volume_background_mute_similar_words_en = ["Mute background", "Turn off background sound", "Silent background music"]
        volume_background_mute_similar_words.extend(volume_background_mute_similar_words_en)
        for word in volume_background_mute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_BACKGROUND_MUTE.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 音乐音量控制
        volume_music_up_similar_words = ["音乐音量调高", "音乐声音大点", "音乐调大"]
        volume_music_up_similar_words_en = ["Increase music volume", "Music louder", "Turn up music"]
        volume_music_up_similar_words.extend(volume_music_up_similar_words_en)
        for word in volume_music_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MUSIC_UP.value,
                "vector": EmbedModel().embed(word)
            })
            
        volume_music_down_similar_words = ["音乐音量调低", "音乐声音小点", "音乐调小"]
        volume_music_down_similar_words_en = ["Decrease music volume", "Music quieter", "Turn down music"]
        volume_music_down_similar_words.extend(volume_music_down_similar_words_en)
        for word in volume_music_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MUSIC_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
            
        volume_music_mute_similar_words = ["音乐静音", "关闭音乐声音", "不要音乐声音"]
        volume_music_mute_similar_words_en = ["Mute music", "Turn off music sound", "No music sound"]
        volume_music_mute_similar_words.extend(volume_music_mute_similar_words_en)
        for word in volume_music_mute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_MUSIC_MUTE.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 灯光控制相关问题
        light_brightness_up_similar_words = ["调亮灯光", "灯光亮一点", "把灯调亮", "灯光调亮"]
        light_brightness_up_similar_words_en = ["Brighten lights", "Make lights brighter", "Turn up the lights", "Increase brightness"]
        light_brightness_up_similar_words.extend(light_brightness_up_similar_words_en)
        for word in light_brightness_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_BRIGHTNESS_UP.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_brightness_down_similar_words = ["调暗灯光", "灯光暗一点", "把灯调暗", "灯光调暗"]
        light_brightness_down_similar_words_en = ["Dim lights", "Make lights darker", "Turn down the lights", "Decrease brightness"]
        light_brightness_down_similar_words.extend(light_brightness_down_similar_words_en)
        for word in light_brightness_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_BRIGHTNESS_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 灯光颜色控制
        light_color_green_similar_words = ["灯光变绿色", "把灯调成绿色", "绿色灯光"]
        light_color_green_similar_words_en = ["Green lights", "Change lights to green", "Make the lights green"]
        light_color_green_similar_words.extend(light_color_green_similar_words_en)
        for word in light_color_green_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_GREEN.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_red_similar_words = ["灯光变红色", "把灯调成红色", "红色灯光"]
        light_color_red_similar_words_en = ["Red lights", "Change lights to red", "Make the lights red"]
        light_color_red_similar_words.extend(light_color_red_similar_words_en)
        for word in light_color_red_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_RED.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_blue_similar_words = ["灯光变蓝色", "把灯调成蓝色", "蓝色灯光", "蓝光"]
        light_color_blue_similar_words_en = ["Blue lights", "Change lights to blue", "Make the lights blue", "Blue light"]
        light_color_blue_similar_words.extend(light_color_blue_similar_words_en)
        for word in light_color_blue_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_BLUE.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_purple_similar_words = ["灯光变紫色", "把灯调成紫色", "紫色灯光", "紫光"]
        light_color_purple_similar_words_en = ["Purple lights", "Change lights to purple", "Make the lights purple", "Purple light"]
        light_color_purple_similar_words.extend(light_color_purple_similar_words_en)
        for word in light_color_purple_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_PURPLE.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_yellow_similar_words = ["灯光变黄色", "把灯调成黄色", "黄色灯光", "黄光"]
        light_color_yellow_similar_words_en = ["Yellow lights", "Change lights to yellow", "Make the lights yellow", "Yellow light"]
        light_color_yellow_similar_words.extend(light_color_yellow_similar_words_en)
        for word in light_color_yellow_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_YELLOW.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_color_white_similar_words = ["灯光变白色", "把灯调成白色", "白色灯光", "白光", "灯光变成自然光"]
        light_color_white_similar_words_en = ["White lights", "Change lights to white", "Make the lights white", "White light", "Natural light"]
        light_color_white_similar_words.extend(light_color_white_similar_words_en)
        for word in light_color_white_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_COLOR_WHITE.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_state_on_similar_words = ["开灯", "打开灯", "开启灯光"]
        light_state_on_similar_words_en = ["Turn on the lights", "Lights on", "Switch on lights"]
        light_state_on_similar_words.extend(light_state_on_similar_words_en)
        for word in light_state_on_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_STATE_ON.value,
                "vector": EmbedModel().embed(word)
            })
        
        light_state_off_similar_words = ["关灯", "关闭灯", "关闭灯光"]
        light_state_off_similar_words_en = ["Turn off the lights", "Lights off", "Switch off lights"]
        light_state_off_similar_words.extend(light_state_off_similar_words_en)
        for word in light_state_off_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_STATE_OFF.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 新增灯光模式相关问题
        light_mode_flowing_color_similar_words = ["流光溢彩模式灯光", "流光溢彩灯光"]
        light_mode_flowing_color_similar_words_en = ["Flowing color light mode", "Colorful light mode"]
        light_mode_flowing_color_similar_words.extend(light_mode_flowing_color_similar_words_en)
        for word in light_mode_flowing_color_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_FLOWING_COLOR.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_starry_sky_similar_words = ["星空模式灯光", "星空灯光"]
        light_mode_starry_sky_similar_words_en = ["Starry sky light mode", "Star light mode"]
        light_mode_starry_sky_similar_words.extend(light_mode_starry_sky_similar_words_en)
        for word in light_mode_starry_sky_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_STARRY_SKY.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_jellyfish_similar_words = ["水母模式灯光", "水母灯光"]
        light_mode_jellyfish_similar_words_en = ["Jellyfish light mode", "Jellyfish lighting"]
        light_mode_jellyfish_similar_words.extend(light_mode_jellyfish_similar_words_en)
        for word in light_mode_jellyfish_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_JELLYFISH.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_flame_similar_words = ["火焰模式灯光", "火焰灯光"]
        light_mode_flame_similar_words_en = ["Flame light mode", "Fire light mode", "Flame lights"]
        light_mode_flame_similar_words.extend(light_mode_flame_similar_words_en)
        for word in light_mode_flame_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_FLAME.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_waves_similar_words = ["海浪模式灯光", "海浪灯光", "显示波浪光效"]
        light_mode_waves_similar_words_en = ["Wave light mode", "Ocean wave lights","Show wave light effect"]
        light_mode_waves_similar_words.extend(light_mode_waves_similar_words_en)
        for word in light_mode_waves_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_WAVES.value,
                "vector": EmbedModel().embed(word)
            })
            
        light_mode_random_similar_words = ["切换灯光模式","随机模式灯光", "随机灯光"]
        light_mode_random_similar_words_en = ["Switch light mode", "Random light mode", "Random lights"]
        light_mode_random_similar_words.extend(light_mode_random_similar_words_en)
        for word in light_mode_random_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_RANDOM.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 香薰控制相关问题
        fragrance_on_similar_words = ["开香薰", "打开香薰", "开启香薰"]
        fragrance_on_similar_words_en = ["Turn on fragrance", "Start fragrance", "Enable aroma"]
        fragrance_on_similar_words.extend(fragrance_on_similar_words_en)
        for word in fragrance_on_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.FRAGRANCE_ON.value,
                "vector": EmbedModel().embed(word)
            })
        
        fragrance_off_similar_words = ["关香薰", "关闭香薰", "关掉香薰"]
        fragrance_off_similar_words_en = ["Turn off fragrance", "Stop fragrance", "Disable aroma"]
        fragrance_off_similar_words.extend(fragrance_off_similar_words_en)
        for word in fragrance_off_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.FRAGRANCE_OFF.value,
                "vector": EmbedModel().embed(word)
            })
        
        # 系统控制相关问题
        system_sleep_similar_words = ["进入睡眠", "系统睡眠", "休眠"]
        system_sleep_similar_words_en = ["Enter sleep mode", "System sleep", "Hibernate"]
        system_sleep_similar_words.extend(system_sleep_similar_words_en)
        for word in system_sleep_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SYSTEM_SLEEP.value,
                "vector": EmbedModel().embed(word)
            })

        # 音量解除静音
        volume_unmute_similar_words = ["开启声音", "取消静音", "打开声音", "解除静音"]
        volume_unmute_similar_words_en = ["Turn on sound", "Unmute", "Enable sound", "Cancel mute"]
        volume_unmute_similar_words.extend(volume_unmute_similar_words_en)
        for word in volume_unmute_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.VOLUME_UNMUTE.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 夜灯控制
        night_light_on_similar_words = ["打开夜灯", "开夜灯", "开启夜灯模式"]
        night_light_on_similar_words_en = ["Turn on night light", "Enable night light", "Night light on"]
        night_light_on_similar_words.extend(night_light_on_similar_words_en)
        for word in night_light_on_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.NIGHT_LIGHT_ON.value,
                "vector": EmbedModel().embed(word)
            })
            
        night_light_off_similar_words = ["关闭夜灯", "关夜灯", "停止夜灯", "关掉夜灯"]
        night_light_off_similar_words_en = ["Turn off night light", "Disable night light", "Night light off", "Stop night light"]
        night_light_off_similar_words.extend(night_light_off_similar_words_en)
        for word in night_light_off_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.NIGHT_LIGHT_OFF.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 灯光模式切换
        light_mode_next_similar_words = ["切换灯光模式", "下一个灯光模式", "切换灯效", "更换灯光模式"]
        light_mode_next_similar_words_en = ["Switch light mode", "Next light mode", "Change lighting effect", "Change light mode"]
        light_mode_next_similar_words.extend(light_mode_next_similar_words_en)
        for word in light_mode_next_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.LIGHT_MODE_NEXT.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 香薰强度调节
        fragrance_lower_similar_words = ["香味淡一点", "香味调淡", "香味太浓了", "降低香薰强度"]
        fragrance_lower_similar_words_en = ["Lower fragrance", "Reduce aroma intensity", "Less fragrance", "Decrease fragrance strength"]
        fragrance_lower_similar_words.extend(fragrance_lower_similar_words_en)
        for word in fragrance_lower_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.FRAGRANCE_LOWER.value,
                "vector": EmbedModel().embed(word)
            })
            
        fragrance_higher_similar_words = ["香味浓一点", "香味调浓", "香味太淡了", "增加香薰强度"]
        fragrance_higher_similar_words_en = ["Stronger fragrance", "Increase aroma intensity", "More fragrance", "Increase fragrance strength"]
        fragrance_higher_similar_words.extend(fragrance_higher_similar_words_en)
        for word in fragrance_higher_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.FRAGRANCE_HIGHER.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 系统关机
        system_shutdown_similar_words = ["关机", "关闭机器", "关闭设备", "关闭系统"]
        system_shutdown_similar_words_en = ["Shut down", "Power off", "Turn off device", "System off"]
        system_shutdown_similar_words.extend(system_shutdown_similar_words_en)
        for word in system_shutdown_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SYSTEM_SHUTDOWN.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 摄像头控制
        camera_on_similar_words = ["打开摄像头", "打开摄像", "打开监控", "打开录像"]
        camera_on_similar_words_en = ["Turn on camera", "Enable camera", "Start camera", "Start recording"]
        camera_on_similar_words.extend(camera_on_similar_words_en)
        for word in camera_on_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.CAMERA_ON.value,
                "vector": EmbedModel().embed(word)
            })
            
        camera_off_similar_words = ["关闭摄像头", "关闭摄像", "关闭监控", "关闭录像"]
        camera_off_similar_words_en = ["Turn off camera", "Disable camera", "Stop camera", "Stop recording"]
        camera_off_similar_words.extend(camera_off_similar_words_en)
        for word in camera_off_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.CAMERA_OFF.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 麦克风控制
        microphone_on_similar_words = ["打开麦克风", "打开话筒", "开启麦克风"]
        microphone_on_similar_words_en = ["Turn on microphone", "Enable microphone", "Start microphone"]
        microphone_on_similar_words.extend(microphone_on_similar_words_en)
        for word in microphone_on_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MICROPHONE_ON.value,
                "vector": EmbedModel().embed(word)
            })
            
        microphone_off_similar_words = ["关闭麦克风", "关闭话筒", "停用麦克风"]
        microphone_off_similar_words_en = ["Turn off microphone", "Disable microphone", "Stop microphone"]
        microphone_off_similar_words.extend(microphone_off_similar_words_en)
        for word in microphone_off_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MICROPHONE_OFF.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 屏幕亮度控制
        screen_brightness_up_similar_words = ["调亮屏幕", "屏幕亮一点", "屏幕太暗了", "增加屏幕亮度"]
        screen_brightness_up_similar_words_en = ["Brighten screen", "Screen brighter", "Screen too dark", "Increase screen brightness"]
        screen_brightness_up_similar_words.extend(screen_brightness_up_similar_words_en)
        for word in screen_brightness_up_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SCREEN_BRIGHTNESS_UP.value,
                "vector": EmbedModel().embed(word)
            })
            
        screen_brightness_down_similar_words = ["调暗屏幕", "屏幕暗一点", "屏幕太亮了", "降低屏幕亮度"]
        screen_brightness_down_similar_words_en = ["Dim screen", "Screen darker", "Screen too bright", "Decrease screen brightness"]
        screen_brightness_down_similar_words.extend(screen_brightness_down_similar_words_en)
        for word in screen_brightness_down_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SCREEN_BRIGHTNESS_DOWN.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 冥想功能
        meditation_start_similar_words = ["打开冥想", "开始冥想", "我要冥想", "进入冥想", "冥想"]
        meditation_start_similar_words_en = ["Start meditation", "Begin meditation", "I want to meditate", "Enter meditation", "Meditation"]
        meditation_start_similar_words.extend(meditation_start_similar_words_en)
        for word in meditation_start_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MEDITATION_START.value,
                "vector": EmbedModel().embed(word)
            })
            
        meditation_stop_similar_words = ["关闭冥想", "停止冥想", "退出冥想", "结束冥想", "不冥想了"]
        meditation_stop_similar_words_en = ["Stop meditation", "End meditation", "Exit meditation", "Quit meditation", "No more meditation"]
        meditation_stop_similar_words.extend(meditation_stop_similar_words_en)
        for word in meditation_stop_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MEDITATION_STOP.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 助眠功能
        sleep_assistant_start_similar_words = ["打开助眠", "开始助眠", "开启助眠功能", "助眠"]
        sleep_assistant_start_similar_words_en = ["Start sleep aid", "Begin sleep assistance", "Enable sleep mode", "sleep assistance"]
        sleep_assistant_start_similar_words.extend(sleep_assistant_start_similar_words_en)
        for word in sleep_assistant_start_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SLEEP_ASSISTANT_START.value,
                "vector": EmbedModel().embed(word)
            })
            
        sleep_assistant_stop_similar_words = ["关闭助眠", "停止助眠", "退出助眠", "结束助眠", "不需要助眠了"]
        sleep_assistant_stop_similar_words_en = ["Stop sleep aid", "End sleep assistance", "Exit sleep mode", "Stop sleeping help", "Don't need sleep aid anymore"]
        sleep_assistant_stop_similar_words.extend(sleep_assistant_stop_similar_words_en)
        for word in sleep_assistant_stop_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.SLEEP_ASSISTANT_STOP.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 音乐播放控制
        music_play_similar_words = ["打开音乐", "播放音乐", "来点音乐", "开始播放", "放首歌"]
        music_play_similar_words_en = ["Play music", "Start music", "Some music please", "Begin playback", "Play a song"]
        music_play_similar_words.extend(music_play_similar_words_en)
        for word in music_play_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MUSIC_PLAY.value,
                "vector": EmbedModel().embed(word)
            })
            
        music_stop_similar_words = ["关闭音乐", "停止播放", "不要音乐了", "停止音乐", "关掉歌曲"]
        music_stop_similar_words_en = ["Stop music", "Stop playback", "No more music", "Turn off music", "End song"]
        music_stop_similar_words.extend(music_stop_similar_words_en)
        for word in music_stop_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MUSIC_STOP.value,
                "vector": EmbedModel().embed(word)
            })
            
        music_next_similar_words = ["换一首", "换个音乐", "下一首", "下一曲", "切歌"]
        music_next_similar_words_en = ["Next song", "Change music", "Next track", "Skip song", "Another song"]
        music_next_similar_words.extend(music_next_similar_words_en)
        for word in music_next_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MUSIC_NEXT.value,
                "vector": EmbedModel().embed(word)
            })
            
        music_repeat_all_similar_words = ["循环播放", "全部循环", "列表循环", "顺序循环"]
        music_repeat_all_similar_words_en = ["Repeat all", "Loop all", "Playlist repeat", "Sequential repeat"]
        music_repeat_all_similar_words.extend(music_repeat_all_similar_words_en)
        for word in music_repeat_all_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MUSIC_REPEAT_ALL.value,
                "vector": EmbedModel().embed(word)
            })
            
        music_repeat_one_similar_words = ["单曲循环", "单曲重复", "重复这首歌", "循环当前歌曲"]
        music_repeat_one_similar_words_en = ["Repeat one", "Single track repeat", "Repeat this song", "Loop current song"]
        music_repeat_one_similar_words.extend(music_repeat_one_similar_words_en)
        for word in music_repeat_one_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.MUSIC_REPEAT_ONE.value,
                "vector": EmbedModel().embed(word)
            })
            
        # 闹钟功能
        alarm_start_similar_words = ["打开闹钟", "开启闹钟"]
        alarm_start_similar_words_en = ["Open alarm", "Enable alarm"]
        alarm_start_similar_words.extend(alarm_start_similar_words_en)
        for word in alarm_start_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.ALARM_START.value,
                "vector": EmbedModel().embed(word)
            })
            
        alarm_stop_similar_words = ["关闭闹钟", "停止闹钟"]
        alarm_stop_similar_words_en = ["Stop alarm", "Turn off alarm", "Disable alarm", "Cancel ringing"]
        alarm_stop_similar_words.extend(alarm_stop_similar_words_en)
        for word in alarm_stop_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.ALARM_STOP.value,
                "vector": EmbedModel().embed(word)
            })
            
        alarm_set_similar_words = ["定一个12点的闹钟","设置一个12点的闹钟","设置一个明天12点的闹钟", "定一个明天12点的闹钟", "明天早上12点的闹钟", "明天下午12点的闹钟", "明天晚上12点的闹钟"]
        alarm_set_similar_words_en = ["Set an alarm for 12 o'clock", "Set alarm for 12 o'clock", "Set alarm for 12 o'clock tomorrow", "Set a tomorrow's alarm for 12 o'clock", "Set alarm for tomorrow morning at 12", "Set alarm for tomorrow afternoon at 12", "Set alarm for tomorrow evening at 12"] 
        alarm_set_similar_words.extend(alarm_set_similar_words_en)
        for word in alarm_set_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.ALARM_SET.value,
                "vector": EmbedModel().embed(word)
            })
            
        alarm_cancel_similar_words = ["取消12点的闹钟", "删除12点的闹钟", "取消明天12点的闹钟", "删除明天12点的闹钟","取消明天的闹钟", "删除明天的闹钟"]
        alarm_cancel_similar_words_en = ["Cancel the 12 o'clock alarm", "Delete the 12 o'clock alarm", "Cancel tomorrow's 12 o'clock alarm", "Delete tomorrow's 12 o'clock alarm", "Cancel tomorrow's alarm", "Delete tomorrow's alarm"]
        alarm_cancel_similar_words.extend(alarm_cancel_similar_words_en)
        for word in alarm_cancel_similar_words:
            questions.append({
                "question": word,
                "category_name": QuestionType.ALARM_CANCEL.value,
                "vector": EmbedModel().embed(word)
            })

        for q in questions:
            # 创建 version 1 的 Question，使用 V1 嵌入模型
            # kb.create_question(
            #     session=session,
            #     question=q["question"],
            #     vector=embed_model_v1.embed([q["question"]], version=EmbedModel.V1)[0],  # 使用 V1 模型
            #     category_id=category_objects[q["category_name"]].id,
            #     version=1 
            # )
            # 创建 version 2 的 QuestionV2，使用 V2 嵌入模型
            kb.create_question(
                session=session,
                question=q["question"],
                vector=embed_model_v2.embed([q["question"]], version=EmbedModel.V2)[0],  # 使用 V2 模型
                category_id=category_objects[q["category_name"]].id,
                version=2
            )
        print("示例数据初始化完成 总计问题数:", len(questions))


if __name__ == '__main__':
    init_kb_data()