import numpy as np
from neo4j import GraphDatabase
from typing import List, Tuple, Optional, Dict, Any
from Knowledge.models.embedding_model import EmbeddingClient

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str,
                 embedding_client: Optional[EmbeddingClient] = None,
                 embedding_dim: int = 2048,
                 similarity_threshold: float = 0.85):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.embedding_client = embedding_client
        self.embedding_dim = embedding_dim
        self.threshold = similarity_threshold

        # 本地缓存：存储所有实体的name和embedding，避免每次查询全量拉取
        self._entity_cache: Dict[str, List[float]] = {}
        self._cache_dirty = True  # 标记缓存是否需要更新

        # 创建向量索引（如果尚未创建）- 保留但后续不再使用
        self._create_vector_indexes()

    def close(self):
        self.driver.close()

    def _refresh_entity_cache(self):
        """刷新本地实体缓存，拉取所有Entity节点的name和embedding"""
        if not self._cache_dirty:
            return

        with self.driver.session() as session:
            result = session.run(
                "MATCH (e:Entity) RETURN e.name AS name, e.embedding AS embedding"
            )
            self._entity_cache = {}
            for record in result:
                name = record["name"]
                embedding = record["embedding"]
                if name and embedding:
                    self._entity_cache[name] = embedding
            self._cache_dirty = False
            print(f"[缓存刷新] 已加载 {len(self._entity_cache)} 个实体到本地缓存")

    def _create_vector_indexes(self):
        """创建实体向量索引（若不存在）"""
        with self.driver.session() as session:
            session.run(
                """
                CREATE VECTOR INDEX entity_embedding_idx IF NOT EXISTS
                FOR (e:Entity) ON e.embedding
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: $dim,
                        `vector.similarity_function`: 'cosine'
                    }
                }
                """,
                dim=self.embedding_dim
            ).consume()

            session.run(
                """
                CREATE VECTOR INDEX relation_embedding_idx IF NOT EXISTS
                FOR ()-[r:HAS_RELATION]-() ON r.triple_embedding
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: $dim,
                        `vector.similarity_function`: 'cosine'
                    }
                }
                """,
                dim=self.embedding_dim
            ).consume()



