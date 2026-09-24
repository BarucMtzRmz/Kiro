import argparse
import sys

from . import rag, vectorstore


def cmd_ingest(args):
    docs, chunks = rag.ingest_path(args.path)
    print(f"Indexed {docs} document(s) into {chunks} chunk(s).")


def cmd_ask(args):
    answer, sources = rag.answer(args.question, top_k=args.top_k)
    print(answer)
    if sources:
        print("\nSources:")
        for s in sources:
            print(f"  - {s}")


def cmd_chat(args):
    print("Kiro — chat with your local documents. Type 'exit' or Ctrl+D to quit.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        answer, sources = rag.answer(question)
        print(f"\nKiro: {answer}")
        if sources:
            print("Sources: " + ", ".join(sources))
        print()


def cmd_reset(args):
    vectorstore.reset_collection()
    print("Index cleared.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kiro", description="Chat with documents stored on your own device."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Index a file or directory of documents")
    p_ingest.add_argument("path", help="Path to a file or directory (.txt, .md, .pdf, .docx)")
    p_ingest.set_defaults(func=cmd_ingest)

    p_ask = sub.add_parser("ask", help="Ask a single question and exit")
    p_ask.add_argument("question")
    p_ask.add_argument("--top-k", type=int, default=None, dest="top_k")
    p_ask.set_defaults(func=cmd_ask)

    p_chat = sub.add_parser("chat", help="Interactive chat session")
    p_chat.set_defaults(func=cmd_chat)

    p_reset = sub.add_parser("reset", help="Clear the local index")
    p_reset.set_defaults(func=cmd_reset)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
