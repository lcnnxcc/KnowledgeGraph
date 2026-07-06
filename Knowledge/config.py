import os

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")

# 阿里云百炼（关系抽取）
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "eab3e57e-edc9-4927-8df6-a88446da8fee")
# QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen3.6-plus")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen3.6-35b-a3b")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# DASHSCOPE_API_KEY = "ark-140d7c0e-0647-4ffa-aab8-8b9d09764caa-6fee4"
# QWEN_MODEL = os.getenv("QWEN_MODEL", "doubao-seed-2-1-pro-260628")
# DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
# 调用阿里云模型时长一次15s左右，火山方舟模型时长一次120s左右


# VOL_BASE_URL = os.getenv("VOL_BASE_URL", "http://localhost:11434/v1")
# VOL_EMBED_MODEL = os.getenv("VOL_EMBED_MODEL", "qwen3-embedding:0.6b")
# VOL_API_KEY = os.getenv("VOL_API_KEY", "ark-140d7c0e-0647-4ffa-aab8-8b9d09764caa-6fee4")
# doubao embedding
VOL_BASE_URL = os.getenv("VOL_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
VOL_EMBED_MODEL = os.getenv("VOL_EMBED_MODEL", "doubao-embedding-large-text-250515")
VOL_API_KEY = os.getenv("VOL_API_KEY", "ark-140d7c0e-0647-4ffa-aab8-8b9d09764caa-6fee4")


EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "2048"))

# 知识库系统（knowledge-base-system）对接配置
KBS_PG_HOST = os.getenv("KBS_PG_HOST", "localhost")
KBS_PG_PORT = int(os.getenv("KBS_PG_PORT", "5432"))
KBS_PG_DATABASE = os.getenv("KBS_PG_DATABASE", "knowledge_base")
KBS_PG_USER = os.getenv("KBS_PG_USER", "kbuser")
KBS_PG_PASSWORD = os.getenv("KBS_PG_PASSWORD", "kbpass")
# 仅处理标记为relation类型的知识块
KBS_RELATION_KNOWLEDGE_TYPES = os.getenv("KBS_RELATION_KNOWLEDGE_TYPES", "relation,relational").split(",")