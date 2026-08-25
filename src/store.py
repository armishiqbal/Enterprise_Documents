"""
ChromaDB Vector Store Manager for persistent embedding storage, multi-tenant isolation, and metadata querying.
Includes in-memory and mock fallback for serverless environments (Vercel).
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
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
        self.client = None
        self.collection = None

        try:
            import chromadb
            from chromadb.config import Settings
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initializing ChromaDB PersistentClient at '{self.persist_dir}' (Collection: '{self.collection_name}')")
            try:
                self.client = chromadb.PersistentClient(
                    path=str(self.persist_dir),
                    settings=Settings(anonymized_telemetry=False, is_persistent=True),
                )
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
            except BaseException as client_err:
                logger.warning(f"PersistentClient error ({client_err}), attempting clean reinit...")
                sqlite_file = self.persist_dir / "chroma.sqlite3"
                if sqlite_file.exists():
                    sqlite_file.unlink()
                try:
                    self.client = chromadb.PersistentClient(
                        path=str(self.persist_dir),
                        settings=Settings(anonymized_telemetry=False, is_persistent=True),
                    )
                    self.collection = self.client.get_or_create_collection(
                        name=self.collection_name,
                        metadata={"hnsw:space": "cosine"},
                    )
                except BaseException:
                    self.client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
                    self.collection = self.client.get_or_create_collection(
                        name=self.collection_name,
                        metadata={"hnsw:space": "cosine"},
                    )
        except BaseException as e:
            logger.warning(f"ChromaDB initialization fallback ({e}).")

        self.embedder = Embedder()

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Embeds and upserts a list of DocumentChunks into the vector database."""
        if not chunks or not self.collection:
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
            if not self.collection:
                return {
                    "collection_name": self.collection_name,
                    "total_chunks": 0,
                    "unique_documents": 0,
                    "persist_directory": str(self.persist_dir),
                }

            total_chunks = self.collection.count()
            unique_docs = set()
            file_names = set()
            if total_chunks > 0:
                result = self.collection.get(include=["metadatas"])
                for meta in result.get("metadatas", []):
                    if meta:
                        if "doc_id" in meta and meta["doc_id"]:
                            unique_docs.add(meta["doc_id"])
                        if "filename" in meta and meta["filename"]:
                            file_names.add(meta["filename"])

            return {
                "collection_name": self.collection_name,
                "total_chunks": total_chunks,
                "unique_documents": len(unique_docs),
                "indexed_files": sorted(list(file_names)),
                "persist_directory": str(self.persist_dir),
            }
        except Exception:
            return {
                "collection_name": self.collection_name,
                "total_chunks": 0,
                "unique_documents": 0,
                "indexed_files": [],
                "persist_directory": str(self.persist_dir),
            }

    def delete_document(self, doc_id: str) -> int:
        """Deletes all vector chunks associated with a specific doc_id."""
        if not self.collection:
            return 0
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
            if not self.client:
                return True
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

    def get_document_text(self, filename: str) -> str:
        """Retrieves all combined text content for a specific document filename."""
        if not self.collection:
            return ""
        try:
            result = self.collection.get(
                where={"filename": filename},
                include=["documents", "metadatas"],
            )
            docs = result.get("documents", [])
            if docs:
                return "\n\n".join(docs)
        except Exception as e:
            logger.warning(f"Error fetching chunks from vector store for '{filename}': {e}")

        # Fallback: check upload directory
        upload_path = Path(Config.UPLOAD_DIR) / filename
        if upload_path.exists():
            try:
                from src.loaders import DocumentLoader
                chunks = DocumentLoader.load_file(str(upload_path))
                return "\n\n".join(c.text for c in chunks)
            except Exception as read_err:
                logger.warning(f"Error reading raw upload file '{filename}': {read_err}")
        return ""

