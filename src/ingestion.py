"""
Document ingestion pipeline orchestrating loading, parsing, cleaning, chunking, and vector database indexing.
"""
from pathlib import Path
from typing import List, Union, Optional
from src.config import Config, logger
from src.loaders import load_document, SUPPORTED_EXTENSIONS
from src.models import DocumentChunk
from src.splitter import DocumentSplitter
from src.store import VectorStore


class IngestionPipeline:
    """Orchestrates loading, processing, chunking, and vector database indexing."""

    def __init__(
        self,
        chunk_size: int = Config.CHUNK_SIZE,
        chunk_overlap: int = Config.CHUNK_OVERLAP,
        vector_store: Optional[VectorStore] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = DocumentSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        self.vector_store = vector_store or VectorStore()

    def process_file(self, file_path: Union[str, Path], index_to_store: bool = True) -> List[DocumentChunk]:
        """Loads, chunks, and indexes a single document file into the vector store."""
        path = Path(file_path).resolve()
        documents = load_document(path)
        chunks = self.splitter.split_documents(documents)

        if index_to_store and chunks:
            self.vector_store.add_chunks(chunks)

        logger.info(f"Successfully processed '{path.name}': generated and indexed {len(chunks)} chunk(s).")
        return chunks

    def process_directory(
        self, dir_path: Union[str, Path], recursive: bool = True, index_to_store: bool = True
    ) -> List[DocumentChunk]:
        """Loads, chunks, and indexes all supported document files in a directory."""
        path = Path(dir_path).resolve()
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Target directory does not exist: {path}")

        pattern = "**/*" if recursive else "*"
        all_chunks = []

        for p in path.glob(pattern):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    chunks = self.process_file(p, index_to_store=index_to_store)
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.warning(f"Skipping file '{p.name}' due to ingestion error: {e}")

        logger.info(f"Batch ingestion complete for '{path.name}': total {len(all_chunks)} chunk(s) indexed.")
        return all_chunks
