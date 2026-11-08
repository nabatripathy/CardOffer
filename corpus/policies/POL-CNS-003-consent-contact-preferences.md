---
doc_id: POL-CNS-003
title: "Consent and Contact Preferences Standard"
doc_type: policy
lob: Enterprise
region: US
owner: Privacy Office
version: "3.1"
effective_date: 2026-04-01
classification: INTERNAL
tags: [TCPA, CAN-SPAM, GLBA, Reg V, affiliate marketing, DNC, consent, suppression, SMS]
---

# Consent and Contact Preferences Standard (POL-CNS-003)

> Synthetic policy for the Card Offer AI Assistant prototype. Not legal advice.

## 1. Golden Source

The Consent Hub (`DP-CONSENT-HUB`) is the only approved source of marketing consent and suppression. Local
copies or spreadsheets may not be used.

## 2. Channel Rules

| Channel | Requirement | Regulation |
|---|---|---|
| SMS / text | **Prior express written consent** for marketing texts; honor STOP immediately | TCPA |
| Outbound calls | Consent for autodialed/prerecorded marketing calls; scrub internal and National DNC lists | TCPA, TSR |
| Email | Honor opt-outs within 10 business days; clear sender identification and working unsubscribe | CAN-SPAM |
| Direct mail | Honor do-not-solicit; prescreened mail must honor prescreen opt-out | FCRA |
| All channels | Respect GLBA and affiliate-marketing opt-outs when data comes from an affiliate | GLBA, FCRA/Reg V |

## 3. Global Suppressions

Always remove: do-not-solicit, deceased, bankruptcy, and (for credit offers) customers covered by the
Military Lending Act where the offer's terms are not MLA-compliant.

## 4. When to Apply Consent

Consent and suppression must be applied **inside the governed sizing query**, before counts are reported,
and again at deployment (final scrub within 24 hours of send). Applying consent later as a separate step is
not allowed. Reference incident: CMP-26Q1-BT, where 616 SMS were sent without SMS consent.

## 5. Evidence

Log the list count before and after each suppression step, and the consent snapshot timestamp.
