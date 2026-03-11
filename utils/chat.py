import os
from dotenv import load_dotenv
from openai import OpenAI
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

# 实例化每个API提供者的客户端
kimi_client = OpenAI(api_key=os.getenv('KIMI_API_KEY'), base_url=os.getenv('KIMI_API_BASE'))
qwen_client = OpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'), base_url=os.getenv('QWEN_API_BASE'))
glm_client = ZhipuAI(api_key=os.getenv('GLM_API_KEY'))


def perform_chat(client, model_name, messages, functions, temperature, max_tokens):
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        functions=functions
    )
    return response.choices[0].message.content


def kimi_chat(system_prompt, user_content, functions=None, max_tokens=5000):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    response = perform_chat(kimi_client, "moonshot-v1-8k", messages,  functions=functions, temperature=0.3, max_tokens=max_tokens)
    return response


def glm_chat(system_prompt, user_content, functions=None, max_tokens=5000):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    response = perform_chat(glm_client, "glm-4", messages, functions=functions,  temperature=0.4, max_tokens=max_tokens)
    return response


def qwen_chat(system_prompt, user_content, functions=None, max_tokens=2000):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    response = perform_chat(qwen_client, "qwen-plus", messages, functions=functions, temperature=0.80, max_tokens=max_tokens)
    return response


