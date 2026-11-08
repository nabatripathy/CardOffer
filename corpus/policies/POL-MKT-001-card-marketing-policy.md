---
doc_id: POL-MKT-001
title: "Card Marketing Policy"
doc_type: policy
lob: Card
region: US
owner: Card Marketing Compliance
version: "4.2"
effective_date: 2026-06-01
classification: INTERNAL
tags: [marketing policy, approvals, holdout, prohibited claims, UDAAP]
---

# Card Marketing Policy (POL-MKT-001)

> Synthetic policy for the Card Offer AI Assistant prototype. Not legal advice.

## 1. Scope

Applies to all acquisition, balance-transfer, upgrade and retention marketing for consumer credit cards,
in every channel (email, SMS, direct mail, outbound calls, digital and in-app).

## 2. Required Approvals Before Launch

| Approver | Reviews |
|---|---|
| Marketing (campaign owner) | Business case, segment, offer, projected economics |
| Credit Risk | Offer terms, eligible FICO range, expected losses |
| Marketing Compliance | Copy, disclosures, channel consent, UDAAP review |
| Fair Lending (Compliance) | Targeting attributes and segment logic |
| Model Risk (if a model or AI tool shaped targeting) | Model documentation per SR 11-7 |

No campaign may launch without all applicable approvals recorded in the approval workflow.

## 3. Targeting Rules

1. Use only **certified** segments and data products from the enterprise data catalog.
2. Never use prohibited-basis attributes or close proxies (see POL-FL-002).
3. Apply consent and suppression **in the same query that sizes the segment** (see POL-CNS-003).
4. Every campaign must hold out a randomized **control cell of at least 10%** (20% for retention tests).
5. Exclude customers on an active promotional balance from new BT offers ("no promo stacking").
6. Exclude accounts that are delinquent (30+ DPD), charged off, in bankruptcy, or flagged deceased.

## 4. Prohibited and Restricted Claims

| Claim | Rule |
|---|---|
| "No fee", "free", "no cost" | Prohibited if any fee applies to the advertised feature (see PM-26Q1-BT) |
| Promo rate in a headline | Must say "intro" or "introductory" next to the rate, show the promo period and the go-to APR in the same view |
| "Pre-approved" / "guaranteed" | Only for FCRA-compliant firm offers |
| Savings claims | Must be based on a stated, realistic example and approved by Compliance |
| Urgency ("act now", "last chance") | Allowed only if the deadline is real |

Footnotes and asterisks may clarify a claim but may not contradict the headline's net impression.

## 5. AI-Assisted Campaign Design

- AI tools may recommend offers and segments, but **humans approve**. AI output is advisory.
- Every AI recommendation must cite its sources (documents, tables, rules) and be logged with the prompt.
- AI tools must use only certified data and must not have access to prohibited-basis attributes for targeting.

## 6. Record Keeping

Keep segment SQL, list counts before and after suppression, final creative, disclosures and approvals for at
least 25 months after the campaign ends.
