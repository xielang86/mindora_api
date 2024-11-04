from aivc.utils.message_dict import MessageDict
import asyncio

async def test_insert_and_query():
    msg_dict = MessageDict()
    await msg_dict.insert("test_key", {"message": "Hello, World!"})
    result = await msg_dict.query("test_key")
    assert result == [{"message": "Hello, World!"}], f"Expected [{'message': 'Hello, World!'}], but got {result}"
    await msg_dict.delete("test_key")

async def test_insert_multiple_and_query():
    msg_dict = MessageDict()
    await msg_dict.insert("test_key", {"message": "Hello, World!"})
    await msg_dict.insert("test_key", {"message": "Hello again!"})
    result = await msg_dict.query("test_key")
    assert result == [{"message": "Hello, World!"}, {"message": "Hello again!"}], f"Expected [{'message': 'Hello, World!'}, {'message': 'Hello again!'}], but got {result}"
    await msg_dict.delete("test_key")

async def test_delete():
    msg_dict = MessageDict()
    await msg_dict.insert("test_key", {"message": "Hello, World!"})
    await msg_dict.delete("test_key")
    result = await msg_dict.query("test_key")
    assert result == [], f"Expected [], but got {result}"

async def test_query_non_existent_key():
    msg_dict = MessageDict()
    result = await msg_dict.query("non_existent_key")
    assert result == [], f"Expected [], but got {result}"

async def test_singleton_behavior():
    msg_dict1 = MessageDict()
    msg_dict2 = MessageDict()
    await msg_dict1.insert("test_key", {"message": "Hello, Singleton!"})
    result = await msg_dict2.query("test_key")
    assert result == [{"message": "Hello, Singleton!"}], f"Expected [{'message': 'Hello, Singleton!'}], but got {result}"
    assert msg_dict1 is msg_dict2, "Expected msg_dict1 and msg_dict2 to be the same instance"
    await msg_dict1.delete("test_key")

async def run_tests():
    await test_insert_and_query()
    await test_insert_multiple_and_query()
    await test_delete()
    await test_query_non_existent_key()
    await test_singleton_behavior()
    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(run_tests())
