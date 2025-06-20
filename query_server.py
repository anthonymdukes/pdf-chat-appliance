from flask import Flask, request, jsonify
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore

app = Flask(__name__)

@app.route("/query", methods=["POST"])
def query():
    prompt = request.json["question"]
    vector_store = ChromaVectorStore(persist_dir="chroma_store")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    return jsonify({"answer": str(response)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
