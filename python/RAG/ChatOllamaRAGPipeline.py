from typing import List
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings

from python.downloader.ResourceFactory import ResourceFactory
from python.utils.timeit import timeit
from python.vectorstore.VectorStore import PersistentFAISSStore


class ChatOllamaRAGPipeline:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        model: str = "llama3",
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

        self.embeddings = OllamaEmbeddings(model="embeddinggemma")
        self.llm = ChatOllama(model=model, temperature=0.2)
        self.vectorstore = PersistentFAISSStore(self.embeddings)

    @timeit
    def build_index(self, paths: List[str]) -> None:
        for path in paths:
            try:
                res = ResourceFactory.get_for_path(path)
                location, content = res.download(path)
                if content:
                    chunks = self.text_splitter.split_text(content)
                    documents : List[Document] = []
                    for i, chunk in enumerate(chunks):
                        documents.append(Document(
                                page_content=chunk,
                                metadata={"source": location, "chunk_index": i, "total_chunks": len(chunks)},
                            ))
                    self.vectorstore.add_documents(documents)
                else:
                    self.logger.warning(f"No content from: {path}")
            except Exception as e:
                self.logger.error(f"Failed to extract {path}: {e}")

    @timeit
    def answer(self, query: str, num_of_documents: int = 4) -> str:
        if not self.vectorstore:
            raise RuntimeError("Vector index is not built. Call build_index() first.")
        
        retriever_docs = self.vectorstore.similarity_search(query, num_of_documents=num_of_documents)
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