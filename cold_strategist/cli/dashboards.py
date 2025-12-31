import os
import json
import argparse
from tabulate import tabulate
from core.analytics.book_tracker import BookInfluenceTracker

BASE = os.path.join("data", "telemetry")


def load(name):
    path = os.path.join(BASE, f"{name}.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def show_minister_influence():
    rows = []
    for e in load("minister_events"):
        rows.append([e.get("minister"), e.get("stance"), e.get("confidence"), e.get("decision_id")])
    print(tabulate(rows, headers=["Minister", "Stance", "Conf.", "Decision"]))


def show_overrides():
    rows = []
    for e in load("override_events"):
        rows.append([e.get("override_type"), e.get("was_emotional"), e.get("decision_id")])
    print(tabulate(rows, headers=["Type", "Emotional", "Decision"]))


def show_war_traces():
    rows = []
    for e in load("rag_traces"):
        rows.append([e.get("source_book"), e.get("chapter"), e.get("principle"), e.get("minister_interpretation"), e.get("relevance_score")])
    print(tabulate(rows, headers=["Book", "Chapter", "Principle", "Interpretation", "Score"]))


def show_outcomes():
    rows = []
    for e in load("outcome_events"):
        rows.append([e.get("decision_id"), e.get("satisfaction_score"), e.get("regret_flag"), e.get("observed_outcome")])
    print(tabulate(rows, headers=["Decision", "Satisfaction", "Regret", "Outcome"]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("view", choices=["ministers", "overrides", "war", "rag", "outcomes", "books"], help="Which dashboard to show")
    args = p.parse_args()

    if args.view == "ministers":
        show_minister_influence()
    elif args.view == "overrides":
        show_overrides()
    elif args.view == "war":
        show_war_traces()
    elif args.view == "rag":
        show_war_traces()
    elif args.view == "outcomes":
        show_outcomes()
    elif args.view == "books":
        show_books()


def show_books():
    tracker = BookInfluenceTracker()
    summary = tracker.summarize()
    top = summary.get("top_books", []) if isinstance(summary, dict) else []
    rows = [[b, s] for b, s in top]
    print(tabulate(rows, headers=["Book", "Effectiveness"]))


if __name__ == "__main__":
    main()
