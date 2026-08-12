"""
CLI tool to query the persistent vector store and format retrieved context.
"""
import argparse
from src.config import Config, logger
from src.prompts import GROUND_PROMPT
from src.retriever import Retriever


def main(query, k=4, threshold=0.0):
    retriever = Retriever()
    results = retriever.retrieve(query, k=k, score_threshold=threshold)

    print("\n" + "=" * 60)
    print(f"QUERY: '{query}'")
    print(f"RETRIEVED: {len(results)} relevant document chunk(s)")
    print("=" * 60 + "\n")

    if not results:
        print("No matching document chunks found in vector store. Please ingest documents first.")
        return

    context_blocks = []
    for i, r in enumerate(results, start=1):
        page_str = f", Page {r.page_number}" if r.page_number else ""
        header = f"[{i}] File: {r.filename}{page_str} | Match Score: {int(r.score * 100)}% | Chunk ID: {r.chunk_id}"
        print(header)
        print("-" * len(header))
        print(f"{r.text}\n")
        context_blocks.append(f"Source: {r.filename}{page_str} (Chunk: {r.chunk_id})\nContent:\n{r.text}")

    context_str = "\n\n---\n\n".join(context_blocks)
    prompt = GROUND_PROMPT.format(context=context_str, question=query)

    print("=" * 60)
    print("FORMATTED GROUNDED PROMPT FOR LLM:")
    print("=" * 60)
    print(prompt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query persistent vector database for document chunks.")
    parser.add_argument("--query", required=True, help="User search query.")
    parser.add_argument("--k", type=int, default=4, help="Number of chunks to retrieve.")
    parser.add_argument("--threshold", type=float, default=0.0, help="Minimum similarity score threshold (0.0 to 1.0).")
    args = parser.parse_args()
    main(args.query, k=args.k, threshold=args.threshold)
