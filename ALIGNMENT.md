# Alignment Audit (Rules 85-100 / 16 items)

Repo: claimed-metrics-witness · Audited: 2026-10-11 · v0.1.1

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Safety/Ethics section | N/A | Integrity tooling; no security-domain content. |
| 2 | Privacy/zero secrets | PASS | No keys/tokens/real names; chain stores user-supplied strings only. |
| 3 | Copyright boundary | PASS | Witness-chain practice re-described generically; no copied text >50 chars; MIT LICENSE present. |
| 4 | Fact-source labeling | PASS | All self-test results [measured] with repro; no external numbers cited. |
| 5 | Confidence grading | PASS | Tamper-detection claim High (test B6); discipline-sustainability claim Medium. |
| 6 | Minimal Fallback | PASS | README three-state table. |
| 7 | Quickstart timing | PASS | ~5 s stages + ~5 s self-test. |
| 8 | Design trade-offs/priorities | PASS | honesty > auditability > simplicity > convenience; append-only cost stated. |
| 9 | CHANGELOG ≥2 iterations | PASS | v0.1.0 → v0.1.1 security-claim precision delta (~25% correctness). |
| 10 | Exemption (session rule) | N/A | Session-level; static repo. |
| 11 | Time-sensitive data dated | PASS | Footer "as of 2026-10-11". |
| 12 | Core assumptions ≥3 | PASS | 4 assumptions at README end. |
| 13 | Three-class self-test | PASS | A functional (7), B error paths (6 incl. tamper detection), C edges (6); all PASS. Repro: `python self_test.py`. |
| 14 | When NOT to use | PASS | FAQ Q3: CI-gated metrics; unused retractions. |
| 15 | ≥2 iterations traceable | PASS | v0.1.1 correctness delta documented in CHANGELOG. |
| 16 | ≤60-word first screen | PASS | First paragraph 52 words with a "turns them into accountable statements" judgment. |
