import numpy as np
import time
import sys
import faiss
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def index_code_chunks(chunks) -> tuple[faiss.IndexFlatL2, list[str], list[str]]:
    start = time.time()

    texts = [code for _, code in chunks]
    paths = [path for path, _ in chunks]
    embeddings = _model.encode(texts, show_progress_bar=False)
    vectors = np.array(embeddings, dtype=np.float32)

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)  # type: ignore

    print(f"⏱️ Step -Embedder- took {time.time() - start:.2f}s", file=sys.stderr)
    return index, texts, paths


def embed_query(query):
    vector = _model.encode([query])
    return np.array(vector, dtype=np.float32)
