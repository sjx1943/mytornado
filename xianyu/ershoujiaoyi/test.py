#!/usr/bin/env python
# -*- coding: utf-8 -*-

from langchain.llms import AI21
from langchain.chains.qa import load_qa_chain

# 初始化LLM
llm = AI21()

# 创建QA链
chain = load_qa_chain(llm, chain_type="stuff")


# 定义智能体的输入输出
def smart_agent(query):
    # 使用索引进行搜索
    results = query_index(query)

    # 如果找到相关结果，则返回结果
    if results:
        return results
    else:
        # 否则，使用LLM生成回复
        return chain({"question": query, "context": ""})


# 测试智能体
query = "搜索关于AI的信息"
print(smart_agent(query))


