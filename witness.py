#!/usr/bin/env python3
"""claimed-metrics-witness — honesty labeling for benchmark claims.

Every performance claim gets one of three states:
    self-claimed  -> written down by the claimant, not independently checked
    verified      -> reproduced by a witness (a recorded run with repro command)
    retracted     -> withdrawn by the claimant, with reason preserved

A hash-chained witness log (each entry commits to the previous hash) makes
silent edits detectable: audit() recomputes the chain and reports tampering.
Inspired by the meta-transparency practice of projects that publicly separate
"which of our numbers are real" from "which we wished were real".

Pure stdlib. State = one JSON file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

VERSION = "0.1.1"
STATES = ("self-claimed", "verified", "retracted")


class WitnessError(Exception):
    pass


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


class WitnessChain:
    def __init__(self, path: str):
        self.path = path
        self.data = {"version": VERSION, "entries": [], "genesis": "0" * 64}
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                raise WitnessError(f"corrupted chain file: {exc}") from exc

    # ---------------- write path (every append commits to prev hash)
    def _append(self, entry: dict):
        prev = self.data["entries"][-1]["hash"] if self.data["entries"] else self.data["genesis"]
        entry = {"seq": len(self.data["entries"]), "prev": prev,
                 "ts": time.time(), **entry}
        entry["hash"] = _h({k: v for k, v in entry.items() if k != "hash"})
        self.data["entries"].append(entry)
        self._persist()

    def _persist(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def claim(self, metric: str, value: str, unit: str = "",
              state: str = "self-claimed", repro: str = "") -> dict:
        if state not in STATES:
            raise WitnessError(f"state must be one of {STATES}")
        if not metric.strip() or not str(value).strip():
            raise WitnessError("metric and value required")
        self._append({"action": "claim", "metric": metric, "value": str(value),
                      "unit": unit, "state": state, "repro": repro})
        return {"ok": True, "state": state}

    def verify(self, metric: str, evidence: str) -> dict:
        if not evidence.strip():
            raise WitnessError("verify requires evidence (e.g. repro command + run output)")
        self._append({"action": "verify", "metric": metric, "evidence": evidence})
        return {"ok": True}

    def retract(self, metric: str, reason: str) -> dict:
        if not reason.strip():
            raise WitnessError("retract requires a reason")
        self._append({"action": "retract", "metric": metric, "reason": reason})
        return {"ok": True}

    # ---------------- read path
    def current(self) -> dict:
        """Latest state per metric, considering the full entry sequence."""
        out: dict = {}
        for e in self.data["entries"]:
            if e["action"] == "claim":
                out[e["metric"]] = {"state": e["state"], "value": e["value"],
                                    "unit": e.get("unit", ""), "repro": e.get("repro", "")}
            elif e["action"] == "verify":
                if e["metric"] in out:
                    out[e["metric"]]["state"] = "verified"
                    out[e["metric"]]["evidence"] = e.get("evidence", "")
            elif e["action"] == "retract":
                if e["metric"] not in out:  # retraction of an unrecorded metric stays visible
                    out[e["metric"]] = {"state": "retracted", "value": None,
                                        "unit": "", "repro": ""}
                out[e["metric"]]["state"] = "retracted"
                out[e["metric"]]["retraction_reason"] = e.get("reason", "")
        return out

    def audit(self) -> dict:
        """Recompute the hash chain; report any tampering."""
        prev = self.data["genesis"]
        bad = []
        for i, e in enumerate(self.data["entries"]):
            if e.get("prev") != prev:
                bad.append({"seq": i, "problem": "prev-hash mismatch"})
                prev = e.get("hash", prev)
                continue
            expect = _h({k: v for k, v in e.items() if k != "hash"})
            if e.get("hash") != expect:
                bad.append({"seq": i, "problem": "entry hash mismatch (edited in place?)"})
            prev = e.get("hash", prev)
        counts = {"self-claimed": 0, "verified": 0, "retracted": 0}
        for m in self.current().values():
            counts[m["state"]] = counts.get(m["state"], 0) + 1
        return {"intact": not bad, "tampering": bad, "state_counts": counts,
                "entries": len(self.data["entries"])}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="claimed-metrics-witness",
                                description="three-state honesty labeling with a hash-chained witness log")
    p.add_argument("--chain", default="witness.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("claim", help="register a metric claim")
    c.add_argument("--metric", required=True)
    c.add_argument("--value", required=True)
    c.add_argument("--unit", default="")
    c.add_argument("--state", default="self-claimed", choices=STATES)
    c.add_argument("--repro", default="")
    v = sub.add_parser("verify", help="record witness verification")
    v.add_argument("--metric", required=True)
    v.add_argument("--evidence", required=True)
    r = sub.add_parser("retract", help="withdraw a claim (reason kept)")
    r.add_argument("--metric", required=True)
    r.add_argument("--reason", required=True)
    a = sub.add_parser("audit", help="verify chain integrity + state counts")
    cur = sub.add_parser("current", help="latest state per metric")

    a2 = p.parse_args(argv)
    try:
        w = WitnessChain(a2.chain)
        if a2.cmd == "claim":
            print(json.dumps(w.claim(a2.metric, a2.value, a2.unit, a2.state, a2.repro)))
        elif a2.cmd == "verify":
            print(json.dumps(w.verify(a2.metric, a2.evidence)))
        elif a2.cmd == "retract":
            print(json.dumps(w.retract(a2.metric, a2.reason)))
        elif a2.cmd == "audit":
            print(json.dumps(w.audit(), indent=2))
        elif a2.cmd == "current":
            print(json.dumps(w.current(), indent=2))
        return 0
    except WitnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
