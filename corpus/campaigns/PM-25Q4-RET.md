---
doc_id: PM-25Q4-RET
title: "Post-Mortem: Promo Expiry Retention (CMP-25Q4-RET)"
doc_type: campaign_post_mortem
lob: Card
region: US
campaign_id: CMP-25Q4-RET
offer_id: OFR-RET-999-12
segment_id: SEG-PROMO-EXPIRY-90D
owner: Card Retention Marketing
effective_date: 2026-03-10
classification: INTERNAL
tags: [retention, promo expiry, attrition, balance runoff]
---

# Post-Mortem: Promo Expiry Retention (CMP-25Q4-RET)

> Synthetic document for the Card Offer AI Assistant prototype. Metrics come from the synthetic dataset.

## Summary

Customers who took the 12-month Balance Consolidation Offer (CMP-24Q4-BT) were reaching promo expiry in
November 2025. We offered them a reduced 9.99% APR for 12 more months on the remaining transferred balance.
The offer cut attrition and should become a standard step after any BT campaign.

## Offer and Targeting

| Item | Value |
|---|---|
| Launch | 2025-10-06 (about 45 days before promo expiry) |
| Offer | 9.99% APR for 12 months on remaining BT balance; no fee |
| Segment | SEG-PROMO-EXPIRY-90D — CMP-24Q4-BT responders whose promo ends within 90 days |
| Channel | Direct mail |
| Holdout | 20% control |

## Results (Synthetic Sample)

| Metric | Treatment | Control |
|---|---|---|
| Customers | 450 | 126 |
| Offer acceptance | 31.8% | — |
| Account attrition after promo expiry | 15.3% | 19.0% |
| Attrition among accepters | 7.7% | — |

## Learnings

- Customers who carried a promo balance are rate-shoppers. Without a retention touch, about 1 in 5 left
  within 3 months of promo expiry.
- A retention offer lowered attrition by about 4 points overall and by more than half among accepters.
- **Promo expiry should be designed into the original BT offer economics**, not handled as an afterthought.

## Recommendations

1. For every BT campaign, schedule a retention touch 60–90 days before promo expiry.
2. Include expected post-promo attrition (~19% without a retention offer) in projected BT economics.
3. Test email as a lower-cost channel for retention where consent exists.
