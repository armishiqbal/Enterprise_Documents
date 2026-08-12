"""
Recursive character text chunker with header preservation and stable chunk ID generation.
"""
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import Config, logger
from src.models import Document, DocumentChunk


class DocumentSplitter:
    """Splits Document instances into smaller, section-aware DocumentChunk instances."""

    def __init__(self, chunk_size: int = Config.CHUNK_SIZE, chunk_overlap: int = Config.CHUNK_OVERLAP):
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be > 0, got {chunk_size}")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be >= 0 and < chunk_size ({chunk_size})")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n\n", "\n\n", "\nSection ", "\n1.", "\n2.", "\n3.", "\n4.", "\n5.", "\n", ". ", " ", ""],
        )

    def split_document(self, document: Document) -> List[DocumentChunk]:
        """Splits a single Document into a list of DocumentChunks with stable IDs."""
        raw_chunks = self._splitter.split_text(document.page_content)
        total_chunks = len(raw_chunks)
        chunks = []

        page_suffix = f"_p{document.page_number}" if document.page_number is not None else ""

        for idx, chunk_text in enumerate(raw_chunks):
            # Deterministic, stable chunk ID: <doc_id>[_p<page>]_c<idx>
            chunk_id = f"{document.doc_id}{page_suffix}_c{idx}"

            chunk_meta = dict(document.metadata)
            chunk_meta.update({
                "chunk_id": chunk_id,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
            })

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=document.doc_id,
                    filename=document.filename,
                    file_type=document.file_type,
                    source_path=document.source_path,
                    page_content=chunk_text,
                    chunk_index=idx,
                    total_chunks=total_chunks,
                    page_number=document.page_number,
                    metadata=chunk_meta,
                )
            )

        return chunks

    def split_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """Splits a list of Documents into DocumentChunks."""
        all_chunks = []
        for doc in documents:
            doc_chunks = self.split_document(doc)
            all_chunks.extend(doc_chunks)
        logger.info(f"Split {len(documents)} document section(s) into {len(all_chunks)} chunk(s).")
        return all_chunks
