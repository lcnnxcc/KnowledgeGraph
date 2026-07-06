from Knowledge import config
from Knowledge.models import chat_model, embedding_model
from Knowledge.extractors import relation_extractor
from Knowledge.storage import neo4j_store
from chunk import MOCK_CHUNKS

# 测试数据
# MOCK_CHUNKS = [
#     {
#         "chunk_id": "chunk_001",
#         "title": "看视频奖励活动升级",
#         "content": "看视频奖励活动关联用户积分和观看时长。",
#         "knowledge_type": "relational"
#     },
#     {
#         "chunk_id": "chunk_002",
#         "title": "会员权限说明",
#         "content": "高级会员包含无限次视频回放和专属客服权益。",
#         "knowledge_type": "relational"
#     },
#     {
#         "chunk_id": "chunk_003",
#         "title": "订单归属",
#         "content": "订单数据归属于用户ID字段，同时关联支付流水号。",
#         "knowledge_type": "relational"
#     },
#     {
#         "chunk_id": "chunk_004",
#         "title": "版本更新声明",
#         "content": "活动已经升级到支持视频播放功能了。",
#         "knowledge_type": "declarative"
#     }
# ]
# MOCK_CHUNKS = [
#     {
#         "chunk_id": "chunk_005",
#         "title": "看视频奖励活动升级",
#         "content": "视频观看激励活动包含专属客服权益。",
#         "knowledge_type": "relational"
#     },
#     # 可继续添加更多
# ]

def main():
    # config = Config()

    # 1. 创建模型客户端（独立创建，业务逻辑引用）
    qwen_client = chat_model.ChatModel(
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.DASHSCOPE_BASE_URL,
        model=config.QWEN_MODEL
    )


    embedding_client = embedding_model.EmbeddingClient(
        api_key=config.VOL_API_KEY,
        base_url=config.VOL_BASE_URL,
        model=config.VOL_EMBED_MODEL
    )

    # 2. 创建抽取器（注入 LLM 客户端）
    extractor = relation_extractor.RelationExtractor(chat_model=qwen_client)

    # 3. 创建 Neo4j 存储客户端
    neo4j = neo4j_store.Neo4jClient(
        uri=config.NEO4J_URI,
        user=config.NEO4J_USER,
        password=config.NEO4J_PASSWORD,
        embedding_client=embedding_client,
        embedding_dim=config.EMBEDDING_DIM,
        similarity_threshold=0.85,

    )

    # 4. 处理每个知识块
    for chunk in MOCK_CHUNKS:
        chunk_id = chunk["chunk_id"]
        content = chunk["content"]
        k_type = chunk["knowledge_type"]

        print(f" 处理知识块: {chunk_id} (类型: {k_type})")
        print(f" 内容: {content}")

        if k_type == "relational":
            triples = extractor.extract(content)
            if triples:
                print(f" 抽取到三元组: {triples}")
                neo4j.add_triples(triples, chunk_id)
                print(f" 已存储到 Neo4j")
            else:
                print(f" 未抽取到有效三元组")
        else:
            print(f" 跳过 (非关系型)")

        print("-" * 50)

    neo4j.close()
    print("所有知识块处理完毕")

if __name__ == "__main__":
    main()