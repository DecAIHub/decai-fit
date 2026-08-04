# Examples — Expected Outputs

Four fictional projects illustrating the scoring bands and the anti-manipulation caps. Score them all:

```bash
python ../scorer/decai_fit.py *.json
```

| File | Scenario | a / o / t / e | S | Base | Caps | DecAI Fit |
|---|---|---|---|---|---|---|
| `strong_project.json` | Full-stack DeAI protocol: verified AI (description + demo + metrics + architecture), load-bearing onchain, functional token, Tier-1 evidence everywhere | 3 / 3 / 2 / 3 | 11 | 6 | none | **6/6 — high** |
| `mid_project.json` | Honest AI service without a token: real AI (described + demo), useful onchain logic, Tier-1 for AI and onchain | 2 / 2 / 2 / 2 | 8 | 4 | R4 (effective cap 5, not binding) | **4/6 — medium** |
| `weak_project.json` | Marketing-first project: AI only as a roadmap intent, onchain = token issuance, replaceable token, Tier-3 sources only | 1 / 1 / 0 / 0 | 2 | 1 | R1 (Tier-3-only → cap 2) | **1/6 — low** |
| `zero_project.json` | No AI reality and no Tier-1 AI intent: whatever the onchain and token mechanics, the project is not a Decentralized-AI project as of the review date | 0 / 2 / 1 / 1 | 4 | 2 | R2, then **R0 forces 0** | **0/6** |

Note how the caps, not the averages, carry the anti-manipulation weight: `zero_project` has decent onchain mechanics and would reach 2/6 by arithmetic alone, but zero verified AI reality forces 0/6 — a project cannot buy a "Decentralized AI" label with token engineering.
