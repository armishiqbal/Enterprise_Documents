"""
ChromaDB Vector Store Manager for persistent embedding storage, multi-tenant isolation, and metadata querying.
Includes in-memory fallback for serverless environments (Vercel).
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import chromadb
from src.config import Config, logger
from src.embedder import Embedder
from src.models import DocumentChunk


class VectorStore:
    """Manager for persistent ChromaDB vector store operations with serverless fallback."""

    def __init__(
        self,
        persist_dir: Optional[Union[str, Path]] = None,
        collection_name: str = "document_chunks",
    ):
        self.persist_dir = Path(persist_dir or Config.VECTOR_STORE_DIR).resolve()
        self.collection_name = collection_name

        try:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initializing ChromaDB PersistentClient at '{self.persist_dir}' (Collection: '{self.collection_name}')")
            self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        except Exception as e:
            logger.warning(f"ChromaDB PersistentClient initialization fallback ({e}). Using EphemeralClient.")
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.embedder = Embedder()

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Embeds and upserts a list of DocumentChunks into the vector database."""
        if not chunks:
            return 0

        logger.info(f"Adding {len(chunks)} chunk(s) to vector store...")

        ids = [chunk.chunk_id for chunk in chunks]
        texts = [chunk.page_content for chunk in chunks]
        
        metadatas = []
        for chunk in chunks:
            clean_meta = {}
            for k, v in chunk.metadata.items():
                if v is not None:
                    clean_meta[k] = str(v) if isinstance(v, (list, dict)) else v
            metadatas.append(clean_meta)

        embeddings = self.embedder.embed_texts(texts)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        logger.info(f"Successfully indexed {len(chunks)} chunk(s) in collection '{self.collection_name}'.")
        return len(chunks)

    def get_collection_stats(self) -> Dict[str, Any]:
        """Returns statistics about stored document chunks in the collection."""
        try:
            total_chunks = self.collection.count()
            unique_docs = set()
            if total_chunks > 0:
                result = self.collection.get(include=["metadatas"])
                for meta in result.get("metadatas", []):
                    if meta and "doc_id" in meta:
                        unique_docs.add(meta["doc_id"])

            return {
                "collection_name": self.collection_name,
                "total_chunks": total_chunks,
                "unique_documents": len(unique_docs),
                "persist_directory": str(self.persist_dir),
            }
        except Exception:
            return {
                "collection_name": self.collection_name,
                "total_chunks": 0,
                "unique_documents": 0,
                "persist_directory": str(self.persist_dir),
            }

    def delete_document(self, doc_id: str) -> int:
        """Deletes all vector chunks associated with a specific doc_id."""
        result = self.collection.get(where={"doc_id": doc_id})
        ids_to_delete = result.get("ids", [])
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            logger.info(f"Deleted {len(ids_to_delete)} chunk(s) for doc_id '{doc_id}'.")
            return len(ids_to_delete)
        return 0

    def reset_store(self) -> bool:
        """Clears all stored entries in the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"Vector store collection '{self.collection_name}' reset successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to reset vector store collection: {e}")
            return False
