#!/usr/bin/env python3
"""DecAI Fit — reference scoring implementation.

Computes the DecAI Fit score (0-6) from a verified flag set, applying the
fixed formulas, anti-manipulation caps, and staleness penalty specified in
``methodology/scoring.md``. Pure standard library; Python 3.9+.

Usage:
    python decai_fit.py CARD.json [CARD2.json ...]
    python decai_fit.py --json CARD.json        # machine-readable output

Input format: see ``schema/decai_fit_input.schema.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

FLAG_NAMES = (
    "AI_0", "AI_1", "AI_2", "AI_3", "AI_4",
    "OC_1", "OC_2", "OC_3",
    "TK_0", "TK_1", "TK_2", "TK_3", "TK_4",
    "E_AI_T1", "E_OC_T1", "E_TK_T1", "E_only_T3",
)

STALENESS_THRESHOLD_DAYS = 550

LEVEL_LABELS = {
    0: "no verified AI reality and no AI intent",
    1: "low alignment with the Decentralized AI thesis",
    2: "low alignment with the Decentralized AI thesis",
    3: "medium alignment with the Decentralized AI thesis",
    4: "medium alignment with the Decentralized AI thesis",
    5: "high alignment with the Decentralized AI thesis",
    6: "high alignment with the Decentralized AI thesis",
}


@dataclass
class ScoreResult:
    project_id: str
    ai_score: int
    onchain_score: int
    token_score: int
    evidence_score: int
    total: int
    base: int
    caps_applied: list  # list[str], e.g. ["R2 (missing core evidence): cap 3"]
    effective_cap: int
    stale: bool
    last_verified_days: int
    final: int
    label: str = ""
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "components": {
                "ai_score": self.ai_score,
                "onchain_score": self.onchain_score,
                "token_score": self.token_score,
                "evidence_score": self.evidence_score,
            },
            "total": self.total,
            "base": self.base,
            "caps_applied": self.caps_applied,
            "effective_cap": self.effective_cap,
            "stale": self.stale,
            "last_verified_days": self.last_verified_days,
            "decai_fit": self.final,
            "label": self.label,
            "warnings": self.warnings,
        }


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _validate(flags: dict, warnings: list) -> None:
    """Consistency checks. Violations do not stop scoring but are reported."""
    if flags["TK_0"] == 1 and any(flags[f] for f in ("TK_1", "TK_2", "TK_3", "TK_4")):
        warnings.append(
            "TK_0=1 (no token) but other TK_* flags are set; they are ignored by the formula."
        )
    if flags["AI_0"] == 1 and any(flags[f] for f in ("AI_1", "AI_2", "AI_3", "AI_4")):
        warnings.append(
            "AI_0=1 requires AI_1..AI_4 = 0 by operational definition (intent-only declaration)."
        )
    if flags["E_only_T3"] == 1 and any(flags[f] for f in ("E_AI_T1", "E_OC_T1", "E_TK_T1")):
        warnings.append(
            "E_only_T3=1 contradicts Tier-1 coverage flags (E_*_T1=1); check the source inventory."
        )


def score(card: dict) -> ScoreResult:
    """Compute DecAI Fit for one scoring-input record (validated upstream)."""
    missing = [k for k in ("project_id", "flags", "last_verified_days") if k not in card]
    if missing:
        raise ValueError(f"missing required keys: {', '.join(missing)}")

    flags = card["flags"]
    missing_flags = [f for f in FLAG_NAMES if f not in flags]
    if missing_flags:
        raise ValueError(f"missing flags: {', '.join(missing_flags)}")
    for name in FLAG_NAMES:
        if flags[name] not in (0, 1):
            raise ValueError(f"flag {name} must be 0 or 1, got {flags[name]!r}")

    days = card["last_verified_days"]
    if not isinstance(days, int) or days < 0:
        raise ValueError(f"last_verified_days must be a non-negative integer, got {days!r}")

    warnings: list = []
    _validate(flags, warnings)

    # --- Block scores (0-3 each) -------------------------------------------
    a = min(3, flags["AI_0"] + flags["AI_1"] + flags["AI_2"] + flags["AI_3"] + flags["AI_4"])
    o = min(3, flags["OC_1"] + flags["OC_2"] + flags["OC_3"])
    if flags["TK_0"] == 1:
        t = 2
    else:
        t = _clamp(flags["TK_1"] + flags["TK_2"] + flags["TK_3"] - flags["TK_4"], 0, 3)
    e = min(3, flags["E_AI_T1"] + flags["E_OC_T1"] + flags["E_TK_T1"])

    # --- Base index (1-6) ---------------------------------------------------
    total = a + o + t + e  # 0..12
    base = max(1, (total + 1) // 2)  # 0-2 -> 1, 3-4 -> 2, ..., 11-12 -> 6

    # --- Anti-manipulation caps (R1-R4) --------------------------------------
    caps_applied: list = []
    cap = 6
    if flags["E_only_T3"] == 1:
        cap = 2
        caps_applied.append("R1 (Tier-3-only sources): cap 2")
    elif flags["E_AI_T1"] == 0 or flags["E_OC_T1"] == 0:
        cap = 3
        caps_applied.append("R2 (missing Tier-1 evidence for AI or onchain): cap 3")
    elif flags["TK_0"] == 0 and flags["E_TK_T1"] == 0:
        cap = 4
        caps_applied.append("R3 (token present without Tier-1 token evidence): cap 4")

    ai_cap = {1: 3, 2: 5, 3: 6}.get(a, 6)
    if a > 0 and ai_cap < cap:
        cap = ai_cap
        caps_applied.append(f"R4 (AI-reality cap for ai_score={a}): cap {ai_cap}")

    capped = min(base, cap)

    # --- R0 zero-forcing and staleness penalty -------------------------------
    stale = days > STALENESS_THRESHOLD_DAYS
    if a == 0:
        final = 0
        caps_applied.append("R0 (ai_score=0): DecAI Fit forced to 0")
    elif stale:
        final = max(1, capped - 1)
    else:
        final = capped

    return ScoreResult(
        project_id=card["project_id"],
        ai_score=a,
        onchain_score=o,
        token_score=t,
        evidence_score=e,
        total=total,
        base=base,
        caps_applied=caps_applied,
        effective_cap=cap,
        stale=stale,
        last_verified_days=days,
        final=final,
        label=LEVEL_LABELS[final],
        warnings=warnings,
    )


def format_report(result: ScoreResult) -> str:
    lines = [
        f"Project: {result.project_id}",
        f"  AI reality      a = {result.ai_score}/3",
        f"  Onchain         o = {result.onchain_score}/3",
        f"  Token           t = {result.token_score}/3",
        f"  Evidence        e = {result.evidence_score}/3",
        f"  Sum S = {result.total}  ->  base = {result.base}",
    ]
    if result.caps_applied:
        lines.append("  Caps applied: " + "; ".join(result.caps_applied))
    else:
        lines.append(f"  Caps applied: none (effective cap = {result.effective_cap})")
    freshness = "STALE" if result.stale else "fresh"
    lines.append(f"  Staleness: {freshness} ({result.last_verified_days} days)")
    lines.append(f"  DecAI Fit: {result.final}/6 — {result.label}")
    for warning in result.warnings:
        lines.append(f"  WARNING: {warning}")
    return "\n".join(lines)


def main(argv: list) -> int:
    # Keep output readable on consoles with legacy code pages (e.g. Windows cp1251).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="DecAI Fit reference scorer")
    parser.add_argument("cards", nargs="+", help="path(s) to scoring-input JSON file(s)")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    # Expand glob patterns ourselves: PowerShell/cmd do not expand them for us.
    paths = []
    for pattern in args.cards:
        if any(ch in pattern for ch in "*?["):
            matches = sorted(Path().glob(pattern))
            if not matches:
                print(f"error: no files match pattern {pattern!r}", file=sys.stderr)
                return 1
            paths.extend(matches)
        else:
            paths.append(Path(pattern))

    results = []
    for path in paths:
        try:
            card = json.loads(path.read_text(encoding="utf-8"))
            results.append(score(card))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {path}: {exc}", file=sys.stderr)
            return 1

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(format_report(r) for r in results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
