---
doc_id: POL-FCRA-005
title: "FCRA Prescreened Offer Standard"
doc_type: policy
lob: Card
region: US
owner: Compliance - Consumer Reporting
version: "1.4"
effective_date: 2025-09-01
classification: INTERNAL
tags: [FCRA, prescreen, firm offer, opt-out notice, consumer report]
---

# FCRA Prescreened Offer Standard (POL-FCRA-005)

> Synthetic policy for the Card Offer AI Assistant prototype. Not legal advice.

## 1. When This Applies

Use this standard when a campaign list is built or filtered with **consumer report (credit bureau) data**
obtained for prescreening under FCRA §604(c). In-house data on existing accounts (balances, payment history
with us) does not by itself make an offer prescreened; refreshed bureau scores pulled for the campaign may.

## 2. Requirements

| Requirement | Detail |
|---|---|
| Firm offer of credit | The offer must be honored if the consumer still meets the pre-set criteria |
| Prescreen opt-out notice | Short-form and long-form notice (FCRA §615(d)) in every prescreened solicitation |
| Opt-out honoring | Exclude consumers on the prescreen opt-out list (`consent.privacy_flags.prescreen_opt_out`) |
| Criteria documentation | Keep the selection criteria and any post-screen criteria |

## 3. Assistant Guidance

If a proposed segment uses bureau-sourced attributes refreshed for the campaign, the assistant should flag
the campaign as **prescreened**, require the opt-out notice in the T&C, and apply the prescreen opt-out flag.
