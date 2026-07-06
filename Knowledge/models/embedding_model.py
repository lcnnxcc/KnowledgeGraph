import requests
from typing import List



# 向量模型
# class EmbeddingClient:
#     def __init__(self, base_url: str = None, model: str = None):
#         self.base_url = base_url
#         self.model = model
#         self.endpoint = f"{self.base_url}/api/embeddings"
#
#     def embed(self, text: str) -> List[float]:
#         response = requests.post(
#             self.endpoint,
#             json={"model": self.model, "prompt": text}
#         )
#         if response.status_code == 200:
#             data = response.json()
#             return data.get("embedding", [])
#         else:
#             raise Exception(f"Ollama Embedding 请求失败: {response.text}")


import os
from openai import OpenAI
from typing import List


class EmbeddingClient:
    def __init__(self, api_key:str = None, base_url: str = None, model: str = None):
        """
        OpenAI Embedding 客户端
        :param api_key: OpenAI API Key（或兼容服务的 Key）
        :param base_url: 自定义端点（可选，如代理地址）
        :param model: 模型名称，如 text-embedding-ada-002 或 text-embedding-3-small
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("OpenAI API Key 未设置，请传入 api_key 或设置环境变量 OPENAI_API_KEY")
        self.base_url = base_url
        self.model = model

        # 复用 OpenAI 客户端（与 chat_model 一致）
        self.client = OpenAI(base_url=self.base_url,api_key=self.api_key)

    def embed(self, text: str) -> List[float]:
        """
        将文本转为向量
        :param text: 输入文本
        :return: 浮点数列表（向量）
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            # 返回第一个结果（通常 input 为单个字符串时 data 只有一项）
            embedding = response.data[0].embedding
            # print('----------测试向量是否归一化----------')
            # import numpy as np
            # # 假设 vec 是你的嵌入向量
            # norm = np.linalg.norm(embedding)
            # print(norm)  # 应该 ≈ 11024.0
            print(f"向量实际维度：{len(embedding)}")
            return embedding
        except Exception as e:
            raise Exception(f"OpenAI Embedding 调用失败: {e}")



# import os
# from typing import List
# from volcenginesdkarkruntime import Ark
#
# class EmbeddingClient:
#     def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
#         """
#         火山引擎 Embedding 客户端（基于 ArkRuntime）
#         :param api_key: 火山引擎 API Key（控制台获取，非 AccessKey）
#         :param base_url: 服务端点，默认北京地域
#         :param model: 模型接入点 ID（如 ep-xxxxx）
#         """
#         self.api_key = api_key or os.getenv("VOLC_ACCESSKEY")
#         if not self.api_key:
#             raise ValueError("火山引擎 API Key 未设置，请传入 api_key 或设置环境变量 VOLC_ACCESSKEY")
#         self.base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"
#         self.model = model or os.getenv("VOLC_EMBEDDING_MODEL")
#         if not self.model:
#             raise ValueError("火山引擎 Embedding 模型 ID 未设置，请传入 model 或设置环境变量 VOLC_EMBEDDING_MODEL")
#
#         # 初始化 ArkRuntime 客户端（与 OpenAI 兼容）
#         self.client = Ark(
#             api_key=self.api_key,
#             base_url=self.base_url
#         )
#
#     def embed(self, text: str) -> List[float]:
#         """
#         将文本转为向量
#         :param text: 输入文本
#         :return: 浮点数列表（向量）
#         """
#         try:
#             response = self.client.embeddings.create(
#                 model=self.model,
#                 input=text
#             )
#             # 返回格式：response.data[0].embedding
#             embedding = response.data[0].embedding
#             return embedding
#         except Exception as e:
#             raise Exception(f"火山引擎 Embedding 调用失败: {e}")