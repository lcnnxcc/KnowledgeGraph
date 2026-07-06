from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import config
import json
import os

class KBSImporter:
    """从知识库系统导入知识块"""

    PROCESSED_CHUNKS_FILE = os.path.join(os.path.dirname(__file__), "processed_chunks.json")

    def __init__(self):
        self.conn = None
        self._load_processed_chunks()

    def _connect(self):
        """建立PostgreSQL连接"""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(
                host=config.KBS_PG_HOST,
                port=config.KBS_PG_PORT,
                database=config.KBS_PG_DATABASE,
                user=config.KBS_PG_USER,
                password=config.KBS_PG_PASSWORD
            )

    def _load_processed_chunks(self):
        """加载已处理的chunk_id列表"""
        self.processed_chunk_ids = set()
        if os.path.exists(self.PROCESSED_CHUNKS_FILE):
            try:
                with open(self.PROCESSED_CHUNKS_FILE, "r", encoding="utf-8") as f:
                    self.processed_chunk_ids = set(json.load(f))
            except:
                self.processed_chunk_ids = set()

    def _save_processed_chunks(self):
        """保存已处理的chunk_id列表"""
        with open(self.PROCESSED_CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(self.processed_chunk_ids), f, ensure_ascii=False, indent=2)

    def mark_as_processed(self, chunk_id: str):
        """标记chunk为已处理"""
        self.processed_chunk_ids.add(chunk_id)
        self._save_processed_chunks()

    def get_unprocessed_relation_chunks(self, limit: int = 100, category: Optional[str] = None) -> List[Dict]:
        """
        获取未处理的关系型知识块
        :param limit: 最多获取数量
        :param category: 可选，按分类筛选
        :return: 知识块列表
        """
        self._connect()
        placeholders = ", ".join(["%s"] * len(config.KBS_RELATION_KNOWLEDGE_TYPES))
        params = list(config.KBS_RELATION_KNOWLEDGE_TYPES)

        # 构建查询
        query = f"""
        SELECT
            chunk_id, content, title, doc_id, category, knowledge_type,
            source, created_at, updated_at
        FROM chunks
        WHERE knowledge_type IN ({placeholders})
        AND chunk_id NOT IN ({", ".join(["%s"] * len(self.processed_chunk_ids))})
        """
        params.extend(list(self.processed_chunk_ids))

        if category:
            query += " AND category = %s"
            params.append(category)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            chunks = [dict(row) for row in cur.fetchall()]

        return chunks

    def get_all_chunks_by_doc_id(self, doc_id: str) -> List[Dict]:
        """获取指定文档的所有知识块"""
        self._connect()
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT chunk_id, content, title, doc_id, category, knowledge_type,
                       source, created_at, updated_at
                FROM chunks
                WHERE doc_id = %s
            """, (doc_id,))
            return [dict(row) for row in cur.fetchall()]

    def close(self):
        """关闭数据库连接"""
        if self.conn and not self.conn.closed:
            self.conn.close()
