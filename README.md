# claimed-metrics-witness

A three-state honesty ledger for project metrics: every claim is `self-claimed`, `verified`, or `retracted`, recorded in a hash-chained witness log that makes silent edits detectable. If your README states performance numbers, this turns them into accountable, auditable statements.

**Confidence: High (≥80%)** for the tamper-evidence property — the hash chain is recomputed by `audit()`, and self_test B6 proves an edited entry is caught. **Confidence: Medium (60–79%)** that teams sustain the discipline over time; the tool makes honesty cheap, not inevitable.

## Problem

README performance numbers decay quietly. A benchmark gets re-run on new hardware, an over-eager figure survives review, and six months later nobody remembers which numbers were ever real. Vector databases and dev tools repeatedly ship claims that later get walked back — but the walk-back is a buried commit, not structured data.

The overlooked angle: a small but notable practice from high-star sensor projects is publishing a *witness chain* — explicitly separating "which numbers are real" from "which we wished were real," with third-party verification recorded. That separation is generic engineering metadata, not a sensor thing. Make it a tool: **claims with states, states with history, history with tamper evidence.**

## How it works

- `claim` registers a metric with a state (`self-claimed` by default) and optionally a repro command.
- `verify` records witness evidence (a repro command + observed output) and flips the metric to `verified`.
- `retract` withdraws a claim but **preserves the reason** — retracted numbers stay visible as retracted, instead of vanishing.
- Every entry is appended to a SHA-256 hash chain (each entry commits to the previous hash). `audit` recomputes the chain and reports any in-place editing, plus current state counts.

## Quickstart

Stage 1 — minimal example (~5 s):

```bash
python witness.py claim --metric tokens_per_query --value 436 --unit tok --repro "python bench.py"
python witness.py verify --metric tokens_per_query --evidence "bench.py run at commit abc"
python witness.py current
```

Stage 2 — full self-test incl. tamper detection (~5 s):

```bash
python self_test.py    # 22 checks
```

## Why not X

| Alternative | Why not | What we keep instead |
|---|---|---|
| "Just update the README" | History is lost; a wrong number leaves no trace of what it claimed before | Append-only chain; retracted claims stay visible with reasons |
| Full CI benchmark gating | Heavy infrastructure; still doesn't label *which* numbers are verified in prose | One JSON file, no runner required |
| Signed releases only | Signs the code, not the *claims* in it | Claim-level state + evidence per metric |

## Minimal Fallback

No tooling? Add a table to your README with one extra column:

```markdown
| metric        | value | state        | evidence            |
|---------------|-------|--------------|---------------------|
| tokens/query  | 436   | verified     | self_test.py output |
| recall        | high  | self-claimed | —                   |
```

You lose tamper evidence and history; you keep the three-state discipline, which is most of the value.

## Design Trade-offs

Priority: **honesty > auditability > simplicity > convenience**. Consequences:

- Append-only: corrections are new entries, not edits. Verbose history is the price of a truthful one.
- No crypto-grade security: SHA-256 chaining detects *accidental* or casual tampering by anyone holding the file; a determined editor can rewrite the whole chain including genesis. This is an honesty aid, not a notarization service.
- `verify` trusts whoever runs it; the evidence string is the record, not proof.

## Limits & Second-order Effects

- The ledger is only as honest as its writer — it cannot stop a claim from being verified sloppily.
- Second-order effect: three-state labels can become ritual (everything "verified" by the author's own bench). Require a second party or an independent repro for the verified state where it matters.
- Second-order effect: a public retraction ledger builds trust, but if only failures are logged while successes go unverified, the ledger reads pessimistically. Audit counts make the balance visible.
- Genesis is hardcoded; cross-file chains are out of scope.

## FAQ

**Q: Is the chain cryptographically secure?**
A: It detects silent *edits* to a file you keep, not malicious rewrites of the entire file. For real non-repudiation, anchor the head hash externally (git commit, timestamping service).

**Q: Who is the "witness"?**
A: Anyone who runs your repro and records the output. The tool structures the record; it doesn't certify the witness.

**Q: When you should NOT use this tool?**
A: If your metrics are all generated and checked in CI automatically, the ledger adds ceremony with no new information. Also skip it if you won't act on `retracted` — a retraction nobody reads is decoration.

## [Core Assumptions]

1. Publicly separating claim states (claimed/verified/retracted) improves trust more than the cost of maintaining it.
2. Most metric corruption is *accidental drift* (stale numbers after re-runs), which append-only history catches.
3. A repro command + recorded output is adequate evidence granularity for project-level claims.
4. Single-file JSON state fits the scale of a project's metric claims (hundreds, not millions).

---

All self-test results [measured] locally via `python self_test.py`; no external benchmarks cited. As of 2026-10-11. License: MIT (zhengming contributors).
