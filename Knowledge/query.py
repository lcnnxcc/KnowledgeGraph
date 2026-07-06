import sys
from typing import List, Tuple, Set, Optional
from Knowledge import config
from Knowledge.models import embedding_model
from Knowledge.storage import neo4j_store

class QueryEngine:
    """交互式知识图谱查询引擎，支持向量语义检索和多跳扩展"""
    def __init__(self, neo4j_client: neo4j_store.Neo4jClient, embedding_client: embedding_model.EmbeddingClient, similarity_threshold: float = 0.8):
        self.neo4j = neo4j_client
        self.embedder = embedding_client
        self.threshold = similarity_threshold

    def _embed(self, text: str) -> List[float]:
        """获取文本向量，若失败则抛出异常"""
        return self.embedder.embed(text)

    def _vector_search_entity(self, keyword: str) -> Optional[Tuple[str, float]]:
        """
        使用向量索引查询与关键词最相似的实体（相似度 > threshold）
        返回 (实体名称, 相似度得分) 或 None
        """
        try:
            embedding = self._embed(keyword)
            # L2归一化适配Neo4j余弦索引（与存储时保持一致）
            import numpy as np
            norm = np.linalg.norm(embedding)
            if norm != 0:
                embedding = [float(x / norm) for x in embedding]
        except Exception as e:
            print(f" 嵌入计算失败: {e}")
            return None

        with self.neo4j.get_driver().session() as session:
            result = session.run(
                """
                CALL db.index.vector.queryNodes('entity_embedding_idx', 1, $embedding)
                YIELD node, score
                WHERE score > $threshold
                RETURN node.name AS name, score
                """,
                embedding=embedding,
                threshold=self.threshold
            )
            record = result.single()
            if record:
                return record["name"], record["score"]
        return None

    def _expand_subgraph(self, entity_name: str, depth: int) -> Tuple[Set[Tuple[int, str, bool]], List[Tuple[int, str, str, list, int, int]]]:
        """
        从指定实体出发，扩展 depth 跳以内的子图
        返回 (节点集合, 关系列表)
        节点集合: (node_id, name, has_embedding)
        关系列表: (rel_id, rel_type, label, source_chunks, start_node_id, end_node_id)
        """
        with self.neo4j.get_driver().session() as session:
            query = f"""
            MATCH path = (start:Entity {{name: $name}})-[r:HAS_RELATION*1..{depth}]-(connected)
            RETURN start, relationships(path) AS rels, nodes(path) AS all_nodes
            """
            result = session.run(query, name=entity_name)

            nodes = set()
            rels = []
            for record in result:
                # 记录所有节点
                for node in record["all_nodes"]:
                    # 判断是否有 embedding 属性（简单检查）
                    has_emb = node.get("embedding") is not None
                    nodes.add((node.element_id, node.get("name", ""), has_emb))
                # 记录所有关系
                for rel in record["rels"]:
                    rels.append((
                        rel.element_id,
                        rel.type,
                        rel.get("type", ""),          # 实际关系标签存储在 type 属性上
                        rel.get("source_chunks", []),
                        rel.start_node.element_id,
                        rel.end_node.element_id
                    ))
            return nodes, rels

    def _format_result(self, nodes: Set[Tuple[int, str, bool]], rels: List[Tuple[int, str, str, list, int, int]]):
        """格式化打印查询结果"""
        if not nodes and not rels:
            print("未找到任何关联节点或关系。")
            return

        print(f"\n 查询结果：")
        print(f"节点数: {len(nodes)}，关系数: {len(rels)}")

        # 构建节点ID到名称的映射
        node_map = {nid: name for nid, name, _ in nodes}

        print("\n 节点列表：")
        for node_id, name, has_emb in sorted(nodes, key=lambda x: x[0]):
            emb_flag = "" if has_emb else " "
            print(f"  {emb_flag} {name} (ID: {node_id})")

        print("\n 关系列表：")
        for rel_id, rel_type, label, chunks, start_id, end_id in rels:
            start_name = node_map.get(start_id, "未知")
            end_name = node_map.get(end_id, "未知")
            chunks_str = ", ".join(chunks) if chunks else "无"
            print(f"  {start_name} --[{label}]--> {end_name}  (来源: {chunks_str})")

    def interactive_query(self):
        """交互式循环查询"""
        print(" 知识图谱查询引擎启动")
        print(f"阈值设定: {self.threshold}")
        print("输入 'exit' 退出程序\n")

        while True:
            keyword = input("请输入关键词（实体名称/描述）：").strip()
            if keyword.lower() in ("exit", "quit", "q"):
                print("退出查询。")
                break
            if not keyword:
                continue

            depth_input = input("请输入查询层级（跳数，默认1）：").strip()
            try:
                depth = int(depth_input) if depth_input else 1
                if depth < 1:
                    depth = 1
            except ValueError:
                print("层级必须是整数，使用默认值1。")
                depth = 1

            # 向量检索最相似实体
            result = self._vector_search_entity(keyword)
            if not result:
                print(f"️ 未找到相似度高于 {self.threshold} 的实体，请换一个关键词。\n")
                continue

            entity_name, score = result
            print(f" 匹配到实体: '{entity_name}' (相似度: {score:.3f})")

            # 扩展子图
            nodes, rels = self._expand_subgraph(entity_name, depth)
            self._format_result(nodes, rels)
            print("\n" + "-" * 60 + "\n")

# ---------- 独立运行入口 ----------
if __name__ == "__main__":
    # 加载配置

    # 初始化客户端
    embedding_client = embedding_model.EmbeddingClient(
        base_url=config.VOL_BASE_URL,
        model=config.VOL_EMBED_MODEL,
        # api_key=config.VOL_API_KEY
    )
    neo4j_client = neo4j_store.Neo4jClient(
        uri=config.NEO4J_URI,
        user=config.NEO4J_USER,
        password=config.NEO4J_PASSWORD,
        embedding_client=embedding_client,   # 仍然传入，用于存储时的去重，但查询中我们仅使用embedder
        embedding_dim=config.EMBEDDING_DIM,
        similarity_threshold=0.85
    )

    # 创建查询引擎
    engine = QueryEngine(neo4j_client, embedding_client, similarity_threshold=0.85)

    # 启动交互
    engine.interactive_query()

    # 关闭连接
    neo4j_client.close()