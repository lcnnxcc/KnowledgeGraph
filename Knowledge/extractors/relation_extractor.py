import json
import re
from typing import List, Tuple, Optional
from ..models.chat_model import ChatModel

class RelationExtractor:

    def __init__(self, chat_model: Optional[ChatModel] = None):
        self.chat_model = chat_model

    def extract(self, text: str) -> List[Tuple[str, str, str]]:

        if self.chat_model:
            try:
                return self._extract_by_llm(text)
            except Exception as e:
                print(f" LLM 抽取失败: {e}，回退正则")
                return self._extract_by_regex(text)
        else:
            return self._extract_by_regex(text)

    def _extract_by_llm(self, text: str) -> List[Tuple[str, str, str]]:
        prompt = self._build_prompt(text)
        raw = self.chat_model.generate(prompt)
        return self._parse_llm_output(raw)

    def _build_prompt(self, text: str) -> str:
        return f"""请从以下文本中提取所有的（主语, 谓语, 宾语）三元组。
要求：
1. 输出格式必须为 JSON 对象，键为 "triples"，值为一个二维数组，例如：{{"triples": [["实体A", "关系", "实体B"], ["实体C", "关系", "实体D"]]}}
2. 如果没有任何关系，返回 {{"triples": []}}。
3. 不要输出任何解释性文字。
4. 文本中的“关联”、“包含”、“属于”、“支持”等连接词都要提取为关系。

文本：{text}
"""

    def _parse_llm_output(self, raw_text: str) -> List[Tuple[str, str, str]]:
        raw_text = raw_text.strip()
        # 去除 Markdown 代码块
        if raw_text.startswith("```"):
            pattern = r"```(?:json)?\s*([\s\S]*?)```"
            matches = re.findall(pattern, raw_text)
            if matches:
                raw_text = matches[0].strip()

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            # 尝试提取第一个 JSON 对象
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if not match:
                match = re.search(r'\[\s*\[.*?\]\s*\]', raw_text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except:
                    return []
            else:
                return []

        triples = []
        if isinstance(data, dict) and "triples" in data:
            triples = data["triples"]
        elif isinstance(data, list):
            triples = data
        else:
            return []

        result = []
        for item in triples:
            if isinstance(item, (list, tuple)) and len(item) == 3:
                result.append(tuple(str(x).strip() for x in item))
        return result

    def _extract_by_regex(self, text: str) -> List[Tuple[str, str, str]]:
        triples = []
        relation_patterns = [
            (r'关联', '关联'),
            (r'关系到', '关系到'),
            (r'包含', '包含'),
            (r'包括', '包含'),
            (r'含有', '包含'),
            (r'属于', '属于'),
            (r'归属于', '属于'),
            (r'支持', '支持'),
            (r'升级到', '升级到'),
        ]
        for rel_regex, rel_label in relation_patterns:
            match = re.match(r'(.*?)' + rel_regex + r'(.*)', text)
            if match:
                subject = match.group(1).strip()
                tail_part = match.group(2).strip()
                if subject and tail_part:
                    tails = re.split(r'[和与及、，]', tail_part)
                    for tail in tails:
                        tail = tail.strip()
                        if tail:
                            triples.append((subject, rel_label, tail))
                break
        return list(set(triples))