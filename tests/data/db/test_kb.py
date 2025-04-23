from aivc.chat.router import Router
from aivc.common.route import Route
from aivc.common.query_analyze import QueryAnalyzer
from aivc.common.task_class import QuestionType


async def test_search_kb_case1():
    question_dict = {
       "今天上海的天气怎么样？七宝今天上海的天气怎么样？": QuestionType.WEATHER.value,
       "那我手里是什么？": QuestionType.TAKE_PHOTO.value,
        "你是谁？": QuestionType.ABOUT.value,
        "7号。": None,
        "我是谁？": None,
        #我不是很开心啊！
        #今天有点累，今
        "我不是很开心啊！": QuestionType.SLEEP_ASSISTANT.value,
        # 新增测试例子
        "把声音调大一点": QuestionType.VOLUME_MAIN_UP.value,
        "调低背景音量": QuestionType.VOLUME_BACKGROUND_DOWN.value,
        "灯光变亮": QuestionType.LIGHT_BRIGHTNESS_UP.value,
        "把灯变成红色": QuestionType.LIGHT_COLOR_RED.value,
        "开启香薰": QuestionType.FRAGRANCE_ON.value,
        # 新增灯光模式测试例子
        "打开流光溢彩效果": QuestionType.LIGHT_MODE_FLOWING_COLOR.value,
        "切换到星空模式": QuestionType.LIGHT_MODE_STARRY_SKY.value,
        "让灯光显示水母效果": QuestionType.LIGHT_MODE_JELLYFISH.value,
    }
    for question, category_name in question_dict.items():
        result = await Router(
            route = Route(
                query_analyzer=QueryAnalyzer(
                    question=question
                )
            )
        ).search_kb()
        print(f"question: {question}, result: {result}")
        if category_name is None:
            assert result is None
            continue
        if result:
            assert result.category_name == category_name

async def test_control_features():
    """测试控制类功能（音量、灯光、香薰、系统睡眠）"""
    # 音量控制测试
    volume_control_tests = {
        "把声音调大一点": QuestionType.VOLUME_MAIN_UP.value,
        "声音调小": QuestionType.VOLUME_MAIN_DOWN.value, 
        "静音": QuestionType.VOLUME_MUTE.value,
        "把语音音量调高": QuestionType.VOLUME_VOICE_UP.value,
        "语音声音小一点": QuestionType.VOLUME_VOICE_DOWN.value,
        "语音静音": QuestionType.VOLUME_VOICE_MUTE.value,
        "背景音乐声音调大": QuestionType.VOLUME_BACKGROUND_UP.value,
        "背景声音小一点": QuestionType.VOLUME_BACKGROUND_DOWN.value,
        "背景音乐静音": QuestionType.VOLUME_BACKGROUND_MUTE.value,
        "调高音乐音量": QuestionType.VOLUME_MUSIC_UP.value,
        "调小音乐音量": QuestionType.VOLUME_MUSIC_DOWN.value,
        "音乐静音": QuestionType.VOLUME_MUSIC_MUTE.value,
    }
    
    # 灯光控制测试
    light_control_tests = {
        "把灯光调亮一点": QuestionType.LIGHT_BRIGHTNESS_UP.value,
        "灯光暗一点": QuestionType.LIGHT_BRIGHTNESS_DOWN.value,
        "把灯变成绿色": QuestionType.LIGHT_COLOR_GREEN.value,
        "我想要蓝色灯光": QuestionType.LIGHT_COLOR_BLUE.value,
        "把灯变成紫色": QuestionType.LIGHT_COLOR_PURPLE.value,
        "黄色灯光": QuestionType.LIGHT_COLOR_YELLOW.value,
        "白光模式": QuestionType.LIGHT_COLOR_WHITE.value,
        "开灯": QuestionType.LIGHT_STATE_ON.value,
        "关闭灯光": QuestionType.LIGHT_STATE_OFF.value,
        # 新增灯光模式测试
        "切换到流光溢彩模式": QuestionType.LIGHT_MODE_FLOWING_COLOR.value,
        "打开星空灯光": QuestionType.LIGHT_MODE_STARRY_SKY.value,
        "切换到水母灯光效果": QuestionType.LIGHT_MODE_JELLYFISH.value,
        "开启火焰模式": QuestionType.LIGHT_MODE_FLAME.value,
        "显示海浪灯光效果": QuestionType.LIGHT_MODE_WAVES.value,
        "随机切换灯光模式": QuestionType.LIGHT_MODE_RANDOM.value,
    }
    
    # 香薰控制测试
    fragrance_control_tests = {
        "开启香薰": QuestionType.FRAGRANCE_ON.value,
        "关掉香薰": QuestionType.FRAGRANCE_OFF.value,
    }
    
    # 系统控制测试
    system_control_tests = {
        "系统睡眠": QuestionType.SYSTEM_SLEEP.value,
        "进入休眠模式": QuestionType.SYSTEM_SLEEP.value,
    }
    
    # 合并所有测试用例
    all_tests = {}
    all_tests.update(volume_control_tests)
    all_tests.update(light_control_tests)
    all_tests.update(fragrance_control_tests)
    all_tests.update(system_control_tests)
    
    for question, category_name in all_tests.items():
        result = await Router(
            route = Route(
                query_analyzer=QueryAnalyzer(
                    question=question
                )
            )
        ).search_kb()
        print(f"Control test - question: {question}, result: {result}")
        if result:
            assert result.category_name == category_name
        else:
            print(f"Warning: No result for question '{question}', expected '{category_name}'")

def test_get_threshold_by_category_name():
    print(QuestionType.get_threshold_by_category_name("sleep_assistant"))

def test_get_min_threshold():
    print(QuestionType.get_min_threshold())

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_search_kb_case1())
    asyncio.run(test_control_features())
    test_get_threshold_by_category_name()
    test_get_min_threshold()

