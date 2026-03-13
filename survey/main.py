import json
import re
from langchain_core.messages import AIMessage, HumanMessage
from utils.chat import kimi_chat, qwen_chat, record_dialogue_history, contains_json,is_json
from survey.prompt import PROMPT
from utils.reflection import perform_reflection
from utils.chat import build_warmup_messages, kimi_model, chat_with_model, qwen_model


user_name = "用户"
bot_name = "AI"


# 检查问卷是否结束
def is_survey_complete(boolean, dialogue_history):
    if boolean:
        required_patterns = [
            r"姓名.*?\s*(\S+)",
            r"性别.*?\s*(\S+)",
            r"年龄.*?\s*(\S+)",
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
def interactive_survey(model, warmup_messages, output_file):
    messages = warmup_messages.copy()
    dialogue_history = "问卷调查开始\n"

    # 启动调查并获取第一个问题
    current_question = chat_with_model(model, messages)
    print(f"{bot_name}: {current_question}")
    dialogue_history += f"{bot_name}: {current_question}\n"
    messages.append(AIMessage(content=current_question))


    while True:
        user_response = input(f"{user_name}: ")

        # 更新对话历史
        dialogue_history += f"{user_name}  {user_response} \n"
        messages.append(HumanMessage(content=user_response))


        # # 检索相似回答并构建新提示
        # retrieved_answers = retrieve_answers(user_response)
        # prompt = build_prompt(user_response, retrieved_answers)

        # 检查问卷是否完成
        if is_survey_complete(contains_json(dialogue_history), dialogue_history) or user_response == '结束':
            break
        
        # 再次调用模型生成下一个问题
        current_question = chat_with_model(model, messages)
        print(f"{bot_name}: {current_question}")
        dialogue_history += f"{bot_name}: {current_question}\n"
        messages.append(AIMessage(content=current_question))

        # 将对话保存在文件中
        record_dialogue_history(dialogue_history, output_file)

    return messages, dialogue_history
    # 计算评分并生成建议
    # prompts = "请根据评分标准在每个风险因素上进行评估。将每个因素的分数相加以得出总分。根据总分，将个体归入相应的风险等级。"
    # suggestions = model_chat_func(prompts, dialogue_history)
    # print(suggestions)


if __name__ == "__main__":
    output_file = 'final.txt'
    warmup = build_warmup_messages()

    # 使用kimi用作提问
    messages, dialogue_history = interactive_survey(kimi_model, warmup, output_file)

    # 使用qwen作为json格式问卷输出
    summary_prompt = "请将以下对话记录转换为 JSON 格式：\n" + dialogue_history
    summary = chat_with_model(qwen_model, [HumanMessage(content=summary_prompt)])
    record_dialogue_history(summary, 'final1.json')

    
    # 在最终生成建议之前应用反思机制
    final_output = perform_reflection(dialogue_history)
    print(final_output)