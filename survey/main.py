from langchain_core.messages import AIMessage, HumanMessage
from utils.chat import qwen_chat, record_dialogue_history
from utils.chat import build_warmup_messages, chat_with_model, qwen_model, kimi_model
from utils.rag import generate_health_advice
from django_api import get_all_patients, get_patient_by_name, save_follow_up_record, get_doctor_by_phone
import config


user_name = "用户"
bot_name = "AI"

# 用于开启对话
def interactive_survey(model, warmup_messages, output_file, patient_name=None):
    """
    交互式随访调查
    
    Args:
        model: 使用的模型
        warmup_messages: 预热消息
        output_file: 输出文件
        patient_name: 患者姓名（可选）
    """
    messages = warmup_messages.copy()
    dialogue_history = "问卷调查开始\n"
    
    # 获取患者信息
    patient_info = None
    if patient_name:
        patient_info = get_patient_by_name(patient_name)
        if patient_info:
            # 根据患者性别生成称呼
            title = "先生" if patient_info['gender'] == "男" else "女士"
            greeting = f"您好，{patient_info['name']}{title}！"
            print(f"{bot_name}: {greeting}")
            dialogue_history += f"{bot_name}: {greeting}\n"
            
            # 添加患者信息到对话历史
            patient_info_text = f"患者信息：姓名-{patient_info['name']}，性别-{patient_info['gender']}，年龄-{patient_info['age']}岁"
            dialogue_history += f"{patient_info_text}\n"

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

        # 检查问卷是否完成
        if "生活愉快" in current_question or user_response == '结束':
            break
        
        # 再次调用模型生成下一个问题
        current_question = chat_with_model(model, messages)
        print(f"{bot_name}: {current_question}")
        dialogue_history += f"{bot_name}: {current_question}\n"
        messages.append(AIMessage(content=current_question))

        # 将对话保存在文件中
        record_dialogue_history(dialogue_history, output_file)

    return messages, dialogue_history, patient_info
    # 计算评分并生成建议
    # prompts = "请根据评分标准在每个风险因素上进行评估。将每个因素的分数相加以得出总分。根据总分，将个体归入相应的风险等级。"
    # suggestions = model_chat_func(prompts, dialogue_history)
    # print(suggestions)


if __name__ == "__main__":
    output_file = 'final.txt'
    warmup = build_warmup_messages()

    # 显示患者列表供选择
    print("=== 医疗随访系统 ===")
    patients = get_all_patients()
    
    if not patients:
        print("数据库中没有患者信息，请先在Django管理后台添加患者。")
        print("访问地址: http://127.0.0.1:8001/admin/")
        patient_name = None
    else:
        print("请选择患者进行随访：")
        for i, patient in enumerate(patients, 1):
            print(f"{i}. {patient['name']} ({patient['gender']}, {patient['age']}岁)")
        
        choice = input("请输入患者编号（输入0直接开始随访）: ")
        
        if choice == "0":
            patient_name = None
        else:
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(patients):
                    patient_name = patients[choice_idx]['name']
                    print(f"已选择患者: {patient_name}")
                else:
                    print("无效的选择，将不使用患者信息进行随访。")
                    patient_name = None
            except ValueError:
                print("无效的输入，将不使用患者信息进行随访。")
                patient_name = None

    # 使用kimi用作提问
    messages, dialogue_history, patient_info = interactive_survey(kimi_model, warmup, output_file, patient_name)

    # 使用qwen作为json格式问卷输出
    summary = qwen_chat(dialogue_history)
    record_dialogue_history(summary, 'final1.json')
    
    # 使用RAG生成基于健康知识的准确建议
    rag_advice = generate_health_advice(dialogue_history)
    print("\n=== RAG健康建议 ===")
    print(rag_advice)
    
    # 如果有患者信息，将随访记录保存到Django数据库
    if patient_info:
        print("\n=== 保存随访记录 ===")
        
        # 显示医生列表供选择
        print("请选择负责本次随访的医生：")
        for i, doctor in enumerate(config.DOCTORS, 1):
            print(f"{i}. {doctor['name']} ({doctor['department']}, {doctor['title']})")
        
        doctor_choice = input("请输入医生编号（默认为1）: ")
        
        try:
            doctor_idx = int(doctor_choice) - 1 if doctor_choice else 0
            if 0 <= doctor_idx < len(config.DOCTORS):
                doctor_phone = config.DOCTORS[doctor_idx]['phone']
                doctor_name = config.DOCTORS[doctor_idx]['name']
            else:
                print("无效的选择，使用默认医生。")
                doctor_phone = config.DEFAULT_DOCTOR['phone']
                doctor_name = config.DEFAULT_DOCTOR['name']
        except ValueError:
            print("无效的输入，使用默认医生。")
            doctor_phone = config.DEFAULT_DOCTOR['phone']
            doctor_name = config.DEFAULT_DOCTOR['name']
        
        # 构建随访内容
        follow_up_content = f"随访对话记录：\n{dialogue_history}\n\nRAG健康建议：\n{rag_advice}"
        
        # 保存随访记录
        result = save_follow_up_record(
            patient_phone=patient_info['phone'],
            doctor_phone=doctor_phone,
            content=follow_up_content,
            health_assessment=rag_advice,
            recommendations=rag_advice
        )
        
        if result:
            print(f"随访记录已保存到数据库，记录ID: {result['id']}")
            print(f"患者: {result['patient']}")
            print(f"医生: {result['doctor']}")
            print(f"随访时间: {result['record_date']}")
        else:
            print("保存随访记录失败，请检查数据库连接和数据。")
    else:
        print("\n由于没有选择患者，随访记录未保存到数据库。")