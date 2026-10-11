#!/usr/bin/env python3
"""self_test for claimed-metrics-witness. Three classes (rule 97).
Run: python self_test.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import witness as m  # noqa: E402

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))


def main() -> int:
    td = tempfile.mkdtemp()
    path = os.path.join(td, "w.json")
    w = m.WitnessChain(path)

    # ---------------- A. functional
    w.claim("tokens_per_query", "436", "tok", repro="python bench.py")
    w.claim("recall_quality", "high", state="self-claimed")
    w.verify("tokens_per_query", "python self_test.py; 5-query table printed")
    cur = w.current()
    check("A1 verified claim flips state",
          cur["tokens_per_query"]["state"] == "verified")
    check("A2 unverified stays self-claimed",
          cur["recall_quality"]["state"] == "self-claimed")
    check("A3 evidence recorded", "self_test" in cur["tokens_per_query"].get("evidence", ""))
    w.retract("old_latency", "measured on wrong hardware; figure misleading")
    cur = w.current()
    check("A4 retract flips state and keeps reason",
          cur["old_latency"]["state"] == "retracted"
          and "wrong hardware" in cur["old_latency"]["retraction_reason"])
    aud = w.audit()
    check("A5 audit intact on clean chain", aud["intact"] is True, str(aud))
    check("A6 state counts correct",
          aud["state_counts"] == {"self-claimed": 1, "verified": 1, "retracted": 1})
    check("A7 chain length = 4 entries", aud["entries"] == 4)

    # ---------------- B. error paths
    try:
        w.claim("", "1")
        check("B1 empty metric rejected", False)
    except m.WitnessError:
        check("B1 empty metric rejected", True)
    try:
        w.claim("x", "1", state="trusted")  # not a legal state
        check("B2 illegal state rejected", False)
    except m.WitnessError:
        check("B2 illegal state rejected", True)
    try:
        w.verify("x", "  ")
        check("B3 empty evidence rejected", False)
    except m.WitnessError:
        check("B3 empty evidence rejected", True)
    try:
        w.retract("x", "")
        check("B4 empty reason rejected", False)
    except m.WitnessError:
        check("B4 empty reason rejected", True)
    corrupt = os.path.join(td, "corrupt.json")
    with open(corrupt, "w") as f:
        f.write("{not json")
    try:
        m.WitnessChain(corrupt)
        check("B5 corrupted chain file rejected", False)
    except m.WitnessError:
        check("B5 corrupted chain file rejected", True)

    # tampering detection
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data["entries"][1]["value"] = "999999"  # silent edit of a recorded claim
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    aud = m.WitnessChain(path).audit()
    check("B6 tampered entry detected", aud["intact"] is False
          and any(t["problem"] for t in aud["tampering"]))

    # ---------------- C. extreme edges
    empty = m.WitnessChain(os.path.join(td, "empty.json"))
    check("C1 empty chain audits clean with zero counts",
          empty.audit()["intact"] and empty.audit()["state_counts"]["verified"] == 0)
    check("C2 current() on empty chain is {}", empty.current() == {})
    long_reason = "r" * 100_000
    empty.retract("big", long_reason)
    check("C3 100KB reason survives round-trip",
          len(empty.current()["big"]["retraction_reason"]) == 100_000)
    empty.claim("unicode- Métrica", "1.5", unit="µs")
    check("C4 unicode metric handled",
          empty.current()["unicode- Métrica"]["value"] == "1.5")
    empty.verify("unicode- Métrica", "ok")
    check("C5 unicode verify flips state",
          empty.current()["unicode- Métrica"]["state"] == "verified")
    check("C6 CLI audit exits 0 on clean chain",
          m.main(["--chain", os.path.join(td, "empty.json"), "audit"]) == 0)

    fails = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
    print(f"\ntotal={len(RESULTS)} pass={len(RESULTS)-len(fails)} fail={len(fails)}")
    print("repro: python self_test.py")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
