import os
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from utils.chat import kimi_model

# 加载健康相关文档
def load_documents():
    # 示例：从目录加载所有txt文件
    # loader = DirectoryLoader('path/to/health_docs', glob="*.txt", loader_cls=TextLoader)
    # documents = loader.load()
    
    # 示例文档 - 实际应用中应替换为真实的健康知识文档
    sample_documents = [
        "高血压患者应该保持低盐饮食，每天盐摄入量不超过5克。",
        "糖尿病患者需要定期监测血糖，控制碳水化合物的摄入。",
        "吸烟者患心血管疾病的风险是不吸烟者的2-4倍。",
        "适量运动可以降低血压和血糖，建议每周至少150分钟中等强度运动。",
        "脑卒中的常见症状包括面部麻木、言语不清、肢体无力等。",
        "冠心病患者应避免剧烈运动，保持规律作息。",
        "饮酒应适量，男性每天不超过2个标准杯，女性不超过1个标准杯。",
        "定期体检可以早期发现慢性疾病，建议每年进行一次全面体检。"
    ]
    
    # 转换为LangChain文档格式

    documents = [Document(page_content=doc) for doc in sample_documents]
    
    return documents

# 构建向量存储
def build_vector_store():
    documents = load_documents()
    
    # 分割文档
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(
        api_key=os.getenv('KIMI_API_KEY'),
        base_url=os.getenv('KIMI_API_BASE')
    )
    
    # 创建向量存储
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    return vectorstore

# 创建RAG链
def create_rag_chain():
    vectorstore = build_vector_store()
    
    # 创建检索器
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="你是一个医疗健康专家，根据提供的健康知识和用户的健康信息，生成准确的健康建议。"),
        HumanMessage(content="健康知识：\n{context}\n\n用户健康信息：\n{question}\n\n请生成详细的健康建议：")
    ])
    
    # 创建RAG链
    rag_chain = RetrievalQA.from_chain_type(
        llm=kimi_model,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return rag_chain

# 使用RAG生成建议
def generate_health_advice(dialogue_history):
    rag_chain = create_rag_chain()
    result = rag_chain.invoke({"query": dialogue_history})
    return result["result"]