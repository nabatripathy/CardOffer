# Governed AI Assistant for Credit Card Offer Design and Campaign Targeting

A working prototype of a governed AI assistant that helps card marketers design offers and target segments in
natural language. Every answer is grounded in sources, checked against policy and traceable.

> **All data and documents in this repo are synthetic.** No real customer, bank or campaign data is used.
> The policy documents are illustrations, not legal advice.

**Sample prompt:** *"Design a 0% balance-transfer offer for prime revolvers with no BT activity in the last
12 months. What has worked before, which data can I use, and what are the compliance constraints?"*

## Architecture

| Component | Prototype Choice | Folder |
|---|---|---|
| Warehouse | DuckDB | `data/` |
| Vector store / semantic retrieval (RAG) | Chroma (hybrid: vector + metadata filters) | `corpus/` → Phase 2 |
| MCP servers | MCP Python SDK: Catalog (mock Alation), Warehouse SQL, Consent Hub | `mcp_servers/` |
| Agent orchestration | LangGraph planner with data, history, pricing and compliance sub-tasks | `agent/` |
| Guardrails and audit | Prohibited-attribute block, PII masking, consent filter, prompt/response log | `guardrails/` |

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 1. Synthetic Data & Docs | DuckDB schema, generator, mock catalog, 11-document corpus | **Done** |
| 2. RAG & Vector Store | Chunk and embed corpus into Chroma; hybrid search with citations | Next |
| 3. MCP Servers | Catalog, Warehouse and Consent Hub tool endpoints | Planned |
| 4. Agent Orchestration | LangGraph planner and sub-agents; end-to-end answer for the sample prompt | Planned |
| 5. Guardrails & Audit | Policy rules in code; LangSmith or structured logs | Planned |
| 6. Demo & Write-Up | Walkthrough and architecture summary | Planned |

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python data/generator/generate.py            # 100K customers, ~25 s, writes data/card_offers.duckdb
pytest -q                                    # invariant checks on a 5K-customer build
```

## Data (Phase 1)

See [`data/schema/DATA_DICTIONARY.md`](data/schema/DATA_DICTIONARY.md) for every table, definition and the
planted governance test cases.

| Schema | Stands In For | Key Tables |
|---|---|---|
| `core` | Card system of record | customers, card_accounts, account_monthly (24 months), balance_transfers |
| `mktg` | Campaign history | offers, campaigns (5), campaign_contacts (treatment/control) |
| `consent` | Consent hub | channel_preferences, privacy_flags |
| `gov` | Data catalog (Alation/Collibra) | data_products, segment_definitions, column_classifications, glossary_terms |

Sizing the sample prompt's certified segment (`SEG-PRIME-REVOLVER-NOBT12`, as of Oct 2026) on the
100K-customer build:

| Step | Customers |
|---|---|
| Certified segment | 17,376 |
| After global suppressions (do-not-solicit, deceased, bankruptcy) | 16,705 |
| Email-eligible (marketing opt-in) | 13,761 |

## Document Corpus (Phase 1)

| Doc ID | Type | What the Assistant Learns From It |
|---|---|---|
| PM-24Q4-BT | Post-mortem | Broad targeting diluted response; near-prime risk; 12-month promo too short |
| PM-25Q3-BT | Post-mortem | Reference design: prime revolvers, 15 months, 3% fee, email, 4.08% response |
| PM-25Q4-RET | Post-mortem | Promo-expiry attrition ~19%; retention offer cuts it |
| PM-26Q1-BT | Post-mortem | UDAAP "no fees" headline and TCPA SMS consent failures |
| PM-26Q2-UPG | Post-mortem | Travel upgrade for affluent spenders |
| POL-MKT-001 | Policy | Approvals, holdouts, prohibited claims, AI-assisted design rules |
| POL-FL-002 | Policy | ECOA/Reg B prohibited bases and proxy rules |
| POL-CNS-003 | Policy | TCPA, CAN-SPAM, GLBA, Reg V; consent applied in the sizing query |
| POL-PRC-004 | Pricing | Approved BT offer grid and economics assumptions |
| POL-FCRA-005 | Policy | Prescreened offer rules |
| TPL-BT-STD-v4 | T&C template | Reg Z/CARD Act disclosure pattern and checklist |

Every document has YAML front-matter (`doc_type`, `lob`, `region`, `campaign_id`, `classification`, `tags`)
used as metadata filters in Phase 2.

## Related Work

Extends a LangGraph/LangChain agentic data governance project that uses mocked Alation metadata.
