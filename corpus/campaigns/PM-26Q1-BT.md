---
doc_id: PM-26Q1-BT
title: "Post-Mortem: Fresh Start BT (CMP-26Q1-BT) — Compliance Findings"
doc_type: campaign_post_mortem
lob: Card
region: US
campaign_id: CMP-26Q1-BT
offer_id: OFR-BT-0-18-4
segment_id: SEG-PRIME-REVOLVER-NOBT12
owner: Card Marketing Analytics
effective_date: 2026-05-28
classification: CONFIDENTIAL
tags: [balance transfer, SMS, UDAAP, TCPA, complaints, consent, lessons learned]
---

# Post-Mortem: Fresh Start BT (CMP-26Q1-BT) — Compliance Findings

> Synthetic document for the Card Offer AI Assistant prototype. Metrics come from the synthetic dataset.

## Summary

An 18-month 0% BT offer sent by SMS to prime revolvers. Response was solid, but the campaign produced two
compliance findings: **misleading headline copy (UDAAP)** and **SMS sent without consent (TCPA)**. Remediation
included customer outreach and fee refunds. This campaign is the main reason consent and copy checks now run
**before** list sizing and creative approval.

## Offer and Targeting

| Item | Value |
|---|---|
| Launch | 2026-01-12, response window to 2026-03-13 |
| Offer | 0% intro APR for 18 months; **4% BT fee** (min $5) |
| Headline | "Transfer with no hassle - 0% for 18 months, no fees*" |
| Segment | SEG-PRIME-REVOLVER-NOBT12 v2.1 |
| Channel | SMS |
| Holdout | 10% control |

## Results (Synthetic Sample)

| Metric | Treatment | Control |
|---|---|---|
| Contacted | 5,800 | 621 |
| Response rate | 3.09% | 0.81% |
| Average BT amount | $8,084 | — |
| Complaint rate | 0.55% (32 complaints) | — |
| Complaint rate, other BT campaigns | 0.035%–0.05% | — |

## Finding 1 — UDAAP: Misleading "No Fees" Headline

- The headline said "no fees", with an asterisk pointing to a footnote that disclosed the 4% BT fee.
- A disclosure in a footnote does not cure a net impression that contradicts it. Compliance rated this a
  **deceptive practice risk under UDAAP**.
- Complaints ran at about **10× the normal rate**. Most were "I was charged a fee I was told I would not pay."
- **Remediation:** BT fees refunded to complainants; copy pulled on 2026-02-02.

## Finding 2 — TCPA: SMS Without Prior Express Written Consent

- The consent filter was applied by a separate team **after** the list was pulled and sized.
- A timing gap meant **616 SMS messages (10.6% of sends)** went to customers without SMS marketing consent.
- Marketing texts require prior express written consent under TCPA; statutory damages apply per message.

## Learnings

1. **Never use "no fee" or "free" language** when any fee applies to the offer.
2. **Consent filters must run before segment sizing**, inside the same governed query, not as a later step.
3. SMS needs an extra check: SMS opt-in plus DNC status.
4. Fee level matters: the 4% fee (vs 3% on CMP-25Q3-BT) did not hurt response but raised the stakes of the
   misleading copy.

## Required Controls Going Forward

| Control | Owner |
|---|---|
| Pre-launch copy review against POL-MKT-001 prohibited-claims list | Marketing Compliance |
| Consent and DNC suppression applied in the sizing query (POL-CNS-003) | Marketing Analytics |
| Headline must show the BT fee whenever a promo APR is in the headline | Creative + Compliance |
