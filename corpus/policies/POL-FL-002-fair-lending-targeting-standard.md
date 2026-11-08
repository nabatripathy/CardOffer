---
doc_id: POL-FL-002
title: "Fair Lending Standard for Marketing and Targeting"
doc_type: policy
lob: Card
region: US
owner: Compliance - Fair Lending
version: "2.0"
effective_date: 2026-02-12
classification: INTERNAL
tags: [ECOA, Reg B, fair lending, prohibited basis, proxies, disparate impact]
---

# Fair Lending Standard for Marketing and Targeting (POL-FL-002)

> Synthetic policy for the Card Offer AI Assistant prototype. Not legal advice.

## 1. Purpose

The Equal Credit Opportunity Act (ECOA) and Regulation B prohibit discrimination in any aspect of a credit
transaction, and Reg B prohibits statements in advertising that would discourage applicants on a prohibited
basis. Marketing that steers better offers away from protected groups creates fair lending risk.

## 2. Prohibited Bases

Race, color, religion, national origin, sex, marital status, age (provided the person can contract), receipt
of public-assistance income, and the good-faith exercise of rights under the Consumer Credit Protection Act.

## 3. Attribute Rules

| Attribute | Status for Targeting | Notes |
|---|---|---|
| Date of birth / age | **Prohibited** | Includes age bands and derived "life stage" variables |
| Gender / sex | **Prohibited** | |
| Marital status | **Prohibited** | |
| Race, ethnicity, national origin, religion | **Prohibited** | Not stored in marketing data |
| ZIP code / geography | **Restricted** | Allowed for legal/state eligibility only; review for redlining proxy risk |
| Language preference | **Restricted** | Requires Fair Lending review |
| FICO score / band | Allowed | Credit-related and documented |
| Income | Allowed | Must be self-reported or verified per policy |
| Balances, utilization, revolving behavior, tenure | Allowed | |

The data catalog marks prohibited attributes as `PROHIBITED_BASIS` with `allowed_for_targeting = FALSE`.
Restricted demographic data (`DP-CUSTOMER-DEMOGRAPHICS`) is limited to fair lending testing.

## 4. Proxy and Outcome Testing

- New segments and models must be checked for proxies of prohibited bases (for example, variables highly
  correlated with age).
- Fair Lending tests offer outcomes for disparate impact before launch for new segment logic and quarterly
  for recurring campaigns.

## 5. Uncertified Segments

Draft or experimental segments (for example, `SEG-HIGH-PROPENSITY-BT-EXP`) may not be used for any production
campaign. AI assistants must refuse to return them as targeting options and explain why.
