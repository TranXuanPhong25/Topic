
from __future__ import annotations

import logging

from dotenv import load_dotenv

from .Retrieve import RAGPipeline

load_dotenv()
LOGGER = logging.getLogger(__name__)


def _print_header() -> None:
    print("=" * 70)
    print("🤖  RAG Assistant CLI")
    print("Enter a medical question in English to retrieve documents.")
    print("Type 'exit' or 'quit' to exit.")
    print("=" * 70)


def main() -> None:
    try:
        pipeline = RAGPipeline.from_existing_index()
    except Exception as exc:
        LOGGER.exception("Không khởi tạo được pipeline: %s", exc)
        raise SystemExit(1) from exc

    _print_header()

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        try:
            result = pipeline.invoke(question)
            print("\nAcademic Response\n")
            print(result["answer"])
        except ValueError as exc:
            print(f"ERROR: {exc}")
        except Exception as exc:
            LOGGER.exception("Error generating answer: %s", exc)
            print("ERROR: An error occurred. Please try again.")


if __name__ == "__main__":
    main()

