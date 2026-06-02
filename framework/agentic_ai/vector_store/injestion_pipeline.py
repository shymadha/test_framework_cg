"""
PDF Ingestion Pipeline
Loads a PDF, chunks it, embeds via Capgemini OpenAI-compatible endpoint,
and stores in a local ChromaDB vector store.
"""

import os
import uuid
from typing import List

import chromadb
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()


class IngestionPipeline:
    """
    Handles end-to-end PDF ingestion:
      1. Extract text from PDF
      2. Chunk text
      3. Embed chunks via Capgemini Amazon Titan endpoint
      4. Store embeddings in ChromaDB
    """

    def __init__(
        self,
        pdf_path: str,
        chroma_dir: str = "./chroma_db",
        collection_name: str = "pdf_store",
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        page_slice: slice = None,
    ):
        """
        Args:
            pdf_path:        Path to the PDF file.
            chroma_dir:      Directory to persist ChromaDB.
            collection_name: ChromaDB collection name.
            chunk_size:      Characters per chunk.
            chunk_overlap:   Overlap between consecutive chunks.
            page_slice:      Optional slice to limit pages, e.g. slice(-200, None).
        """
        self.pdf_path = pdf_path
        self.chroma_dir = chroma_dir
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.page_slice = page_slice

        self.api_key = os.getenv("API_KEY")

        self.openai_client = OpenAI(
            base_url="https://openai.generative.engine.capgemini.com/v1",
            api_key=self.api_key,
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        self.chroma_client = chromadb.PersistentClient(path=self.chroma_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )


    def extract_text(self) -> List[str]:
        """
        Extracts text from each page of the PDF using PyPDFLoader.
        Applies page_slice if provided.

        Returns:
            List of page text strings.
        """
        print("Extracting pdf")
        pages = PyPDFLoader(self.pdf_path).load()

        if self.page_slice:
            pages = pages[self.page_slice]

        texts = [doc.page_content or "" for doc in pages]
        print(f"Extracted text from {len(texts)} pages.")
        return texts


    def chunk_texts(self, texts: List[str]) -> List[str]:
        """
        Splits page texts into smaller overlapping chunks.

        Args:
            texts: List of page-level text strings.

        Returns:
            Flat list of text chunks.
        """

        print("Chunking....")

        full_text = "\n".join(texts)
        chunks    = self.splitter.split_text(full_text)
        print(f"Created {len(chunks)} chunks.")
        return chunks


    def embed(self, text: str) -> List[float]:
        """
        Embeds a single text string via the Capgemini Amazon Titan endpoint.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as a list of floats.
        """
        response = self.openai_client.embeddings.create(
            input=text,
            model="amazon.titan-embed-text-v2:0",
        )
        return response.data[0].embedding

    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Embeds all chunks, logging progress every 100 chunks.

        Args:
            chunks: List of text chunks.

        Returns:
            List of embedding vectors.
        """

        print("Embedding")

        embeddings = []
        for i, chunk in enumerate(chunks):
            embeddings.append(self.embed(chunk))
            if (i + 1) % 100 == 0:
                print(f"Embedded {i + 1}/{len(chunks)} chunks...")
        print(f"Embedding complete. Total: {len(embeddings)}")
        return embeddings

    def store(self, chunks: List[str], embeddings: List[List[float]]) -> None:
        """
        Stores chunks and their embeddings in ChromaDB.

        Args:
            chunks:     List of text chunks.
            embeddings: Corresponding embedding vectors.
        """

        print("Storing in VectorDB....")

        ids = [str(uuid.uuid4()) for _ in chunks]

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
        )
        print(f"Stored {len(chunks)} chunks in collection '{self.collection_name}'.")

    def run(self) -> None:
        """
        Runs the full ingestion pipeline:
        extract -> chunk -> embed -> store.
        """
        texts      = self.extract_text()
        chunks     = self.chunk_texts(texts)
        embeddings = self.embed_chunks(chunks)
        self.store(chunks, embeddings)
        print("Ingestion complete.")


if __name__ == "__main__":
    pipeline = IngestionPipeline(
        pdf_path="/home/shyamala/shyamala/code/test_framework_cg/framework/data/log/bbb_gpio_i2c_reference.pdf",
        chroma_dir="./chroma_db",
        collection_name="pdf_store",
        chunk_size=400,
        chunk_overlap=40,
        page_slice=slice(-200, None),   # last 200 pages; pass None for all pages
    )
    pipeline.run()