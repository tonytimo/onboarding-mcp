import time
import sys
from pathlib import Path
from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.base import Language
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

from config import LANGUAGE_MAP

# Initialize the embedding model
_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def get_language_from_extension(file_path: str) -> str:
    """
    Determine the programming language based on file extension.
    """
    ext = Path(file_path).suffix.lower()
    return LANGUAGE_MAP.get(ext, "text")


def load_and_process_code_files(
    file_paths: List[str], base_path: str
) -> List[Document]:
    """
    Load and process code files with LangChain's document loaders and text splitters.
    Supports multiple programming languages.
    """
    all_docs = []

    for file_path in file_paths:
        full_path = Path(base_path) / file_path

        # Load the file directly with TextLoader
        try:
            loader = TextLoader(str(full_path))
            documents = loader.load()

            # Set metadata for the document
            for doc in documents:
                doc.metadata["source"] = file_path

            # Determine language from file extension
            language = get_language_from_extension(file_path)

            # Use language-specific text splitter if supported
            try:
                text_splitter = RecursiveCharacterTextSplitter.from_language(
                    language=Language(language), chunk_size=2000, chunk_overlap=200
                )
            except ValueError:
                # Fallback for unsupported languages
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=2000, chunk_overlap=200
                )

            # Split the documents
            split_docs = text_splitter.split_documents(documents)
            all_docs.extend(split_docs)

        except Exception as e:
            print(f"Error loading {file_path}: {e}", file=sys.stderr)

    return all_docs


def index_code_chunks(file_paths: List[str], project_path: str):
    """
    Process code files and index them using InMemoryVectorStore.
    Returns the vector store for later searching.
    """
    start = time.time()

    # Load and process documents
    documents = load_and_process_code_files(file_paths, project_path)

    # Create InMemoryVectorStore
    vectorstore = InMemoryVectorStore(_embeddings)
    vectorstore.add_documents(documents)

    print(f"⏱️ Step -Embedder- took {time.time() - start:.2f}s", file=sys.stderr)
    return vectorstore
