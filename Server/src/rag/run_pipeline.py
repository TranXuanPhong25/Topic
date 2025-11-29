"""Simple CLI runner for the RAG pipeline."""

from __future__ import annotations

import logging

from dotenv import load_dotenv

from .Retrieve import RAGPipeline

load_dotenv()
LOGGER = logging.getLogger(__name__)


def _print_header() -> None:
    print("=" * 70)
    print("🤖  RAG Assistant CLI")
    print("Nhập câu hỏi y khoa bằng tiếng Việt để truy xuất tài liệu.")
    print("Gõ 'exit' hoặc 'quit' để thoát.")
    print("=" * 70)


def main() -> None:
    """Entry point for interactive usage."""
    try:
        pipeline = RAGPipeline.from_existing_index()
    except Exception as exc:
        LOGGER.exception("Không khởi tạo được pipeline: %s", exc)
        raise SystemExit(1) from exc

    _print_header()

    while True:
        try:
            question = input("\n💬 Câu hỏi: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTạm biệt!")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Tạm biệt!")
            break

        try:
            result = pipeline.invoke(question)
            print("\n📝 Phản hồi học thuật\n")
            print(result["answer"])
        except ValueError as exc:
            print(f"❌ {exc}")
        except Exception as exc:
            LOGGER.exception("Lỗi khi tạo câu trả lời: %s", exc)
            print("❌ Đã xảy ra lỗi. Vui lòng thử lại.")


if __name__ == "__main__":
    main()

