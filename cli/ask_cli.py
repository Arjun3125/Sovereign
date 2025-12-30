import argparse
from query_engine.ask import ask


def main():
    p = argparse.ArgumentParser(description="Doctrine Query CLI")
    p.add_argument("--book-id", required=True, help="Book identifier")
    p.add_argument("--q", required=True, help="Question to ask")

    args = p.parse_args()

    answer = ask(
        book_id=args.book_id,
        question=args.q
    )
    print(answer)


if __name__ == "__main__":
    main()
