# DecAI Fit — Scoring Specification

DecAI Fit is a composite index on a 0–6 scale representing a crypto project's alignment with the principles of Decentralized Artificial Intelligence (DeAI). The metric is strictly constrained by the quality of provided evidence and is designed to resist manipulation (AI-washing, onchain-washing, token-washing).

Project cards are populated with binary (0/1) flags; the final score is computed by the fixed formulas below. The reference implementation is [`../scorer/decai_fit.py`](../scorer/decai_fit.py).

## 1. Input flags

### A) AI reality — depth of verified AI integration

| Flag | Meaning |
|---|---|
| `AI_0` | Tier-1 **declaration of AI intent** (roadmap / official update), but no evidence of a working AI component at the protocol level |
| `AI_1` | It is described **what exactly the AI does** |
| `AI_2` | Working **demos / examples** exist |
| `AI_3` | **Metrics / benchmarks / quality** assessments exist (see operational definition below) |
| `AI_4` | **Technical description / architecture / model versions** exist |

### B) Onchain necessity — dependence on blockchain

| Flag | Meaning |
|---|---|
| `OC_1` | **Contracts / addresses / network** exist |
| `OC_2` | Onchain is **not just a token**: useful logic (access / accounting / rules / DAO) |
| `OC_3` | Onchain is **critical** — without blockchain the product breaks (see "replace-the-chain" test below) |

### C) Token necessity — token utility

| Flag | Meaning |
|---|---|
| `TK_0` | Token **does not exist** |
| `TK_1` | Token is **used to pay** for the service |
| `TK_2` | Token is needed for **incentives** (rewards / staking / slashing) |
| `TK_3` | Token is needed for **governance** (voting) |
| `TK_4` | Token is **replaceable** (USDC / subscription would work without loss of meaning) |

### D) Evidence coverage (by tier)

| Flag | Meaning |
|---|---|
| `E_AI_T1` | Tier-1 evidence exists for the **AI** block |
| `E_OC_T1` | Tier-1 evidence exists for the **onchain** block |
| `E_TK_T1` | Tier-1 evidence exists for the **token** block |
| `E_only_T3` | Sources are **exclusively Tier-3** (marketing / rumors) |

### E) Freshness

| Field | Meaning |
|---|---|
| `last_verified_days` | Days since the card was last verified |

## 2. Block scores (0–3 each)

```
a  =  min(3, AI_0 + AI_1 + AI_2 + AI_3 + AI_4)          # ai_score
o  =  min(3, OC_1 + OC_2 + OC_3)                        # onchain_score
t  =  2                        if TK_0 = 1              # token_score
      clamp[0..3](TK_1 + TK_2 + TK_3 − TK_4)  otherwise
e  =  min(3, E_AI_T1 + E_OC_T1 + E_TK_T1)               # evidence_score
```

Notes:

- A token-less project receives a fixed `t = 2`: absence of a token is a legitimate design choice, neither rewarded as maximal nor punished.
- `TK_4` (replaceability) *subtracts* — a token whose functions could be served by USDC or a subscription is evidence of token-washing.

## 3. Base index

```
S = a + o + t + e            # 0..12

S 0–2  -> base = 1
S 3–4  -> base = 2
S 5–6  -> base = 3
S 7–8  -> base = 4
S 9–10 -> base = 5
S 11–12 -> base = 6
```

## 4. Anti-manipulation caps

Caps are applied to the base index; **every rule can only lower the score**.

| Rule | Condition | Effect |
|---|---|---|
| **R1 — informational-noise cap** | `E_only_T3 = 1` | cap = 2 |
| **R2 — missing core evidence cap** | else if `E_AI_T1 = 0` **or** `E_OC_T1 = 0` | cap = 3 |
| **R3 — token verifiability cap** | else if token exists (`TK_0 = 0`) **and** `E_TK_T1 = 0` | cap = 4 |
| **R4 — AI-reality cap** | `a = 1` → cap ≤ 3; `a = 2` → cap ≤ 5; `a = 3` → cap ≤ 6 | applied on top of R1–R3 (`cap = min(cap, ai_cap)`) |

```
capped = min(base, cap)
```

### R0 — AI-reality zero-forcing (mandatory)

