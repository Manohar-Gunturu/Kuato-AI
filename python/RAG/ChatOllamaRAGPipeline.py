from typing import List, Tuple, Optional
from pathlib import Path
from urllib.parse import urlparse
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama

from python.downloader.ResourceFactory import ResourceFactory


class ChatOllamaRAGPipeline:
    """
    Local RAG using:
      - ResourceFactory (singletons per resource)
      - RecursiveCharacterTextSplitter
      - OllamaEmbeddings (e.g., nomic-embed-text)
      - ChatOllama (e.g., llama3/mistral)
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "nomic-embed-text",
        llm_model: str = "llama3",
        ollama_base_url: Optional[str] = "http://localhost:11434",
    ):
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

        self.embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_base_url)
        self.llm = ChatOllama(model=llm_model, base_url=ollama_base_url, temperature=0.2)

        self.vectorstore: Optional[FAISS] = None

    def _extract(self, inputs: List[str]) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        for p in inputs:
            try:
                res = ResourceFactory.get_for_path(p)
                location, content = res.download(p)
                if content and content.strip():
                    out.append((location, content))
                    self.logger.info(f"Extracted: {location}")
                else:
                    self.logger.warning(f"No content from: {p}")
            except Exception as e:
                self.logger.error(f"Failed to extract {p}: {e}")
        return out

    def _to_documents(self, items: List[Tuple[str, str]]) -> List[Document]:
        docs: List[Document] = []
        for location, content in items:
            chunks = self.text_splitter.split_text(content)
            for i, chunk in enumerate(chunks):
                docs.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": location, "chunk_index": i, "total_chunks": len(chunks)},
                    )
                )
        self.logger.info(f"Created {len(docs)} chunks.")
        return docs

    def build_index(self, inputs: List[str]) -> FAISS:
        extracted = self._extract(inputs)
        if not extracted:
            raise ValueError("No content extracted from inputs.")
        docs = self._to_documents(extracted)
        self.vectorstore = FAISS.from_documents(docs, self.embeddings)
        self.logger.info("FAISS index built.")
        return self.vectorstore

    def answer(self, query: str, k: int = 4) -> str:
        if not self.vectorstore:
            raise RuntimeError("Vector index is not built. Call build_index() first.")
        retriever_docs = self.vectorstore.similarity_search(query, k=k)
        context = "\n\n".join(
            f"[{i+1}] Source: {d.metadata.get('source')}\n{d.page_content}"
            for i, d in enumerate(retriever_docs)
        )
        prompt = (
            "You are a helpful assistant. Answer based only on the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )
        response = self.llm.invoke(prompt)
        return getattr(response, "content", str(response))