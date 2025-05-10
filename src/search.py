import time
import sys
from typing import List, Tuple

from langchain_core.vectorstores import InMemoryVectorStore


def search_code(
    query: str, vectorstore: InMemoryVectorStore, k: int = 5
) -> List[Tuple[str, str]]:
    """
    Search for relevant code chunks using the vector store.
    Returns a list of (path, content) tuples.
    """
    start = time.time()

    # Search the vector store
    docs = vectorstore.similarity_search(query, k=k)

    # Extract path and content from documents
    results = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        content = doc.page_content
        results.append((source, content))

    print(f"⏱️ Step -Search- took {time.time() - start:.2f}s", file=sys.stderr)
    return results