```
if a = 0:  DecAI Fit = 0
```

A project with no verified AI capability and no Tier-1 AI intent does not meet the threshold for Decentralized-AI classification as of the review date — regardless of its onchain, token, or evidence scores.

## 5. Staleness penalty

```
if last_verified_days > 550:
    final = 0               if a = 0
    final = max(1, capped − 1)   otherwise
else:
    final = 0               if a = 0
    final = capped          otherwise
```

## 6. Output

Displayed as:

> **DecAI Fit: `final`/6** — 0 = no verified AI reality and no AI intent; 1–2 low / 3–4 medium / 5–6 high alignment with the Decentralized AI thesis.

## Operational definitions

The rules below govern flag assignment so that different assessors produce identical flags and marketing cannot raise a score without verifiable artifacts.

**Universal rule.** Every flag set to `1` must carry a **justification**: source link(s) plus a short fact / quote / artifact confirming it. If there is no basis, sources conflict, or the situation is unclear — the flag is set to `0`, together with a note of what would need to be provided or checked for it to become `1`.

**`AI_0` — Tier-1 declaration of AI intent.** Set to 1 only if (a) a Tier-1 source (official blog / docs / repository / roadmap) explicitly states an AI direction, AI milestone, DeAI, or AI module *as a plan or intent*, and (b) there is **no** Tier-1 evidence of a working AI component at the protocol level (i.e. `AI_1..AI_4` remain 0). Mentions of AI only in Tier-2/3 sources do not qualify.

**`AI_3` — metrics / benchmarks / quality.** Set to 1 only if all of the following hold:

1. At least 1–2 **quantitative** quality indicators exist (not "industry-leading").
2. It is clear **what** was measured (task / model / subsystem) and what counts as success.
3. Basic **context** is given: version / date / release, data or scenarios used.
4. There is verifiability: a **Tier-1 artifact** (repository / report / logs / benchmark / public data) or sufficient **Tier-2 confirmation** (method + independent corroboration).
5. The metric concerns the project's **own product or model**, not a third-party API without an assessment of the project's own contribution.

Otherwise 0 — including: numbers without context; metrics from a demo while the product works differently; metrics of someone else's model.

**`OC_3` — the "replace-the-chain" test.** Imagine the blockchain replaced by an ordinary (even honest) server or database. Set `OC_3 = 1` only if that replacement breaks a key property of the product, e.g.:

- trustless settlement / rule execution without a trusted operator;
- public verifiability of state / history / reward distribution;
- censorship / tamper resistance (the operator cannot rewrite history or reallocate);
- trustless incentive accounting (contributions / rewards / slashing).

If the chain can be swapped out without loss of meaning ("it's just a service"), or "onchain" reduces to a token or payments — `OC_3 = 0`. The minimum justification for `OC_3 = 1` is a statement of the form "blockchain is required because of property X, otherwise attack/failure Y" plus a Tier-2-or-better source.

## Anti-manipulation rules (source handling)

1. **Priority:** Tier-1 > Tier-2 > Tier-3 (see [`evidence-tiers.md`](evidence-tiers.md)).
2. **Marketing proves nothing:** PR, claims, and "partnerships" without artifacts do not raise flags to 1.
3. **Conservatism:** with insufficient data or doubts, the flag is 0.
4. **Source conflicts:** incompatible claims (including within Tier-1) are marked `CONFLICT`, and dependent flags are set to 0 until re-verified.
5. **Proximity of evidence to the object:** for AI, metrics must concern a specific model/version; for onchain — specific addresses / network / contract logic.

### AI-washing red flags

Any of the following raises the Tier-1 bar and biases flags toward 0 until verifiable artifacts appear:

- "There is a repository", but it is empty / has no releases / is unrelated to the product.
- "There is an audit", but no public report / link / exact match to the relevant contracts.
- "There are AI metrics", but no method / version / context, or the metrics belong to a third-party model or API.
- "Onchain", but no contract addresses / network, or onchain reduces to issuing a token.
- "The token is needed for the ecosystem" without concrete functions (payment / staking / slashing / access) and without onchain mechanics.
- Strong claims ("decentralized AI", "verifiable inference") without verifiable artifacts.
