class ReadOnlyContext:
    def __init__(self):
        self.mutable = False

    def enforce(self, operation: str):
        if operation in ("embed", "write", "mutate"):
            raise RuntimeError("READ-ONLY MODE VIOLATION")
        # queries are allowed
        return True
