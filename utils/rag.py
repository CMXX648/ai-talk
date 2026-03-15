import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from utils.chat import kimi_model

# 加载健康相关文档
def load_documents():
    # 示例文档
    sample_documents = [
    "高血压患者自测血压建议每天固定时段，测量前静坐5-10分钟。",
    "高血压患者除低盐外，还应减少腌制食品、加工肉类的摄入。",
    "糖尿病患者需控制空腹血糖在3.9-7.0mmol/L，餐后2小时血糖<10.0mmol/L。",
    "糖尿病患者应规律监测糖化血红蛋白，建议每3个月检测一次。",
    "糖尿病患者需做好足部护理，每天检查足部，避免外伤和感染。",
    "血脂异常患者需减少高胆固醇、高甘油三酯食物，如动物内脏、油炸食品。",
    "高胆固醇血症患者服用他汀类药物，需定期检查肝功能和肌酸激酶。",
    "冠心病患者规律服用抗栓药物，不可擅自停药或调整剂量。",
    "冠心病患者出现胸闷、胸痛时，应立即停止活动并休息，及时就医。",
    "脑卒中恢复期患者应坚持康复训练，建议在发病后3-6个月黄金期持续进行。",
    "短暂性脑缺血发作(TIA)患者需及时治疗，降低脑梗死发生风险。",
    "房颤患者服用抗凝药物，需定期监测凝血功能，避免出血风险。",
    "吸烟者戒烟后24小时内，心血管疾病风险即可开始降低。",
    "戒烟困难者可借助戒烟药物、戒烟门诊等专业方式辅助戒烟。",
    "成年男性腰围应控制在90cm以下，女性腰围控制在85cm以下，减少中心性肥胖。",
    "成年人BMI应维持在18.5-23.9kg/m²，超重或肥胖者需逐步减重。",
    "中等强度运动包括快走、太极拳、慢跑、游泳，每次运动不少于30分钟。",
    "慢病患者运动前应评估身体状况，避免空腹或餐后立即运动。",
    "慢病患者需规律作息，避免熬夜，每天保证7-8小时睡眠时间。",
    "高盐饮食会使血压升高，高血压患者烹饪建议用蒸、煮、炖，少用红烧、酱卤。",
    "糖尿病患者应均衡饮食，主食可替换为杂粮、杂豆，增加膳食纤维摄入。",
    "血脂异常患者可适当增加深海鱼、坚果等富含不饱和脂肪酸的食物。",
    "脑卒中患者需控制基础病，将血压、血糖、血脂控制在达标范围。",
    "慢病患者遵循医嘱用药，漏服药物不可擅自加倍服用。",
    "饮酒会升高血压、血糖，高血压和糖尿病患者建议尽量不饮酒。",
    "规律饮水有助于代谢，成年人每天建议饮用1500-2000ml白开水。",
    "情绪波动会诱发血压骤升，慢病患者应保持心态平和，避免过度焦虑。",
    "有脑卒中家族史者，应更早开始控制血压、血糖、血脂，定期做脑血管检查。",
    "冠心病患者应减少浓茶、咖啡、辛辣刺激性食物的摄入。",
    "康复治疗需在专业医生指导下进行，避免自行训练导致二次损伤。",
    "家庭自测血压的正常值为收缩压<135mmHg，舒张压<85mmHg。",
    "高血脂患者若饮食和运动干预无效，需及时启动药物治疗。",
    "糖尿病患者合并高血压时，血压应控制在130/80mmHg以下。",
    "长期久坐会增加慢病风险，建议每坐1小时起身活动5-10分钟。",
    "慢病患者应定期复查，高血压、糖尿病患者建议每1-3个月复查一次。"
]
    
    # 转换为LangChain文档格式
    documents = [Document(page_content=doc) for doc in sample_documents]
    
    return documents

# 构建向量存储
def build_vector_store():
    documents = load_documents()
    
    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(
        api_key=os.getenv('KIMI_API_KEY'),
        base_url=os.getenv('KIMI_API_BASE')
    )
    
    # 创建向量存储
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    return vectorstore

# 使用RAG生成建议
def generate_health_advice(dialogue_history):
    try:
        # 构建向量存储
        vectorstore = build_vector_store()
        
        # 检索相关文档
        docs = vectorstore.similarity_search(dialogue_history, k=3)
        context = "\n".join([doc.page_content for doc in docs])
        
        # 创建提示
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="你是一个医疗健康专家，根据提供的健康知识和用户的健康信息，生成准确的健康建议。"),
            HumanMessage(content=f"健康知识：\n{context}\n\n用户健康信息: \n{dialogue_history}\n\n请生成详细的健康建议:")
        ])
        
        # 生成建议
        messages = prompt.format_messages()
        response = kimi_model.invoke(messages)
        return response.content
    except Exception as e:
        print(f"生成健康建议时出错: {e}")
        # 出错时返回基本建议
        return "根据您的健康信息，建议您保持健康的生活方式，定期体检，并遵循医生的建议。"