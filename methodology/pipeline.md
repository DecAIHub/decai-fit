# Card Production Pipeline — from Raw Sources to a Scored Card

This document describes how DecAIHub project cards are produced. The pipeline separates **judgment-free arithmetic** (the deterministic scoring specification implemented in this repository) from **evidence collection and flag assignment**, which are governed by the operational definitions in [`scoring.md`](scoring.md) and subject to human verification on a selective basis.

## Stages

```
1. Discovery          2. Source mapping        3. Extraction            4. Verification         5. Scoring
   candidate             per-project link         LLM-assisted             flags set per           deterministic
   projects with   ->    inventory, each    ->    parsing of linked   ->   operational defs;  ->   DecAI Fit
   an AI claim           source tier-labeled      sources against          selective human         computation
                         (Tier-1/2/3)             the flag criteria        review                  (fixed formulas)
```

### 1. Discovery

The candidate pool is assembled by exhaustively collecting projects that publicly present a **crypto + AI claim** — from aggregators, ecosystem catalogues, and direct search. Presence of an AI claim (not its validity) is the inclusion criterion; validity is what the card then measures.

### 2. Source mapping

For each project, an inventory of public sources is built and each source is labeled with an evidence tier per [`evidence-tiers.md`](evidence-tiers.md). Tier labels are assigned by source *class* (e.g., official docs = Tier-1, aggregator = Tier-2, influencer post = Tier-3), not by how favorable the content is.

### 3. LLM-assisted extraction

An LLM agent parses the collected sources and extracts candidate facts relevant to each 0/1 flag: what the AI component is claimed to do, contract addresses, token functions, published metrics, audit references, and so on. The agent's role is **extraction and structuring only** — surfacing candidate justifications with their source URLs. It does not assign final flags and cannot raise a score.

### 4. Flag assignment and verification

Flags are assigned strictly against the operational definitions, with the extracted materials as input:

- each `1` requires a recorded justification (link + short fact/quote);
- missing basis, source conflicts (`CONFLICT`), or unclear attribution default the flag to `0`;
- the AI-washing red-flag checklist (see [`scoring.md`](scoring.md)) raises the evidence bar where triggered.

Human verification is applied **selectively** (spot checks of assigned flags against their recorded justifications), not exhaustively per flag. The conservative defaults above are what makes this workable: under missing or ambiguous evidence a flag is `0` by rule, so assignment errors are biased toward *under*-scoring rather than over-scoring, and any card's flag set can be challenged and re-verified against its recorded justifications at any time.

This stage embodies the **conservative-under-uncertainty** principle: the burden of proof is on the claim, not on the reviewer.

### 5. Deterministic scoring

The assigned flag set is scored by the fixed formulas and caps specified in [`scoring.md`](scoring.md). The scorer in this repository ([`../scorer/decai_fit.py`](../scorer/decai_fit.py)) is the **reference implementation** of that specification — production scores are computed by tooling implementing the same formulas. Because this step is pure arithmetic, **any card's score can be recomputed from its flag set by any third party**, confirming that the registry applies its own rules.

## Re-verification and staleness

Cards carry a `Last verified` date. A card not re-verified within **550 days** takes an automatic score penalty (see [`scoring.md`](scoring.md), §5) — registries die of staleness, and an outdated verification must not masquerade as a current one.

## Transparency notes

- The use of LLM assistance in the extraction stage is disclosed here deliberately: it is how the registry scales to hundreds of cards while keeping every flag justified by a recorded source and every scoring step reproducible by rule. Human verification is selective by design; the recorded justification chain is what makes any card auditable after the fact.
- The published dataset ([DOI 10.5281/zenodo.18900950](https://doi.org/10.5281/zenodo.18900950)) includes the evidence entries (source URL + tier + verification date where recorded) for every card — 4,353 entries across 845 cards — so the justification chain is inspectable end to end.
