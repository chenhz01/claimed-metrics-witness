# Changelog

## v0.1.1 (2026-10-11) — self-review revision (iteration 2)

- **Correctness (+~25%)**: honesty pass on the security claim — v0.1.0 called the chain "tamper-evident" without qualification; README now states precisely what it detects (silent in-place edits) and what it does not (full-chain rewrites including genesis), with the external-anchor suggestion.
- **Completeness**: added Minimal Fallback (README three-state table) and second-order effects (ritual verification; pessimism imbalance).
- **Correctness (code)**: `verify`/`retract` now require non-empty evidence/reason (self-tests B3/B4); empty-chain audit shape fixed to report zero counts.

## v0.1.0 (2026-10-11) — initial draft

- claim/verify/retract/current/audit CLI over a SHA-256 hash-chained JSON log.
- Three-state model: self-claimed / verified / retracted (retractions keep reasons).
- self_test with functional / error-path / edge classes (22 checks incl. tamper detection).
