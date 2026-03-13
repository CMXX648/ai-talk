import json
import re
from langchain_core.messages import SystemMessage, HumanMessage
from utils.chat import kimi_chat, qwen_chat, record_dialogue_history, contains_json,is_json
from survey.prompt import PROMPT
from utils.reflection import perform_reflection

user_name = "用户"
bot_name = "AI"


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
            r"糖尿病.*?\s*(\S+)"]
        for pattern in required_patterns:
            if not re.search(pattern, dialogue_history):
                return False
        return True
    else:
        return False


# 用于开启对话
def interactive_survey(model_chat_func, warmup_messages, output_file):
    messages = warmup_messages.copy()
    dialogue_history = "问卷调查开始\n"

    # 启动调查并获取第一个问题
    current_question = model_chat_func(initial_prompt, dialogue_history)

    while True:
        question_w = (f"{bot_name}: {current_question.split("  ")[0]} \n")
        print(question_w)
        user_response = input(f"{user_name}: ")

        # 更新对话历史
        dialogue_history += f"{question_w}  {user_response} \n"

        # # 检索相似回答并构建新提示
        # retrieved_answers = retrieve_answers(user_response)
        # prompt = build_prompt(user_response, retrieved_answers)

        # 检查问卷是否完成
        # if is_survey_complete(contains_json(dialogue_history), dialogue_history) or user_response == '结束':
        #     break
        if user_response == '结束':
            break

        # 再次调用模型生成下一个问题
        current_question = model_chat_func(initial_prompt, dialogue_history)

        # 将对话保存在文件中
        record_dialogue_history(dialogue_history, output_file)

    # 计算评分并生成建议
    prompts = "请根据评分标准在每个风险因素上进行评估。将每个因素的分数相加以得出总分。根据总分，将个体归入相应的风险等级。"
    suggestions = model_chat_func(prompts, dialogue_history)
    print(suggestions)


if __name__ == "__main__":
    file_path = 'Q.txt'
    output_file = 'final.txt'
    initial_prompt1 = f"按照以下要求来实现本次对话。\n \"\"\"{PROMPT}\"\"\"。"
    initial_prompt = f"请牢记你当前扮演的角色及要求"

    # 使用kimi用作提问
    interactive_survey(kimi_chat, initial_prompt, output_file)

    # 使用qwen作为json格式问卷输出
    with open(output_file, 'r', encoding='utf-8') as file:
        dialogue_history = file.read()
    # 为qwen_chat提供system_prompt参数
    qwen_system_prompt = "请将对话历史转换为JSON格式"
    record = qwen_chat(qwen_system_prompt, dialogue_history)
    record_dialogue_history(record, 'final1.json')

    
    # 在最终生成建议之前应用反思机制
    final_output = perform_reflection(dialogue_history)
    print(final_output)