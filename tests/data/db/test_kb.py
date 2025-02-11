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
        "帮我助眠吧": QuestionType.SLEEP_ASSISTANT.value,
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

def test_get_threshold_by_category_name():
    print(QuestionType.get_threshold_by_category_name("sleep_assistant"))

def test_get_min_threshold():
    print(QuestionType.get_min_threshold())

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_search_kb_case1())
    test_get_threshold_by_category_name()
    test_get_min_threshold()

