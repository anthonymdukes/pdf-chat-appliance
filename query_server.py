from flask import Flask, request, jsonify
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore

import config

app = Flask(__name__)

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json(silent=True) or {}
    prompt = data.get("question", "").strip()
    if not prompt:
        return jsonify({"error": "question field required"}), 400

    try:
        vector_store = ChromaVectorStore(persist_dir=config.PERSIST_DIR)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = load_index_from_storage(storage_context)
    except Exception as err:
        return jsonify({"error": f"failed to load index: {err}"}), 500

    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    return jsonify({"answer": str(response)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
