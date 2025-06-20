import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

import config

docs_dir = config.DOCS_DIR
persist_dir = config.PERSIST_DIR

print(f"[+] Loading PDFs from {docs_dir}...")

if not os.path.exists(docs_dir) or not os.listdir(docs_dir):
    raise SystemExit("No documents found in 'documents/' directory.")

documents = SimpleDirectoryReader(docs_dir, recursive=True).load_data()

print(f"[+] Converting {len(documents)} files to vector store...")

embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL_NAME)
vector_store = ChromaVectorStore(persist_dir=persist_dir)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model
)
index.storage_context.persist()

print("[\u2713] Vector database updated.")
