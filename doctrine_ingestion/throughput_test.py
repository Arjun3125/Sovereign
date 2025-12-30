import time
from concurrent.futures import ProcessPoolExecutor, as_completed

# swap this import to test real vs mock
from llm_client import call_llm
# from llm_client_mock import call_llm


PROMPT = """
Return STRICT JSON:
{
  "principles": [],
  "claims": [],
  "rules": [],
  "warnings": [],
  "cross_references": []
}
TEXT:
Dummy text for throughput test.
"""


def worker(_):
    return call_llm(PROMPT)


def run_test(workers: int, jobs: int = 12):
    start = time.time()

    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(worker, i) for i in range(jobs)]
        for _ in as_completed(futures):
            pass

    total = time.time() - start
    print(
        f"workers={workers} | "
        f"jobs={jobs} | "
        f"total={total:.2f}s | "
        f"avg/job={total/jobs:.2f}s"
    )


if __name__ == "__main__":
    for w in [1, 2, 3, 4, 5, 6]:
        run_test(w)
