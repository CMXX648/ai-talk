import json
import re
from utils.chat import kimi_chat, glm_chat, qwen_chat
from survey.prompt import PROMPT

from external_retrieval import retrieve_answers, build_prompt  # 假设这两个函数被存储在 external_retrieval.py 中
from utils.reflection import perform_reflection  # 假设 perform_reflection 被存储在 reflection.py 中

functions = [
    {
        'name_for_human': '健康风险评估与建议',
        'name_for_model': 'evaluate_and_suggest',

        'description_for_model': '评估用户的健康风险并提供相应建议。' +
                                 ' Format the arguments as a JSON object.',
        'parameters': [{
            'name': 'dialogue_history',
            'description': '包含用户健康相关信息的对话历史记录',
            'required': True,
            'schema': {
                'type': 'object'
            },
        }],
    },
]


# 历史聊天文本切割为json
def contains_json(text):
    json_pattern = re.compile(r'[{].*?[}]', re.DOTALL)
    possible_jsons = json_pattern.findall(text)
    for possible_json in possible_jsons:
        if is_json(possible_json):
            return True
    return False


def is_json(text):
    try:
        json_object = json.loads(text)
    except ValueError as e:
        return False
    return True


# 用于保存对话记录
def record_dialogue_history(dialogue_history, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(dialogue_history)
    except Exception as e:
        print(f"保存对话历史时出错: {e}")


# 检查问卷是否结束
def is_survey_complete(boolean, dialogue_history):
    if boolean:
        required_patterns = [
            r"姓名.*?\s*(\S+)",
            r"性别.*?\s*(\S+)",
            r"年龄.*?\s*(\S+)",
            r"民族.*?\s*(\S+)",
            r"身份证号.*?\s*(\S+)",
            r"户籍地址.*?\s*(\S+)",
            r"联系手机.*?\s*(\S+)",
            r"主要联系人姓名.*?\s*(\S+)",
            r"与本人关系.*?\s*(\S+)",
            r"联系人手机.*?\s*(\S+)",
            r"症状变化.*?\s*(\S+)",
            r"新症状.*?\s*(\S+)",
            r"医嘱.*?\s*(\S+)",
            r"是否吸烟.*?\s*(\S+)",
            r"饮酒情况.*?\s*(\S+)",
            r"脑卒中.*?\s*(\S+)",
            r"冠心病.*?\s*(\S+)",
            r"高血压.*?\s*(\S+)",
            r"糖尿病.*?\s*(\S+)"
        ]
        for pattern in required_patterns:
            if not re.search(pattern, dialogue_history):
                return False
        return True
    else:
        return False


# 用于开启对话
def interactive_survey(model_chat_func, questionnaire_text, initial_prompt, output_file):
    dialogue_history = "问卷调查开始"
    prompt = f"{initial_prompt} {questionnaire_text}"  # 结合初次提示和问卷内容

    # 启动调查并获取第一个问题
    current_question = model_chat_func(prompt, dialogue_history)

    while current_question.strip() != "":
        question_w = current_question.split("  ")[0]
        print("Question:", question_w)
        user_response = input("Your  ")

        # 更新对话历史
        dialogue_history += f"\n {question_w}  {user_response} \n"

        # 检索相似回答并构建新提示
        retrieved_answers = retrieve_answers(user_response)
        prompt = build_prompt(user_response, retrieved_answers)

        # 检查问卷是否完成
        if is_survey_complete(contains_json(dialogue_history), dialogue_history) or user_response == '结束':
            break

        # 再次调用模型生成下一个问题
        current_question = model_chat_func(prompt, dialogue_history)

        # 将对话保存在文件中
        record_dialogue_history(dialogue_history, output_file)

    # 计算评分并生成建议
    prompts = "请根据评分标准在每个风险因素上进行评估。将每个因素的分数相加以得出总分。根据总分，将个体归入相应的风险等级。"
    suggestions = model_chat_func(prompts, dialogue_history, functions)
    print(suggestions)


if __name__ == "__main__":
    file_path = 'Q.txt'
    output_file = 'final.txt'
    initial_prompt = f"按照以下要求来实现本次对话。\n \"\"\"{PROMPT}\"\"\"。"

    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        questionnaire_text = f"这是问卷内容：\n \"\"\"{file_content}\"\"\""

    interactive_survey(qwen_chat, questionnaire_text, initial_prompt, output_file)

    # 在最终生成建议之前应用反思机制
    with open(output_file, 'r', encoding='utf-8') as file:
        dialogue_history = file.read()

    final_output = perform_reflection(dialogue_history)
    print(final_output)