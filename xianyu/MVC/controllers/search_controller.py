# import sys
# import os
#
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from itertools import product
from typing import Optional, Awaitable

from sqlalchemy.orm import sessionmaker, scoped_session
from base.base import engine
import tornado
from models.items import Item
import urllib.parse
import tornado.web
import logging
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain_community.llms import HuggingFacePipeline
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings  # 修改后的导入
from langchain_community.vectorstores import FAISS  # 修改后的导入
import torch
import time
from transformers import pipeline

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def validate_absolute_path(self, root, absolute_path):
        absolute_path = urllib.parse.unquote(absolute_path)
        return super().validate_absolute_path(root, absolute_path)

Session = sessionmaker(bind=engine)
model_name = "deepseek-ai/DeepSeek-Coder-1.3B-instruct"  # 替换为 DeepSeek 的模型名称
max_retries = 5
retry_delay = 1  # initial delay in seconds

for attempt in range(max_retries):
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
            retry_delay *= 2  # exponential backoff
        else:
            raise e

pipeline = pipeline(
    "question-answering",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

llm = HuggingFacePipeline(pipeline=pipeline)

chain = load_qa_with_sources_chain(llm, chain_type="stuff")



def ai_query(query, context):
    if not context:
        return "未找到相关上下文"

    try:
        docs = [Document(page_content=c) for c in context]
        result = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
        return result.get("output_text", "未找到答案")
    except Exception as e:
        logging.error(f"AI Query failed: {e}")
        return "AI Query failed"


# 1. 加载数据库数据
def load_data_from_db():
    session = Session()
    try:
        items = session.query(Item).all()
        data = [f"{item.name}的年龄是{item.age}" for item in items]  # 创建文本数据
        return data
    except Exception as e:
        logging.error(f"Error loading data from database: {e}")
        return []
    finally:
        session.close()

# 2. 初始化模型
model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# 3. 创建索引
def create_index():
    data = load_data_from_db()
    documents = [Document(page_content=d) for d in data]
    db = FAISS.from_documents(documents, embeddings)
    return db

db = create_index()

class AIQueryHandler(tornado.web.RequestHandler):
    async def get(self):
        query = self.get_argument('query')
        session = Session()
        try:
            # Fuzzy search
            items = session.query(Item).filter(Item.name.like(f"%{query}%")).all()
            if items:
                # 构建文档上下文
                context = [f"{item.name}的年龄是{item.age}" for item in items]
                answer = ai_query(query, context)

                self.write({"result": answer})
            else:
                self.write({"result": "未找到相关结果"})
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            self.write({"error": str(e)})
        finally:
            session.close()



class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("ai_query.html")  # 渲染 AI 查询页面