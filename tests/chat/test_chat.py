from aivc.chat.chat import Chat
import asyncio


def test_chat(question="你好"):
    result = asyncio.run(Chat().chat(
        question=question))
    print(result)

if __name__ == "__main__":
    test_chat()