#余弦相似度的计算
    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        a = np.array(vec_a)
        b = np.array(vec_b)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    @staticmethod
    def normalize_vector(vec: List[float]) -> List[float]:
        """L2归一化向量，适配Neo4j余弦索引要求"""
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return [float(x / norm) for x in vec]

    def _get_or_create_entity(self, entity_name: str) -> str:
        """获取或创建实体节点，基于向量相似度去重，若无嵌入则回退精确匹配"""
        if self.embedding_client is None:
            # 无嵌入服务，直接精确匹配
            with self.driver.session() as session:
                result = session.run(
                    "MERGE (e:Entity {name: $name}) RETURN e.name AS name",
                    name=entity_name
                )
                return result.single()["name"]

        try:
            embedding = self.embedding_client.embed(entity_name)
            # L2归一化适配Neo4j余弦索引
            embedding = self.normalize_vector(embedding)
            # 加这行验证：归一化后的范数应该≈1.0
            # print(f"[调试] 实体{entity_name}向量范数：{np.linalg.norm(embedding):.3f}")
        except Exception as e:
            print(f" Embedding 计算失败: {e}，回退精确匹配")
            with self.driver.session() as session:
                result = session.run(
                    "MERGE (e:Entity {name: $name}) RETURN e.name AS name",
                    name=entity_name
                )
                return result.single()["name"]

        # 本地计算相似度查询相似实体
        self._refresh_entity_cache()
        max_similarity = 0.0
        similar_name = None

        for name, existing_embedding in self._entity_cache.items():
            sim = self.cosine_similarity(embedding, existing_embedding)
            if sim > max_similarity and sim > self.threshold:
                max_similarity = sim
                similar_name = name

        if similar_name:
            print(f"  实体 '{entity_name}' 与已有实体 '{similar_name}' 相似（得分 {max_similarity:.3f}），复用")
            return similar_name

        # 未找到相似实体，创建新实体并存储 embedding
        with self.driver.session() as session:
            print(f'当前实体："{entity_name}",不存在，需要更新')
            result = session.run(
                """
                CREATE (e:Entity {name: $name, embedding: $embedding})
                RETURN e.name AS name
                """,
                name=entity_name, embedding=embedding
            )
            # 标记缓存需要刷新
            self._cache_dirty = True
            return result.single()["name"]

    def _find_similar_relation(self, sub: str, obj: str, triple_embedding: List[float]) -> Optional[Dict[str, Any]]:
        """
        查找从 sub 到 obj 的关系中，与给定 triple_embedding 最相似的关系。
        返回关系对象及相似度，若无则返回 None。
        """
        # 查询所有从sub到obj的关系及其embedding
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (s:Entity {name: $sub})-[r:HAS_RELATION]->(o:Entity {name: $obj})
                RETURN r, r.triple_embedding AS embedding
                """,
                sub=sub, obj=obj
            )
            max_similarity = 0.0
            similar_relation = None

            for record in result:
                rel = record["r"]
                existing_embedding = record["embedding"]
                if not existing_embedding:
                    continue
                sim = self.cosine_similarity(triple_embedding, existing_embedding)
                if sim > max_similarity and sim > self.threshold:
                    max_similarity = sim
                    similar_relation = rel

            if similar_relation:
                return {"relationship": similar_relation, "score": max_similarity}
        return None

    def add_triple(self, sub: str, rel: str, obj: str, chunk_id: str):
        """存储三元组，实体和关系均基于向量相似度去重"""
        # 1. 规范化实体（去重）
        sub_norm = self._get_or_create_entity(sub)
        obj_norm = self._get_or_create_entity(obj)

        # 2. 计算三元组文本的 embedding
        triple_text = f"{sub_norm}|{rel}|{obj_norm}"
        if self.embedding_client is not None:
            try:
                triple_embedding = self.embedding_client.embed(triple_text)
                # L2归一化适配Neo4j余弦索引
                triple_embedding = self.normalize_vector(triple_embedding)
            except Exception as e:
                print(f" 三元组嵌入计算失败: {e}，回退精确匹配")
                triple_embedding = None
        else:
            triple_embedding = None

        # 3. 判断是否存在相似关系
        if triple_embedding is not None:
            similar_rel = self._find_similar_relation(sub_norm, obj_norm, triple_embedding)
            if similar_rel is not None:
                # 关系存在，更新 source_chunks
                rel_obj = similar_rel["relationship"]
                chunks = rel_obj.get("source_chunks", [])
                if chunk_id not in chunks:
                    new_chunks = chunks + [chunk_id]
                    with self.driver.session() as session:
                        session.run(
                            """
                            MATCH (s:Entity {name: $sub})-[r:HAS_RELATION {id: $rel_id}]->(o:Entity {name: $obj})
                            SET r.source_chunks = $chunks
                            """,
                            sub=sub_norm, obj=obj_norm, rel_id=rel_obj.id, chunks=new_chunks
                        )
                return

        # 4. 不存在相似关系，创建新关系（实体已存在）
        with self.driver.session() as session:
            # 先确保实体节点存在（已经存在，但以防万一）
            session.run(
                "MERGE (s:Entity {name: $sub}) MERGE (o:Entity {name: $obj})",
                sub=sub_norm, obj=obj_norm
            )
            # 创建关系
            params = {
                "sub": sub_norm,
                "rel": rel,
                "obj": obj_norm,
                "chunk_id": chunk_id,
            }
            if triple_embedding is not None:
                params["triple_embedding"] = triple_embedding
                query = """
                MATCH (s:Entity {name: $sub})
                MATCH (o:Entity {name: $obj})
                CREATE (s)-[:HAS_RELATION {type: $rel, source_chunks: [$chunk_id], triple_embedding: $triple_embedding}]->(o)
                """
            else:
                query = """
                MATCH (s:Entity {name: $sub})
                MATCH (o:Entity {name: $obj})
                CREATE (s)-[:HAS_RELATION {type: $rel, source_chunks: [$chunk_id]}]->(o)
                """
            session.run(query, **params)

    def add_triples(self, triples: List[Tuple[str, str, str]], chunk_id: str):
        for sub, rel, obj in triples:
            self.add_triple(sub, rel, obj, chunk_id)

    # ---------- 查询接口（占位） ----------
    def query(self, cypher: str, **params):
        raise NotImplementedError("查询接口尚未实现")

    def get_driver(self):
        """返回驱动实例，用于执行原生Cypher查询"""
        return self.driver