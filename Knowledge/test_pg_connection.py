from Knowledge.importer import KBSImporter

importer = KBSImporter()
chunks = importer.get_unprocessed_relation_chunks(limit=5)
print(f"获取到 {len(chunks)} 个知识块")
for chunk in chunks:
    print(f"- {chunk['chunk_id']}: {chunk['title']}")
importer.close()