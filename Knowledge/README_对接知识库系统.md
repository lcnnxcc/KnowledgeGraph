# 与 knowledge-base-system 对接说明

## 功能说明
本模块实现了与知识库系统的无缝对接，无需修改知识库系统的任何代码，仅通过读取其PostgreSQL数据库即可实现：
- 自动拉取知识库系统中标记为`relation`类型的知识块
- 自动抽取三元组构建知识图谱存储到Neo4j
- 自动记录处理进度，支持增量处理，不会重复处理
- 保留完整溯源信息，可关联回原知识库系统的文档和知识块

## 依赖安装
```bash
pip install psycopg2-binary
```

## 配置说明
在 `config.py` 中新增了以下配置项，根据你的实际环境修改：

```python
# 知识库系统PostgreSQL连接配置
KBS_PG_HOST = "localhost"          # 知识库系统PG地址
KBS_PG_PORT = 5432                 # PG端口
KBS_PG_DATABASE = "knowledge_base" # 数据库名
KBS_PG_USER = "postgres"           # 用户名
KBS_PG_PASSWORD = "123456"         # 密码
# 需要处理的知识块类型，和知识库系统的knowledge_type字段对应
KBS_RELATION_KNOWLEDGE_TYPES = ["relation", "relational"]
```

同时确保原有配置正确：
- Neo4j连接配置（NEO4J_URI/USER/PASSWORD）
- 大模型API配置（DASHSCOPE_API_KEY/VOL_API_KEY等）

## 使用方法

### 1. 首次全量导入
```bash
python import_from_kbs.py --limit 1000
```
参数说明：
- `--limit`：单次最多处理的知识块数量，避免一次性处理太多超时
- `--category`：可选，按分类筛选只处理特定分类的知识块

### 2. 增量同步
可以定期执行该脚本（比如每小时）实现增量同步：
```bash
python import_from_kbs.py --limit 100
```
脚本会自动跳过已经处理过的知识块，只处理新产生的内容。

### 3. 处理指定文档的知识块
如果需要单独处理某篇文档，可以直接修改`import_from_kbs.py`调用`importer.get_all_chunks_by_doc_id(doc_id)`方法。

## 已处理记录
已处理的`chunk_id`会保存在`processed_chunks.json`文件中，如需重新处理某个知识块，删除该文件中对应的ID即可。

## 数据结构说明
Neo4j中存储的内容：
- 实体节点：包含`name`和`embedding`字段
- 关系边：包含`type`（关系类型）、`source_chunks`（来源知识块ID列表）、`triple_embedding`（三元组向量）字段
- 可以通过Cypher查询关联回原知识库系统：
  ```cypher
  MATCH (s)-[r:HAS_RELATION]->(o) 
  RETURN s.name, r.type, o.name, r.source_chunks
  ```

## 常见问题
1. **连接PG失败**：检查知识库系统的PostgreSQL是否允许外部连接，确认IP、端口、用户名密码正确
2. **没有拉取到知识块**：检查知识库系统的`chunks`表中是否有`knowledge_type`为`relation`的记录
3. **抽取三元组为空**：部分知识块可能确实没有可抽取的关系，属于正常现象
