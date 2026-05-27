"""
Retrieval Pipeline
"""

import os
from typing import List
from openai import OpenAI
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import chromadb
from dotenv import load_dotenv

load_dotenv()


class RetrievalPipeline:
    """
    Retrieves relevant chunks from ChromaDB using three strategies:
    similarity, hybrid (BM25 + vector), and query expansion.
    """

    def __init__(
        self,
        chroma_dir: str = "./chroma_db",
        collection_name: str = "pdf_store",
        top_k: int = 5,
    ):
        """
        Args:
            chroma_dir:      Path to persisted ChromaDB directory.
            collection_name: Collection to retrieve from.
            top_k:           Number of results to return per retrieval.
        """
        self.top_k           = top_k
        self.api_key         = os.getenv("API_KEY")
        self.openai_client   = OpenAI(
            base_url="https://openai.generative.engine.capgemini.com/v1",
            api_key=self.api_key,
        )
        self.chroma_client   = chromadb.PersistentClient(path=chroma_dir)
        self.collection      = self.chroma_client.get_collection(name=collection_name)

    def _embed(self, text: str) -> List[float]:
        """
        Embeds a single string via the Capgemini Amazon Titan endpoint.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector.
        """
        response = self.openai_client.embeddings.create(
            input=text,
            model="amazon.titan-embed-text-v2:0",
        )
        return response.data[0].embedding

    def _get_all_documents(self) -> List[Document]:
        """
        Fetches all stored chunks from ChromaDB as LangChain Document objects.
        Used to build the BM25 index for hybrid search.

        Returns:
            List of Document objects.
        """
        results = self.collection.get(include=["documents", "metadatas"])
        return [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(results["documents"], results["metadatas"])
        ]

    def _format(self, documents: List[str], label: str) -> List[dict]:
        """
        Wraps raw document strings into a labelled list of dicts.

        Args:
            documents: List of retrieved text chunks.
            label:     Strategy label for traceability.

        Returns:
            List of {"strategy": ..., "content": ...} dicts.
        """
        return [{"strategy": label, "content": doc} for doc in documents]

    def similarity_search(self, query: str) -> List[dict]:
        """
        Pure dense vector retrieval using cosine similarity.

        Args:
            query: User query string.

        Returns:
            Top-k results as formatted dicts.
        """
        query_embedding = self._embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k,
            include=["documents"],
        )
        docs = results["documents"][0]
        print(f"[Similarity] Retrieved {len(docs)} chunks.")
        return self._format(docs, label="similarity")

    def hybrid_search(self, query: str, bm25_weight: float = 0.5) -> List[dict]:
        """
        Combines BM25 sparse retrieval and dense vector retrieval using
        Reciprocal Rank Fusion (RRF) for final ranking.

        Args:
            query:        User query string.
            bm25_weight:  Weight for BM25 scores in RRF (0 to 1).
                          Vector weight = 1 - bm25_weight.

        Returns:
            Top-k fused results as formatted dicts.
        """
        vector_weight = 1 - bm25_weight

        # Dense retrieval (fetch 2x top_k to have enough candidates for fusion)
        query_embedding = self._embed(query)
        vector_results  = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k * 2,
            include=["documents"],
        )
        vector_docs = vector_results["documents"][0]

        # Sparse retrieval via BM25
        all_documents   = self._get_all_documents()
        bm25_retriever  = BM25Retriever.from_documents(all_documents)
        bm25_retriever.k = self.top_k * 2
        bm25_docs       = [doc.page_content for doc in bm25_retriever.invoke(query)]

        # Reciprocal Rank Fusion
        rrf_scores: dict[str, float] = {}

        for rank, doc in enumerate(vector_docs):
            rrf_scores[doc] = rrf_scores.get(doc, 0) + vector_weight / (rank + 1)

        for rank, doc in enumerate(bm25_docs):
            rrf_scores[doc] = rrf_scores.get(doc, 0) + bm25_weight / (rank + 1)

        fused = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[: self.top_k]
        print(f"[Hybrid] Retrieved {len(fused)} chunks after RRF fusion.")
        return self._format(fused, label="hybrid")
     

if __name__ == "__main__":
    pipeline = RetrievalPipeline(
        chroma_dir="./chroma_db",
        collection_name="pdf_store",
        top_k=5,
    )

    query = "The I2cRegisterReadTest failed. The incorrect device slave address used was 53, which is in decimal format and may be incorrect for the intended device. This address was used to read from the I2C bus with ID 0 and register 0."

    print("\n=== Similarity Search ===")
    for r in pipeline.similarity_search(query):
        print(r)
        print("========")

    print("\n=== Hybrid Search ===")
    for r in pipeline.hybrid_search(query, bm25_weight=0.4):
        print(r)
        print("========")
