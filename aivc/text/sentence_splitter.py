import re
import jieba

class SentenceSplitter:
    def __init__(self, min_sentence_length: int = 15):
        self.min_sentence_length = min_sentence_length
        self.sentence_end_re = re.compile(
            r'(?<![(\[])(.*?)([.?!。？！，：,:]|\.{3,}|\n)(?![")\]])'
        )
        self.buffer = ''
        self.pending = []   
        self.input_sentence_number = 0   
        self.output_sentence_number = 0   

    def get_target_length(self, sentence_number: int) -> int:
        if sentence_number == 1:
            return self.min_sentence_length
        elif sentence_number in (2, 3):
            return int(self.min_sentence_length)
        else:
            return int(self.min_sentence_length * (sentence_number - 3) * 3)

    def add_chunk(self, chunk: str) -> str:
        if not chunk:
            return []

        self.buffer += chunk
        result = []

        while self.buffer:
            match = self.sentence_end_re.search(self.buffer)
            
            if not match:
                break

            sentence = (match.group(1) + match.group(2)).strip()
            self.buffer = self.buffer[match.end():]

            if not sentence.strip():
                continue

            self.input_sentence_number += 1

            # 如果有pending内容，先合并
            sentence = "".join(self.pending) + sentence 
            self.pending.clear()

            # 获取当前目标长度
            target_length = self.get_target_length(self.output_sentence_number + 1)
            # print(f"number: {self.input_sentence_number}, output sentence number: {self.output_sentence_number + 1}, target length: {target_length} sentence: {sentence} len:{len(sentence)} self.pending: {self.pending}")

            # 前1句直接输出
            if self.output_sentence_number in [0]:
                result.append(sentence)
                self.output_sentence_number += 1
                continue

            if len(sentence) > target_length*2:
                # 使用jieba分词
                words = list(jieba.cut(sentence))
                current_part = []
                current_length = 0
                found_first = False
                
                for word in words:
                    if not found_first:
                        current_length += len(word)
                        current_part.append(word)
                        
                        if current_length >= target_length:
                            # 将第一部分添加到结果
                            result.append(''.join(current_part))
                            self.output_sentence_number += 1
                            found_first = True
                            current_part = []
                    else:
                        # 剩余部分直接收集
                        current_part.append(word)
                
                # 将剩余部分合并后放入pending
                if current_part:
                    self.pending.append(''.join(current_part))
                
                continue

            # 添加到pending并检查长度
            self.pending.append(sentence)
            pending_length = sum(len(s) for s in self.pending)

            # 如果达到目标长度，输出
            if pending_length >= target_length:
                merged = ''.join(self.pending)
                result.append(merged)
                self.output_sentence_number += 1
                self.pending.clear()
            
        return result

    def finalize(self) -> str:
        result = []
        remaining = self.buffer.strip()

        # 确保所有pending内容都被输出
        if self.pending or remaining:
            if remaining:
                self.pending.append(remaining)
                self.buffer = ''

            merged = ''.join(self.pending)
            result.append(merged)
            self.output_sentence_number += 1
            self.pending.clear()

        return result