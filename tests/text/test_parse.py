
from aivc.text.parse import gen_text

def test_gen_text():
    template = ""
    related_data = ""
    question = "hello"
    result = gen_text(
        template=template, related_data=related_data, question=question
    )
    assert question in result

if __name__ == "__main__":
    test_gen_text()