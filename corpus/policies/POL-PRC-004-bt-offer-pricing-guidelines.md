---
doc_id: POL-PRC-004
title: "Balance Transfer Offer Pricing Guidelines"
doc_type: pricing_guideline
lob: Card
region: US
owner: Card Pricing and Credit Risk
version: "2026.2"
effective_date: 2026-07-01
classification: CONFIDENTIAL
tags: [pricing, balance transfer, promo APR, BT fee, approved grid, economics]
---

# Balance Transfer Offer Pricing Guidelines (POL-PRC-004)

> Synthetic guideline for the Card Offer AI Assistant prototype.

## 1. Approved Offer Grid (Existing Customers)

| FICO Band | Promo APR | Promo Period | BT Fee | Min Fee | Approval |
|---|---|---|---|---|---|
| Super-Prime (740+) | 0% | 15–21 months | 2%–3% | $5 | Standard |
| Prime (670–739) | 0% | 12–18 months | 3%–4% | $5 | Standard |
| Near-Prime (620–669) | 0%–4.99% | 6–12 months | 4%–5% | $10 | Credit Risk exception required |
| Subprime (<620) | Not eligible for BT promotions | — | — | — | — |

Offers outside the grid need Credit Risk and Pricing approval.

## 2. Regulatory Floors

- Promotional rates must last **at least 6 months** (CARD Act / Reg Z §1026.55(b)(1)).
- Go-to APR after the promo must be disclosed and cannot be raised on the promo balance during the promo
  except as Reg Z allows (for example, 60+ days delinquent).
- Payments above the minimum go to the highest-APR balance first (Reg Z §1026.53).

## 3. Economics Assumptions for Projections

| Assumption | Planning Value | Source |
|---|---|---|
| Incremental response, prime revolver BT email | 3.5–4.0 pts | PM-25Q3-BT |
| Incremental response, broad revolver BT mail | ~1.8 pts | PM-24Q4-BT |
| Average BT amount, prime | $7,000–$7,500 | PM-24Q4-BT, PM-25Q3-BT |
| BT balance paydown during promo | ~2.5% per month | Finance |
| Attrition at promo expiry without retention | ~19% | PM-25Q4-RET |
| Attrition at promo expiry with retention offer | ~15% | PM-25Q4-RET |

Projections must show a range (low / expected / high), not a single number.
