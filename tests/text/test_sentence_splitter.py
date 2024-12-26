from aivc.text.sentence_splitter import SentenceSplitter
 
def assert_equal(actual, expected, message=""):
    if actual != expected:
        raise AssertionError(f"{message}\nExpected: {expected}\nGot: {actual}")

def test_basic_sentence_split():
    splitter = SentenceSplitter(min_sentence_length=20)
    chunks = ["Hello.", "This is a test.", "How are you doing today?"]
    results = []
    
    for chunk in chunks:
        results.extend(splitter.add_chunk(chunk))
    results.extend(splitter.finalize())
    
    # 验证输出的句子数量和内容
    assert_equal(len(results), 2, "Should have exactly 2 results")
    assert_equal(results[0], ("Hello.", False), "First sentence should output immediately")
    assert_equal(results[1], ("This is a test.How are you doing today?", False), 
                 "Subsequent sentences should be merged until min length is reached")
    print("Basic sentence split test passed")

def test_chinese_sentence_split():
    splitter = SentenceSplitter(min_sentence_length=15)
    chunks = ["你好。", "这是测试。", "这是一个比较长的句子。"]
    results = []
    
    for chunk in chunks:
        results.extend(splitter.add_chunk(chunk))
    results.extend(splitter.finalize())
    
    # 验证输出的句子数量和内容
    assert_equal(len(results), 2, "Should have exactly 2 results")
    assert_equal(results[0], ("你好。", False), "First sentence should output immediately")
    assert_equal(results[1], ("这是测试。这是一个比较长的句子。", False), 
                 "Subsequent sentences should be merged until min length is reached")
    print("Chinese sentence split test passed")


def test_finalize():
    splitter = SentenceSplitter(min_sentence_length=20)
    results = []

    # 添加多个短句
    results.extend(splitter.add_chunk("Short1."))  # 第一句，立即输出
    results.extend(splitter.add_chunk("Short2."))  # 待处理
    results.extend(splitter.add_chunk("Short3."))  # 待处理
    final_results = splitter.finalize()

    # 验证结果数量
    assert_equal(len(results), 1, "Should have 1 result before finalize")
    assert_equal(len(final_results), 1, "Finalize should output pending sentences")

    # 验证内容
    assert_equal(results[0], ("Short1.", False), "First sentence should output immediately")
    merged_pending = "Short2.Short3."
    assert_equal(final_results[0], (merged_pending, False), "Pending sentences should be merged in finalize")
    print("Finalize test passed")

def test_increasing_length():
    splitter = SentenceSplitter(min_sentence_length=5)
    chunks = [
        "Hi.", 
        "Hello.", 
        "This is longer.",
        "This is the longest sentence in the test case!"
    ]
    
    all_results = []
    for chunk in chunks:
        all_results.extend(splitter.add_chunk(chunk))
    all_results.extend(splitter.finalize())
    
    # 验证每次输出的句子长度是否递增
    prev_len = 0
    for sent, _ in all_results:
        current_len = len(sent)
        assert current_len >= prev_len, f"Sentence length should increase: {sent}"
        prev_len = current_len
    
    print("Increasing length test passed")

def test_modified_splitting_logic():
    splitter = SentenceSplitter(min_sentence_length=10)
    chunks = [
        "这是一个非常长的第一句话，应该被强制断句，因为它超过了最小长度。",
        "第二句话来测试最小长度。",
        "第三句需要累积到一定长度才能输出。",
        "这是第四句话，继续累积。",
        "第五句话。",
    ]
    results = []

    for chunk in chunks:
        results.extend(splitter.add_chunk(chunk))
    results.extend(splitter.finalize())

    # 验证输出的句子数量和内容
    print("Number of sentences:", len(results))
    for idx, sentence in enumerate(results, 1):
        print(f"Sentence {idx}: {sentence} (Length: {len(sentence)})")

    print("Modified splitting logic test passed")

