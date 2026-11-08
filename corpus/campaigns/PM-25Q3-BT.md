---
doc_id: PM-25Q3-BT
title: "Post-Mortem: BT Promo Q3 (CMP-25Q3-BT)"
doc_type: campaign_post_mortem
lob: Card
region: US
campaign_id: CMP-25Q3-BT
offer_id: OFR-BT-0-15-3
segment_id: SEG-PRIME-REVOLVER-NOBT12
owner: Card Marketing Analytics
effective_date: 2025-11-20
classification: INTERNAL
tags: [balance transfer, email, prime revolvers, best practice]
---

# Post-Mortem: BT Promo Q3 (CMP-25Q3-BT)

> Synthetic document for the Card Offer AI Assistant prototype. Metrics come from the synthetic dataset.

## Summary

Our best-performing balance-transfer campaign to date. Tighter targeting (prime revolvers with no BT in the
last 12 months), a 15-month promo and an email channel nearly doubled the response rate of the broad
Balance Consolidation Offer at a fraction of the cost.

## Offer and Targeting

| Item | Value |
|---|---|
| Launch | 2025-08-04, response window to 2025-09-30 |
| Offer | 0% intro APR for 15 months on BTs made within 60 days; 3% BT fee (min $5); go-to APR per account |
| Segment | SEG-PRIME-REVOLVER-NOBT12 v2.1 — FICO 670+, revolver in each of last 3 statements, no BT in 12 months |
| Channel | Email (marketing email opt-in required) |
| Holdout | 10% control |
| T&C Template | TPL-BT-STD-v4 |

## Results (Synthetic Sample)

| Metric | Treatment | Control |
|---|---|---|
| Contacted | 11,992 | 1,298 |
| Response rate | 4.08% | 0.46% |
| Incremental response | 3.62 pts | — |
| Average BT amount | $7,360 | — |
| BT fee revenue | ~$108K | — |
| Complaint rate | 0.05% | — |

Response by FICO band: Prime (670–739) 4.58%; Super-Prime (740+) 2.91% with larger average BT ($9,190).

## What Worked

- **Certified segment** removed customers already on a promo, avoiding "promo stacking" and churn of existing BTs.
- **15-month promo** with a standard 3% fee was competitive without needing a fee waiver.
- **Email** was cheap and fast; consent was applied before list sizing, so no suppression issues.
- Disclosures followed TPL-BT-STD-v4: "intro" next to the rate, promo period and go-to APR in the same view.

## What Did Not Work

- Super-prime customers responded less; consider a separate, lower-fee or longer-promo cell for them.

## Recommendations

1. Treat this campaign as the **reference design** for prime-revolver BT offers.
2. Test a **super-prime cell** (for example a 2% fee or 18 months) with its own holdout.
3. Keep the 10% holdout so we can measure incremental response, not just gross response.
