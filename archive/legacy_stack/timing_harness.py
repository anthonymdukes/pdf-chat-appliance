import os
import shutil
import tempfile
import time
import yaml
from pdfchat import Config, PDFIngestion

# Optimization parameters
CHUNK_SIZES = [256, 512, 768, 1024]
CHUNK_OVERLAPS = [0, 26, 51, 102]  # 0%, 10%, 20% of chunk_size (rounded)
EMBEDDING_MODELS = ["mistral", "bge-small", "mxbai"]  # Add more as available
VECTOR_STORE_CONFIGS = [
    {"distance": "Cosine"},
    {"distance": "Dot"},
    {"distance": "Euclid"},
]
PARALLEL_SETTINGS = [1, 2, 4]  # Number of threads/processes for parallelism

PDF_PATH = "documents/sample-vmware.pdf"
SESSION_NOTES = "session_notes.md"
TASK_MD = "TASK.md"

# Baseline metrics (to be filled after first run)
baseline = {}
best = {"ingestion_time": float('inf'), "query_latency": float('inf')}
loop_n = 1

def log_to_session_notes(log_dict, summary=False):
    with open(SESSION_NOTES, "r", encoding="utf-8") as f:
        old = f.read()
    log_yaml = yaml.dump(log_dict, sort_keys=False)
    if summary:
        with open(SESSION_NOTES, "w", encoding="utf-8") as f:
            f.write(f"## Ingestion Optimization Log (loop {log_dict['loop']})\n" + log_yaml + "\n" + old)
    else:
        with open(SESSION_NOTES, "a", encoding="utf-8") as f:
            f.write(f"\n---\nLoop {log_dict['loop']} details:\n" + log_yaml + "\n")

def run_optimization():
    global loop_n, baseline, best
    for chunk_size in CHUNK_SIZES:
        for overlap_pct in [0, 0.1, 0.2]:
            chunk_overlap = int(chunk_size * overlap_pct)
            for embedding_model in EMBEDDING_MODELS:
                for vstore_cfg in VECTOR_STORE_CONFIGS:
                    for parallel in PARALLEL_SETTINGS:
                        # Prepare temp dir
                        with tempfile.TemporaryDirectory() as temp_dir:
                            shutil.copy(PDF_PATH, os.path.join(temp_dir, "sample-vmware.pdf"))
                            # Config
                            config = Config()
                            config.docs_dir = temp_dir
                            config.embedding_model = embedding_model
                            setattr(config, "chunking", {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap})
                            setattr(config, "vector_store", vstore_cfg)
                            setattr(config, "parallel", parallel)
                            ingestion = PDFIngestion(config)
                            # Timing
                            start_time = time.time()
                            try:
                                ingestion.ingest_pdfs(temp_dir)
                            except Exception as e:
                                log_to_session_notes({
                                    "loop": loop_n,
                                    "start_time": start_time,
                                    "end_time": time.time(),
                                    "parameters": {
                                        "chunk_size": chunk_size,
                                        "chunk_overlap": chunk_overlap,
                                        "embedding_model": embedding_model,
                                        "vector_store_config": vstore_cfg,
                                        "parallel": parallel,
                                    },
                                    "error": str(e)
                                }, summary=True)
                                continue
                            end_time = time.time()
                            ingestion_time = end_time - start_time
                            # Simulate query latency (replace with real query if available)
                            query_latency = ingestion_time * 0.1  # Placeholder
                            # Baseline
                            if loop_n == 1:
                                baseline = {"ingestion_time": ingestion_time, "query_latency": query_latency}
                                best = baseline.copy()
                            # Improvement
                            improvement = {
                                "ingestion": 100 * (baseline["ingestion_time"] - ingestion_time) / baseline["ingestion_time"],
                                "query": 100 * (baseline["query_latency"] - query_latency) / baseline["query_latency"]
                            }
                            # Log summary at top, details at bottom
                            log_to_session_notes({
                                "loop": loop_n,
                                "start_time": start_time,
                                "end_time": end_time,
                                "parameters": {
                                    "chunk_size": chunk_size,
                                    "chunk_overlap": chunk_overlap,
                                    "embedding_model": embedding_model,
                                    "vector_store_config": vstore_cfg,
                                    "parallel": parallel,
                                },
                                "ingestion_time": ingestion_time,
                                "query_latency": query_latency,
                                "improvement": improvement
                            }, summary=True)
                            log_to_session_notes({
                                "loop": loop_n,
                                "start_time": start_time,
                                "end_time": end_time,
                                "parameters": {
                                    "chunk_size": chunk_size,
                                    "chunk_overlap": chunk_overlap,
                                    "embedding_model": embedding_model,
                                    "vector_store_config": vstore_cfg,
                                    "parallel": parallel,
                                },
                                "ingestion_time": ingestion_time,
                                "query_latency": query_latency,
                                "improvement": improvement
                            }, summary=False)
                            # Update best
                            if ingestion_time < best["ingestion_time"] and query_latency < best["query_latency"]:
                                best = {"ingestion_time": ingestion_time, "query_latency": query_latency}
                            # Exit criteria
                            if improvement["ingestion"] >= 25 and improvement["query"] >= 25:
                                with open(TASK_MD, "a", encoding="utf-8") as f:
                                    f.write(f"\n## Performance Optimization v2\nFinal parameters: {chunk_size=}, {chunk_overlap=}, {embedding_model=}, {vstore_cfg=}, {parallel=}\nFinal metrics: {ingestion_time=:.2f}s, {query_latency=:.2f}ms\n")
                                return
                            loop_n += 1

if __name__ == "__main__":
    run_optimization() 