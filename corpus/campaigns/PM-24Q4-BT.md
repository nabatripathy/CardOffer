---
doc_id: PM-24Q4-BT
title: "Post-Mortem: Balance Consolidation Offer (CMP-24Q4-BT)"
doc_type: campaign_post_mortem
lob: Card
region: US
campaign_id: CMP-24Q4-BT
offer_id: OFR-BT-0-12-3
segment_id: SEG-REVOLVER-BROAD
owner: Card Marketing Analytics
effective_date: 2025-04-15
classification: INTERNAL
tags: [balance transfer, direct mail, near-prime, promo expiry]
---

# Post-Mortem: Balance Consolidation Offer (CMP-24Q4-BT)

> Synthetic document for the Card Offer AI Assistant prototype. Metrics come from the synthetic dataset.

## Summary

A broad 0% balance-transfer offer mailed to all revolvers with FICO 620+. It produced high BT volume but the
weakest response rate of our recent BT campaigns, and the near-prime portion of the book carried noticeably
higher credit risk after the promo ended.

## Offer and Targeting

| Item | Value |
|---|---|
| Launch | 2024-11-12 (mail drop), response window to 2025-01-31 |
| Offer | 0% intro APR for 12 months on BTs made within 60 days; 3% BT fee (min $10) |
| Segment | SEG-REVOLVER-BROAD v1.3 — revolvers in each of the last 3 statements, FICO 620+ |
| Channel | Direct mail |
| Holdout | 10% control |

## Results (Synthetic Sample)

| Metric | Treatment | Control |
|---|---|---|
| Contacted | 28,302 | 3,080 |
| Response rate | 2.08% | 0.32% |
| Incremental response | 1.76 pts | — |
| Average BT amount | $7,245 | — |
| BT fee revenue | ~$128K | — |
| Complaint rate | 0.035% | — |

Response by FICO band: Prime 2.41%, Near-Prime 2.03%, Super-Prime 1.44%.

## What Worked

- Mail reached customers without email consent and produced the largest total BT balance of any campaign.
- Prime revolvers (670–739) were the most responsive band.

## What Did Not Work

- **Broad targeting diluted response.** Super-prime revolvers responded at only 1.44%; many revolve by choice
  and are less rate-sensitive.
- **Near-prime risk.** After promo expiry (Nov 2025), near-prime responders were 30+ days past due in 1.9% of
  account-months, versus 0.6% for prime and 0.1% for super-prime.
- **Promo-expiry attrition.** A large share of responders started paying down or leaving as the 12-month promo
  ended. This led to the retention test CMP-25Q4-RET.
- 12 months was too short to build durable balances; competitors were offering 15–21 months.

## Recommendations

1. Restrict future BT offers to **Prime revolvers (FICO 670+)** with no BT in the last 12 months
   (now certified as SEG-PRIME-REVOLVER-NOBT12).
2. Test **15+ month** promo periods.
3. Use email where consent exists; mail costs far more per response.
4. Plan a retention touch **60–90 days before promo expiry**.
