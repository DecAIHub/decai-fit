# Evidence Tiers — the Source Model behind DecAI Fit

The goal is not to "collect all links", but to separate quickly what counts as **proof**, what is **supporting context**, and what is **informational noise**. Every evidence entry attached to a project card carries a tier label; the scoring caps in [`scoring.md`](scoring.md) are driven by Tier-1 coverage.

## Tier-1: proof (highest weight)

Artifacts closest to the project's reality — the only sources that can, on their own, justify a flag:

- **Onchain facts:** contract addresses, transactions/events, protocol parameters observable on the network.
- **Official project documentation:** docs / whitepaper / technical documentation / terms of use (with date/version).
- **Source code and releases:** public repositories, release tags, changelogs, development activity.
- **Audits and security reports:** audit reports, public post-mortems, bug-bounty terms and payouts (where disclosed).

## Tier-2: context and corroboration (medium weight)

Useful for orientation and cross-checking, but must never be the *only* evidence:

- **Aggregators** (CoinMarketCap / CoinGecko and analogues): descriptions, links, categories, basic metadata.
- **Ecosystem and integration catalogues:** reference information and links (external context, not proof of "technology").
- **Onchain analytics / dashboards:** convenient visualizations and metrics (methodology and data source must be understood).
- **Public appearances by the team:** interviews / AMAs / presentations (statements that themselves require Tier-1 confirmation).

## Tier-3: informational noise (low weight)

Readable for the "pulse", used with extreme caution in scoring:

- **Influencer / channel posts** without primary sources.
- **PR publications and sponsored reviews.**
- **News reposts** without verifiable details.
- **Rumors / anonymous claims** without proof.

## How tiers act on the score

- A card whose sources are **exclusively Tier-3** is capped at **2/6** (rule R1) — no amount of marketing coverage can lift it further.
- Missing Tier-1 evidence for the **AI** or **onchain** block caps the score at **3/6** (rule R2).
- A project **with a token** but without Tier-1 token evidence is capped at **4/6** (rule R3).
- Tier priority in flag assignment is absolute: **Tier-1 > Tier-2 > Tier-3**, and marketing never raises a flag to 1.
