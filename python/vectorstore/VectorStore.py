from typing import List, Optional, Iterable
from pathlib import Path

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

class PersistentFAISSStore:
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self.vectorstore: Optional[FAISS] = None

    def build_from_documents(self, documents: List[Document]) -> None:
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)

    def add_documents(self, documents: List[Document]) -> None:
        if not self.vectorstore:
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self.vectorstore.add_documents(documents)

    def add_texts(
        self,
        texts: Iterable[str],
        metadata: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        if not self.vectorstore:
            self.vectorstore = FAISS.from_texts(list(texts), self.embeddings, metadatas=metadata, ids=ids)
            return ids or []
        return self.vectorstore.add_texts(list(texts), metadatas=metadata, ids=ids)

    # ---------------------------
    # Persistence
    # ---------------------------
    def save_index(self, directory: Path) -> None:
        if not self.vectorstore:
            raise RuntimeError("Vector index is not built. Build or add content first.")
        self.vectorstore.save_local(folder_path=str(directory))

    def load_index(self, directory: Path) -> FAISS:
        """
        Load FAISS index from disk using the same embeddings.
        """
        if not directory.exists():
            raise FileNotFoundError(f"Index directory not found: {directory}")
        self.vectorstore = FAISS.load_local(
            folder_path=str(directory),
            embeddings=self.embeddings,
            allow_dangerous_deserialization=False,
        )
        return self.vectorstore

    # ---------------------------
    # Retrieval
    # ---------------------------
    def similarity_search(self, query: str, num_of_documents: int = 4) -> List[Document]:
        if not self.vectorstore:
            raise RuntimeError("Vector index is not built or loaded.")
        return self.vectorstore.similarity_search(query, k=num_of_documents)

    def as_retriever(self, num_of_documents: int = 4):
        if not self.vectorstore:
            raise RuntimeError("Vector index is not built or loaded.")
        return self.vectorstore.as_retriever(search_kwargs={"k": num_of_documents})