import os
from openai import OpenAI
from typing import List, Dict, Any

from volcenginesdkarkruntime import Ark


#聊天模型
class ChatModel:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        if not self.api_key:
            raise ValueError("chat_modelAPI未配置")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # self.client = Ark(base_url=self.base_url,api_key=self.api_key,)


    def generate(self, prompt: str, system_prompt: str = "你是一个专业的关系抽取助手，只输出 JSON 数组。", temperature: float = 0.1) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content