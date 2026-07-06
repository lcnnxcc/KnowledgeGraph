from typing import Dict, Optional, List
import config

class KBSAdapter:
    """知识库系统(knowledge-base-system)输出的知识块格式适配器"""

    @staticmethod
    def convert_kbs_chunk(kbs_chunk: Dict) -> Optional[Dict]:
        """
        将知识库系统的知识块转换为Knowledge模块需要的格式
        :param kbs_chunk: 知识库系统输出的原始知识块字典
        :return: 转换后的知识块，非relation类型返回None
        """
        # 检查是否是需要处理的关系型知识块
        knowledge_type = kbs_chunk.get("knowledge_type", "").lower()
        if knowledge_type not in [t.strip().lower() for t in config.KBS_RELATION_KNOWLEDGE_TYPES]:
            return None

        # 字段映射
        converted = {
            "chunk_id": kbs_chunk.get("chunk_id"),
            "content": kbs_chunk.get("content", ""),
            "knowledge_type": "relational",  # 统一为Knowledge模块使用的类型
            "title": kbs_chunk.get("title", ""),
            # 保留原系统元数据用于溯源
            "metadata": {
                "doc_id": kbs_chunk.get("doc_id"),
                "category": kbs_chunk.get("category"),
                "source": kbs_chunk.get("source"),
                "created_at": kbs_chunk.get("created_at"),
                "updated_at": kbs_chunk.get("updated_at")
            }
        }

        # 必要字段校验
        if not converted["chunk_id"] or not converted["content"].strip():
            return None

        return converted

    @staticmethod
    def batch_convert(kbs_chunks: List[Dict]) -> List[Dict]:
        """批量转换知识块"""
        converted = []
        for chunk in kbs_chunks:
            item = KBSAdapter.convert_kbs_chunk(chunk)
            if item:
                converted.append(item)
        return converted
