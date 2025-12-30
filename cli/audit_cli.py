import argparse
from doctrine_audit import audit_book


def main():
    p = argparse.ArgumentParser(description="Doctrine Audit CLI")
    p.add_argument("--book-id", required=True, help="Book identifier")

    args = p.parse_args()

    report = audit_book(args.book_id)
    print(report)


if __name__ == "__main__":
    main()
