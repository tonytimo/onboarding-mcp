from embedder import embed_query
from faiss import IndexFlatL2
import time
import sys


def search_code(
    query: str, index: IndexFlatL2, texts: list[str], paths: list[str], k: int = 5
) -> list[tuple[str, str]]:
    start = time.time()
    q_vec = embed_query(query)  # shape: (1, d)
    _, indices = index.search(q_vec, k)  # type: ignore
    print(f"⏱️ Step -Search- took {time.time() - start:.2f}s", file=sys.stderr)
    return [(paths[i], texts[i]) for i in indices[0]]
