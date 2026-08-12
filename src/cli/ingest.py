"""
CLI tool for document ingestion and text processing verification.
"""
import argparse
import sys
from src.config import Config, logger
from src.ingestion import IngestionPipeline


def main(files, chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP):
    pipeline = IngestionPipeline(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    total_chunks = []

    for file_path in files:
        try:
            chunks = pipeline.process_file(file_path)
            total_chunks.extend(chunks)
        except Exception as e:
            logger.error(f"Failed to process '{file_path}': {e}")
            print(f"ERROR processing '{file_path}': {e}", file=sys.stderr)

    print("\n" + "=" * 60)
    print(f"INGESTION COMPLETE: Processed {len(files)} file(s), generated {len(total_chunks)} chunk(s).")
    print("=" * 60 + "\n")

    # Display sample chunk details if available
    if total_chunks:
        sample = total_chunks[0]
        print("SAMPLE CHUNK DETAILS:")
        print(f"  Chunk ID     : {sample.chunk_id}")
        print(f"  Doc ID       : {sample.doc_id}")
        print(f"  Filename     : {sample.filename}")
        print(f"  File Type    : {sample.file_type}")
        print(f"  Page Number  : {sample.page_number}")
        print(f"  Source Path  : {sample.source_path}")
        print(f"  Chunk Index  : {sample.chunk_index} of {sample.total_chunks}")
        print("  Metadata     :", sample.metadata)
        print("  Snippet      :", repr(sample.page_content[:150]) + ("..." if len(sample.page_content) > 150 else ""))
        print("-" * 60)

    return total_chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents and extract processed text chunks.")
    parser.add_argument("--files", nargs="+", required=True, help="List of file paths to process.")
    parser.add_argument("--chunk_size", type=int, default=Config.CHUNK_SIZE, help="Chunk size in characters.")
    parser.add_argument("--chunk_overlap", type=int, default=Config.CHUNK_OVERLAP, help="Chunk overlap in characters.")
    args = parser.parse_args()
    main(args.files, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