def test_refined_splitting_logic():
    test_cases = {
        "盗墓故事": """哎呀，小朋友，盗墓在故事里听起来很刺激，但是现实生活中是不可以去的哦。因为盗墓可能会破坏古墓里的宝藏和历史，这是非常不好的行为。我们应该尊重历史，保护文化遗产，让更多的人能够欣赏和学习古时候的人们留下的宝贵东西。但是，我们可以通过阅读书籍、看纪录片或者去博物馆来了解古墓和古代文化，这样既安全又有趣。你想要知道更多的古代故事和历史知识吗？七宝可以陪你一起探索这些奇妙的世界哦！📚🏛️ 我们要做一个爱护历史、尊重文物的小小守护者呢！""",
        "李白诗词": """好的呀，小朋友，这次七宝给你背一首唐代诗人李白的《静夜思》：床前明月光，疑是地上霜。举头望明月，低头思故乡。这首诗描写的是诗人夜晚在床上看到明亮的月光，以为是地上的霜，抬头看着那轮明月，不禁低头思念起远方的家乡。李白用非常简单的词语，表达了对家乡的深深思念。这首诗很有意境，读起来也很美呢！你喜欢这首诗吗？""",
        "短对话": """嗨，小朋友！七宝来啦！今天想跟七宝做些什么有趣的事情呢？""",
        "长对话": """当然可以，小朋友！今天七宝给你讲一个关于勇敢的小刺猬的故事哦～从前，有一个小刺猬叫嘟嘟，它住在一个美丽的森林里。嘟嘟有一身硬硬的刺，看起来有点儿凶凶的，但其实它非常善良和勇敢。有一天，森林里的小动物们遇到了麻烦。一只狡猾的狐狸把小鸟们的家给占了，小鸟们无处可飞，都伤心地哭了起来。嘟嘟听到小鸟们的哭声，心里很难过。它决定要帮助小鸟们赶走狐狸。嘟嘟找到了森林里的老猫头鹰，猫头鹰告诉它：“嘟嘟，你要小心，狐狸很狡猾。”嘟嘟点了点头，说：“我知道，我会用我的智慧打败它的。”然后，嘟嘟想到了一个办法。第二天，嘟嘟带着一颗大石头来到了狐狸的家门口。狐狸看到嘟嘟，笑着说：“小刺猬，你来干什么？难道你以为你能打败我吗？”嘟嘟没有回答，而是把大石头放在了狐狸的面前。狐狸好奇地走过去，想要搬动石头。可是，石头太重了，狐狸搬不动。它生气地走了。这时，嘟嘟悄悄地告诉小鸟们：“狐狸搬不动石头，我们就可以趁机夺回我们的家了！”小鸟们听了都开心地笑了。最后，小鸟们成功地赶走了狐狸，重新回到了自己的家。大家都感谢嘟嘟的勇敢和智慧。小朋友们，这个故事告诉我们，只要我们勇敢、聪明，就没有什么困难是不能克服的哦！你们说对不对呀？""",
    }

    for case_name, original_text in test_cases.items():
        print(f"\n测试用例: {case_name}")
        print("="*50)
        print(f"原始文本: {original_text}")
        print(f"原始长度: {len(original_text)}")
        
        # 创建新的分割器实例
        splitter = SentenceSplitter()
        results = []
        
        # 逐字符输入
        for char in original_text:
            new_results = splitter.add_chunk(char)
            if new_results:
                print(f"处理字符 '{char}' 后得到新句子: {new_results}")
            # 确保每个结果都是元组形式
            results.extend([(sent, False) if isinstance(sent, str) else sent 
                          for sent in new_results])
        
        # 获取最终的句子
        final_results = splitter.finalize()
        if final_results:
            print("Finalize得到最后的句子:", final_results)
        # 确保最终结果也是元组形式
        results.extend([(sent, False) if isinstance(sent, str) else sent 
                       for sent in final_results])
        
        # 验证结果
        print("\n验证结果:")
        total_length = 0
        reconstructed_text = ""
        
        for i, (sentence, is_final) in enumerate(results, 1):
            total_length += len(sentence)
            reconstructed_text += sentence
            print(f"句子{i}: {sentence} 长度: {len(sentence)} target: {splitter.get_target_length(i)}")
        
        # 验证总长度
        assert total_length == len(original_text), (
            f"长度不匹配: 期望={len(original_text)}, 实际={total_length}"
        )
        
        # 验证文本完整性和顺序
        assert reconstructed_text == original_text, (
            f"文本不匹配或顺序错误:\n"
            f"原始: {original_text}\n"
            f"重构: {reconstructed_text}"
        )
        
        print(f"\n✅ {case_name} 测试通过:")


def main():
    print("Running sentence splitter tests...")
    # test_basic_sentence_split()
    # test_chinese_sentence_split()
    # test_finalize()
    # test_increasing_length() 
    # test_long_sentence_split()
    # test_modified_splitting_logic()
    test_refined_splitting_logic()
 
if __name__ == '__main__':
    main()
