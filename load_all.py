import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.storage import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

docs_dir = "documents"
persist_dir = "chroma_store"

print(f"[+] Loading PDFs from {docs_dir}...")

documents = SimpleDirectoryReader(docs_dir, recursive=True).load_data()

print(f"[+] Converting {len(documents)} files to vector store...")

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = ChromaVectorStore(persist_dir=persist_dir)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model
)
index.storage_context.persist()

print("[\u2713] Vector database updated.")
