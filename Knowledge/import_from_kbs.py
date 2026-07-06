import sys
import os
# 将当前目录加入Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Knowledge import config
from Knowledge.models import chat_model, embedding_model
from Knowledge.extractors import relation_extractor
from Knowledge.storage import neo4j_store
from Knowledge.adapter import KBSAdapter
from Knowledge.importer import KBSImporter

def main(limit: int = 100, category: str = None):
    print("=" * 70)
    print("从知识库系统导入知识块并构建知识图谱")
    print("=" * 70)

    # 1. 初始化客户端
    print("\n[1/5] 初始化服务客户端...")
    try:
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

        extractor = relation_extractor.RelationExtractor(chat_model=qwen_client)

        neo4j = neo4j_store.Neo4jClient(
            uri=config.NEO4J_URI,
            user=config.NEO4J_USER,
            password=config.NEO4J_PASSWORD,
            embedding_client=embedding_client,
            embedding_dim=config.EMBEDDING_DIM,
            similarity_threshold=0.85,
        )

        importer = KBSImporter()
    except Exception as e:
        print(f"初始化失败: {e}")
        return

    # 2. 获取待处理知识块
    print("\n[2/5] 获取未处理的关系型知识块...")
    try:
        raw_chunks = importer.get_unprocessed_relation_chunks(limit=limit, category=category)
        if not raw_chunks:
            print("没有需要处理的新知识块")
            neo4j.close()
            importer.close()
            return
        print(f"获取到 {len(raw_chunks)} 个待处理知识块")
    except Exception as e:
        print(f"获取知识块失败: {e}")
        neo4j.close()
        importer.close()
        return

    # 3. 格式转换
    print("\n[3/5] 转换知识块格式...")
    converted_chunks = KBSAdapter.batch_convert(raw_chunks)
    print(f"成功转换 {len(converted_chunks)} 个有效关系型知识块")

    if not converted_chunks:
        print("没有有效知识块需要处理")
        neo4j.close()
        importer.close()
        return

    # 4. 处理每个知识块
    print("\n[4/5] 处理知识块并构建知识图谱...")
    processed_count = 0
    success_count = 0

    for chunk in converted_chunks:
        processed_count += 1
        chunk_id = chunk["chunk_id"]
        content = chunk["content"]
        title = chunk["title"]
        metadata = chunk["metadata"]

        print(f"\n[{processed_count}/{len(converted_chunks)}] 处理知识块: {chunk_id}")
        print(f"标题: {title}")
        print(f"内容: {content[:100]}..." if len(content) > 100 else f"内容: {content}")
        print(f"来源文档ID: {metadata['doc_id']}")

        try:
            # 抽取三元组
            triples = extractor.extract(content)
            if triples:
                print(f"抽取到三元组: {triples}")
                # 存储到Neo4j，传入原chunk_id
                neo4j.add_triples(triples, chunk_id)
                print("三元组已成功存储到知识图谱")
                success_count += 1
            else:
                print("未抽取到有效三元组")

            # 标记为已处理
            importer.mark_as_processed(chunk_id)

        except Exception as e:
            print(f"处理失败: {e}，跳过该知识块")
            continue

        print("-" * 50)

    # 5. 收尾
    print("\n[5/5] 处理完成！")
    print(f"总计处理: {processed_count} 个知识块")
    print(f"成功构建知识图谱: {success_count} 个知识块")
    print(f"失败/无三元组: {processed_count - success_count} 个知识块")

    neo4j.close()
    importer.close()

    print("\n知识图谱构建完成，可以通过Neo4j Browser查看结果。")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="从知识库系统导入知识块构建知识图谱")
    parser.add_argument("--limit", type=int, default=100, help="每次最多处理的知识块数量，默认100")
    parser.add_argument("--category", type=str, help="可选，按分类筛选知识块")
    args = parser.parse_args()

    main(limit=args.limit, category=args.category)
