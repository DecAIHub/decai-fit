# DecAI Fit — Open Scoring Methodology & Reference Implementation

**DecAI Fit** is a composite 0–6 index measuring how well an AI-branded crypto project aligns with the *Decentralized AI* thesis — scored strictly against a tiered evidence model and designed to resist AI-washing, onchain-washing, and token-washing.

This repository contains the **full scoring methodology** and a **deterministic reference scorer**: given a card's binary evidence flags, it computes the DecAI Fit score with a complete per-rule breakdown. Any published score can be recomputed from its flag set, so the registry's arithmetic is verifiable by any third party.

> **Not financial advice.** DecAI Fit measures the *verifiability of a project's claims*, not investment attractiveness, price potential, or timing. See [Disclaimer](#disclaimer).

## The DecAIHub research program

| Artifact | What it is | Where |
|---|---|---|
| **Registry** | Free public verification registry of AI-branded crypto projects | [decaihub.io](https://decaihub.io) · [project cards](https://decaihub.io/wiki/en/projects) |
| **Methodology (reader's guide)** | DecAI Fit explained on the registry site | [DecAI Fit Metric](https://decaihub.io/wiki/en/decaihub-materials/decai-fit-metric) |
| **Dataset** | AI–Blockchain Project-Card Dataset (ABPC) v1.1.0 - 845 cards, 4,371 evidence entries (CC BY 4.0) | [Zenodo, DOI 10.5281/zenodo.22800707](https://doi.org/10.5281/zenodo.22800707) |
| **Data paper** | Peer-reviewed descriptor of the dataset | [IEEE Data Descriptions, DOI 10.1109/IEEEDATA.2026.3740408](https://doi.org/10.1109/IEEEDATA.2026.3740408) |
| **Replication packages** | Code & materials for the peer-reviewed papers | [DecAIHub/papers](https://github.com/DecAIHub/papers) |
| **Methodology + scorer** | This repository | you are here |

## Quick start

No dependencies beyond Python 3.9+ standard library.

```bash
python scorer/decai_fit.py examples/strong_project.json
```

```text
Project: example-strong-project
  AI reality      a = 3/3
  Onchain         o = 3/3
  Token           t = 2/3
  Evidence        e = 3/3
  Sum S = 11  ->  base = 6
  Caps applied: none (effective cap = 6)
  Staleness: fresh (120 days)
  DecAI Fit: 6/6 — high alignment with the Decentralized AI thesis
```

Score every example at once:

```bash
python scorer/decai_fit.py examples/*.json
```

Run the test suite:

```bash
python scorer/test_decai_fit.py
```

## Repository map

```
decai-fit/
├── README.md                          # this file
├── LICENSE                            # MIT (code) — dataset is CC-BY 4.0 on Zenodo
├── CITATION.cff                       # how to cite
├── methodology/
│   ├── scoring.md                     # the full algorithm: flags, formulas, caps, penalty
│   ├── evidence-tiers.md              # Tier-1 / Tier-2 / Tier-3 source model
│   └── pipeline.md                    # how cards are produced (extraction → verification → scoring)
├── schema/
│   └── decai_fit_input.schema.json    # JSON Schema for scorer input
├── scorer/
│   ├── decai_fit.py                   # reference implementation (pure stdlib)
│   └── test_decai_fit.py              # test suite
└── examples/
    ├── README.md                      # expected outputs table
    ├── zero_project.json              # ai_score = 0  ->  DecAI Fit 0/6
    ├── weak_project.json              # marketing-only evidence  ->  1/6
    ├── mid_project.json               # honest service, no token  ->  4/6
    └── strong_project.json            # full-stack DeAI protocol  ->  6/6
```

## How the score works (one paragraph)

A project card carries binary flags in four blocks — **AI reality** (what the AI verifiably does), **Onchain necessity** (whether blockchain is load-bearing), **Token necessity** (whether the token has a real function), and **Evidence** (Tier-1 proof coverage). Block scores (0–3 each) sum to a base index mapped to 1–6, after which **anti-manipulation caps** are applied: marketing-only sourcing caps the score at 2; missing Tier-1 evidence for AI or onchain claims caps it at 3; an unverified token caps it at 4; a shallow AI-reality score caps the total regardless of other strengths; and **zero verified AI reality forces the score to 0**. Cards not re-verified within 550 days take a staleness penalty. Every rule can only *lower* the score — under missing or conflicting evidence the methodology defaults to the conservative value. Full specification: [`methodology/scoring.md`](methodology/scoring.md).

## Design principles

1. **Deterministic and recomputable.** The score is a fixed function of the card's flags. No judgment calls hide in the arithmetic — they are confined to flag assignment, which is governed by operational definitions ([`methodology/scoring.md`](methodology/scoring.md), §Operational definitions) and requires a cited justification for every `1`.
2. **Evidence-gated.** Claims are scored only against the tiered source model ([`methodology/evidence-tiers.md`](methodology/evidence-tiers.md)): Tier-1 proofs > Tier-2 context > Tier-3 noise. Marketing never raises a flag.
3. **Conservative under uncertainty.** Missing basis, conflicting sources, unclear attribution → flag stays 0, with a note of what would need to be provided to change it.
4. **Caps over averages.** Aggregation must not let strong token mechanics mask absent AI reality — hence hard caps instead of compensatory averaging.

## Relationship to the published dataset

The public dataset ([DOI 10.5281/zenodo.18900950](https://doi.org/10.5281/zenodo.18900950)) ships project cards conforming to the [project-card schema](https://github.com/DecAIHub/papers/tree/main/project-card-schema) (passport, links, tiered evidence entries). This repository adds the **scoring layer**: the input schema ([`schema/decai_fit_input.schema.json`](schema/decai_fit_input.schema.json)) describes the flag set derived from a card during verification, and the scorer turns those flags into the published 0–6 score. The production process from raw sources to flags is documented in [`methodology/pipeline.md`](methodology/pipeline.md).

## Disclaimer

DecAI Fit and DecAIHub project pages evaluate the **verifiability and evidential support of a project's public claims** and the risk of AI-washing. They do not assess profitability, token price, or timing, and must not be read as investment advice or a recommendation to buy, hold, or sell any asset.

## Citing

See [`CITATION.cff`](CITATION.cff). The dataset and methodology are described in the accompanying data paper (under review); until it is published, please cite the Zenodo deposit:

> Kadochnikov, N. (2026). *AI–Blockchain Project-Card Dataset* (v1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18900950

## License

Code and methodology text in this repository: [MIT](LICENSE). The dataset is distributed separately on Zenodo under CC-BY 4.0.
