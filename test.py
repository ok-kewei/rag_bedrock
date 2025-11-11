from chromadb import PersistentClient

client = PersistentClient(path="./chroma_db")
collection = client.get_collection("langchain")

sample = collection.peek(1)  # get one stored vector
print(len(sample['embeddings'][0]))  # this is the embedding dimension

# from chromadb import PersistentClient
#
# client = PersistentClient(path="../chroma_db")
# print(client.list_collections())  # should show at least one collection
#
# coll = client.get_or_create_collection("langchain")
# print(coll.metadata)

# import os
# from langchain_chroma import Chroma
#
# CHROMA_DB_DIR = "../chroma_db"
#
# if os.path.exists(CHROMA_DB_DIR):
#     print("🟡 Existing Chroma DB found. Checking embedding dimension...")
#     try:
#         db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=None)
#         print("📏 Existing embedding dimension:", db._collection.metadata.get("embedding_dimension"))
#     except Exception as e:
#         print(f"⚠️ Could not read existing DB metadata: {e}")
# else:
#     print("🆕 No Chroma DB found — will create a new one.")

