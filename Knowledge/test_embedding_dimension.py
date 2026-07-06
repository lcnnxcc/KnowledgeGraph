# import numpy as np
# from volcenginesdkarkruntime import Ark
#
# client = Ark(api_key="ark-140d7c0e-0647-4ffa-aab8-8b9d09764caa-6fee4",
#              base_url="https://ark.cn-beijing.volces.com/api/v3")
#
# words = ["用户积分", "订单状态", "待支付", "已完成"]
# embeddings = {}
# for w in words:
#     emb = client.embeddings.create(model="doubao-embedding-large-text-250515", input=w).data[0].embedding
#     # 归一化
#     emb = np.array(emb) / np.linalg.norm(emb)
#     embeddings[w] = emb
#
# # 计算两两相似度
# for w1 in words:
#     for w2 in words:
#         if w1 < w2:
#             sim = np.dot(embeddings[w1], embeddings[w2])
#             print(f"{w1} ↔ {w2} : {sim:.3f}")
import numpy as np
from neo4j import GraphDatabase
from volcenginesdkarkruntime import Ark

# 初始化客户端
volc_client = Ark(
    api_key="ark-140d7c0e-0647-4ffa-aab8-8b9d09764caa-6fee4",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))


def normalize(vec):
    norm = np.linalg.norm(vec)
    return vec / norm if norm != 0 else vec


# 1. 计算两个词的向量并归一化
word1 = "用户积分"
word2 = "订单状态"

emb1 = volc_client.embeddings.create(model="doubao-embedding-large-text-250515", input=word1).data[0].embedding
emb2 = volc_client.embeddings.create(model="doubao-embedding-large-text-250515", input=word2).data[0].embedding

emb1_norm = normalize(emb1)
emb2_norm = normalize(emb2)

# 2. 本地计算余弦相似度
local_sim = float(np.dot(emb1_norm, emb2_norm))
print(f"✅ 本地计算相似度：{local_sim:.4f}")
print(f"✅ 向量1范数：{np.linalg.norm(emb1_norm):.3f}，向量2范数：{np.linalg.norm(emb2_norm):.3f}")
print(f"✅ 向量维度：{len(emb1_norm)}")

# 3. 写入Neo4j并查询
with neo4j_driver.session() as session:
    # 先清空
    session.run("MATCH (n) DETACH DELETE n")
    session.run("DROP INDEX entity_embedding_idx IF EXISTS")

    # 创建索引
    session.run("""
        CREATE VECTOR INDEX entity_embedding_idx IF NOT EXISTS
        FOR (e:Entity) ON e.embedding
        OPTIONS {
            indexConfig: {
                `vector.dimensions`: 2048,
                `vector.similarity_function`: 'cosine'
            }
        }
    """)

    # 写入第一个实体
    session.run("CREATE (e:Entity {name: $name, embedding: $emb})", name=word1, emb=emb1_norm.tolist())

    # 查询第二个实体的相似度
    result = session.run("""
        CALL db.index.vector.queryNodes('entity_embedding_idx', 1, $emb)
        YIELD node, score
        RETURN node.name AS name, score
    """, emb=emb2_norm.tolist())

    record = result.single()
    if record:
        print(f"\n❌ Neo4j返回相似度：{record['score']:.4f}，匹配实体：{record['name']}")
    else:
        print("\n✅ Neo4j无匹配结果")

neo4j_driver.close()
