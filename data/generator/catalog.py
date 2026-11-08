"""
Mock data catalog content (stand-in for Alation/Collibra).

Populates gov.data_products, gov.segment_definitions, gov.glossary_terms and
gov.column_classifications. Includes deliberate "bad" entries (a DRAFT data
product and a segment that uses a prohibited-basis attribute) so the
guardrails have something to catch.
"""
from __future__ import annotations

from datetime import date

DATA_PRODUCTS = [
    ("DP-CARD-CUSTOMER", "Card Customer Profile",
     "One row per card customer with contact data, credit band and tenure. PII masked by default.",
     "Card Marketing Analytics", "J. Alvarez", "CERTIFIED", date(2026, 3, 2), 96.5, "Daily",
     "core.customers", "Campaign targeting,Segment sizing,Offer analytics",
     "Credit decisioning,Use of prohibited-basis attributes"),
    ("DP-ACCOUNT-MONTHLY", "Card Account Monthly Snapshot",
     "End-of-month balances, revolving status, utilization and delinquency per card account.",
     "Card Finance", "P. Okafor", "CERTIFIED", date(2026, 1, 15), 98.2, "Monthly",
     "core.card_accounts,core.account_monthly", "Campaign targeting,Segment sizing,Economics forecasting",
     "None"),
    ("DP-REVOLVER-SEG", "Revolver Segment",
     "Certified revolver segmentation: customers who carried a balance in each of the last 3 statements, "
     "with BT history and FICO band.",
     "Card Marketing Analytics", "J. Alvarez", "CERTIFIED", date(2026, 6, 10), 97.1, "Monthly",
     "core.customers,core.account_monthly,core.balance_transfers",
     "Balance transfer targeting,Retention targeting", "Credit line management"),
    ("DP-CAMPAIGN-HISTORY", "Campaign History and Response",
     "All past card campaigns, offers, contacts, holdout cells, responses and complaints.",
     "Card Marketing Operations", "S. Chen", "CERTIFIED", date(2026, 5, 20), 94.0, "Weekly",
     "mktg.campaigns,mktg.offers,mktg.campaign_contacts",
     "Offer design,Response modeling,Post-campaign analysis", "None"),
    ("DP-CONSENT-HUB", "Consent and Contact Preferences",
     "Golden source of marketing opt-ins by channel and privacy suppressions (DNC, GLBA, prescreen opt-out).",
     "Privacy Office", "M. Robinson", "CERTIFIED", date(2026, 8, 1), 99.3, "Near real-time",
     "consent.channel_preferences,consent.privacy_flags", "Suppression for all marketing", "None"),
    ("DP-BT-PROPENSITY-EXP", "Experimental BT Propensity Features",
     "Analyst sandbox features for BT propensity. Includes age-derived variables. NOT reviewed by Fair Lending.",
     "Card Marketing Analytics (sandbox)", "unassigned", "DRAFT", None, 71.4, "Ad hoc",
     "core.customers,core.account_monthly", "Exploratory analysis only", "Production targeting"),
    ("DP-CUSTOMER-DEMOGRAPHICS", "Customer Demographics (Restricted)",
     "Date of birth, gender and marital status. Restricted to Fair Lending testing and regulatory reporting.",
     "Compliance - Fair Lending", "R. Patel", "CERTIFIED", date(2026, 2, 12), 95.0, "Daily",
     "core.customers", "Fair lending testing,Regulatory reporting",
     "Marketing targeting,Offer pricing,Segment definition"),
]

SEGMENTS = [
    ("SEG-PRIME-REVOLVER-NOBT12", "Prime Revolvers, No BT in 12 Months",
     "Open card accounts, FICO 670+, revolving balance in each of the last 3 statements, no balance "
     "transfer in the last 12 months, not on an active promo, not 30+ days past due.",
     """SELECT c.customer_id, a.account_id
FROM core.customers c
JOIN core.card_accounts a USING (customer_id)
WHERE a.account_status = 'OPEN'
  AND c.fico_score >= 670
  AND a.account_id IN (
      SELECT account_id FROM core.account_monthly
      WHERE snapshot_month >= DATE '{as_of_month}' - INTERVAL 2 MONTH
        AND snapshot_month <= DATE '{as_of_month}'
      GROUP BY account_id HAVING bool_and(is_revolver) AND count(*) = 3)
  AND a.account_id NOT IN (
      SELECT account_id FROM core.balance_transfers
      WHERE bt_date > DATE '{as_of_month}' - INTERVAL 12 MONTH
         OR promo_end_date > DATE '{as_of_month}')
  AND a.account_id NOT IN (
      SELECT account_id FROM core.account_monthly
      WHERE snapshot_month = DATE '{as_of_month}' AND days_past_due >= 30)""",
     "DP-REVOLVER-SEG", "J. Alvarez", "CERTIFIED", "2.1", date(2026, 6, 10)),
    ("SEG-REVOLVER-BROAD", "All Revolvers, FICO 620+",
     "Open accounts, FICO 620+, revolving in each of the last 3 statements, not on an active promo.",
     """SELECT c.customer_id, a.account_id
FROM core.customers c
JOIN core.card_accounts a USING (customer_id)
WHERE a.account_status = 'OPEN' AND c.fico_score >= 620
  AND a.account_id IN (
      SELECT account_id FROM core.account_monthly
      WHERE snapshot_month >= DATE '{as_of_month}' - INTERVAL 2 MONTH
        AND snapshot_month <= DATE '{as_of_month}'
      GROUP BY account_id HAVING bool_and(is_revolver) AND count(*) = 3)
  AND a.account_id NOT IN (
      SELECT account_id FROM core.balance_transfers WHERE promo_end_date > DATE '{as_of_month}')""",
     "DP-REVOLVER-SEG", "J. Alvarez", "CERTIFIED", "1.3", date(2025, 10, 1)),
    ("SEG-PROMO-EXPIRY-90D", "Promo Expiring in 90 Days",
     "Accounts with a promotional BT balance whose promo ends within the next 90 days.",
     """SELECT DISTINCT a.customer_id, b.account_id
FROM core.balance_transfers b JOIN core.card_accounts a USING (account_id)
WHERE a.account_status = 'OPEN'
  AND b.promo_end_date BETWEEN DATE '{as_of_month}' AND DATE '{as_of_month}' + INTERVAL 90 DAY""",
     "DP-REVOLVER-SEG", "J. Alvarez", "CERTIFIED", "1.0", date(2025, 9, 15)),
    ("SEG-AFFLUENT-SPENDER", "Affluent Spenders",
     "Income 150K+, FICO 700+, average monthly purchase volume 2,500+ over 6 months, not already on Travel Elite.",
     """SELECT c.customer_id, a.account_id
FROM core.customers c JOIN core.card_accounts a USING (customer_id)
WHERE a.account_status = 'OPEN' AND c.annual_income >= 150000 AND c.fico_score >= 700
  AND a.product_code <> 'TRAVEL_ELITE'
  AND a.account_id IN (
      SELECT account_id FROM core.account_monthly
      WHERE snapshot_month > DATE '{as_of_month}' - INTERVAL 6 MONTH
      GROUP BY account_id HAVING avg(purchase_volume) >= 2500)""",
     "DP-ACCOUNT-MONTHLY", "S. Chen", "CERTIFIED", "1.2", date(2026, 3, 30)),
    ("SEG-HIGH-PROPENSITY-BT-EXP", "High BT Propensity (Experimental)",
     "Analyst-built segment: revolvers aged 25-45 with high utilization. NOT approved - uses age.",
     """SELECT c.customer_id, a.account_id
FROM core.customers c JOIN core.card_accounts a USING (customer_id)
WHERE date_diff('year', c.date_of_birth, DATE '{as_of_month}') BETWEEN 25 AND 45
  AND a.account_status = 'OPEN'""",
     "DP-BT-PROPENSITY-EXP", "unassigned", "DRAFT", "0.3", date(2026, 9, 2)),
]

GLOSSARY = [
    ("Revolver", "A card customer who carries a balance past the statement due date; certified definition "
     "requires a revolving balance in each of the last 3 statements.", "J. Alvarez", "APPROVED"),
    ("Transactor", "A card customer who pays the full statement balance each month.", "J. Alvarez", "APPROVED"),
    ("Prime", "FICO score of 670 or higher (Prime 670-739, Super Prime 740+).", "P. Okafor", "APPROVED"),
    ("Balance Transfer (BT)", "Moving a balance from another lender to the bank's card, usually at a promo APR "
     "with a BT fee.", "S. Chen", "APPROVED"),
    ("Promo APR", "Introductory APR applied to a balance for a limited promo period.", "S. Chen", "APPROVED"),
    ("Go-To APR", "The standard APR that applies after a promo period ends.", "S. Chen", "APPROVED"),
    ("Response Rate", "Responders divided by contacted customers in the treatment cell, within the response "
     "window.", "S. Chen", "APPROVED"),
    ("Incremental Response", "Treatment response rate minus control (holdout) response rate.", "S. Chen", "APPROVED"),
    ("Balance Lift", "Average incremental balance per contacted customer versus the control cell.", "S. Chen",
     "APPROVED"),
    ("Prescreened Offer", "A firm offer of credit made using consumer report data under FCRA section 604(c); "
     "requires the prescreen opt-out notice.", "R. Patel", "APPROVED"),
    ("Prohibited Basis", "Characteristics that cannot be used in credit decisions or targeting under ECOA/Reg B "
     "(e.g., race, color, religion, national origin, sex, marital status, age).", "R. Patel", "APPROVED"),
]

# column -> (classification, glossary term, masking, allowed_for_targeting)
CLASSIFICATIONS = {
    ("core.customers", "first_name"): ("PII", None, "FULL", False),
    ("core.customers", "last_name"): ("PII", None, "FULL", False),
    ("core.customers", "email"): ("PII", None, "HASH", False),
    ("core.customers", "phone"): ("PII", None, "HASH", False),
    ("core.customers", "street_address"): ("PII", None, "FULL", False),
    ("core.customers", "zip5"): ("PII", None, "PARTIAL", False),
    ("core.customers", "date_of_birth"): ("PROHIBITED_BASIS", "Prohibited Basis", "FULL", False),
    ("core.customers", "gender"): ("PROHIBITED_BASIS", "Prohibited Basis", "FULL", False),
    ("core.customers", "marital_status"): ("PROHIBITED_BASIS", "Prohibited Basis", "FULL", False),
    ("core.customers", "annual_income"): ("CONFIDENTIAL", None, "NONE", True),
    ("core.customers", "fico_score"): ("CONFIDENTIAL", "Prime", "NONE", True),
    ("core.customers", "fico_band"): ("CONFIDENTIAL", "Prime", "NONE", True),
    ("core.customers", "is_employee"): ("CONFIDENTIAL", None, "NONE", True),
    ("core.account_monthly", "is_revolver"): ("INTERNAL", "Revolver", "NONE", True),
    ("core.balance_transfers", "bt_amount"): ("CONFIDENTIAL", "Balance Transfer (BT)", "NONE", True),
    ("mktg.offers", "promo_apr"): ("INTERNAL", "Promo APR", "NONE", True),
    ("mktg.campaign_contacts", "complaint_filed"): ("CONFIDENTIAL", None, "NONE", False),
}


def build_catalog(con) -> None:
    con.executemany("INSERT INTO gov.data_products VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", DATA_PRODUCTS)
    # sql_definition keeps a {as_of_month} placeholder; the warehouse MCP server fills it at run time
    con.executemany("INSERT INTO gov.segment_definitions VALUES (?,?,?,?,?,?,?,?,?)", SEGMENTS)
    con.executemany("INSERT INTO gov.glossary_terms VALUES (?,?,?,?)", GLOSSARY)

    cols = con.execute("""
        SELECT table_schema || '.' || table_name, column_name
        FROM information_schema.columns
        WHERE table_schema IN ('core','mktg','consent')
        ORDER BY 1, ordinal_position""").fetchall()
    rows = []
    for t, c in cols:
        if (t, c) in CLASSIFICATIONS:
            cls, term, mask, allowed = CLASSIFICATIONS[(t, c)]
        elif t.startswith("consent."):
            cls, term, mask, allowed = "CONFIDENTIAL", None, "NONE", False   # suppression only
        else:
            cls, term, mask, allowed = "INTERNAL", None, "NONE", True
        rows.append((t, c, cls, term, mask, allowed))
    con.executemany("INSERT INTO gov.column_classifications VALUES (?,?,?,?,?,?)", rows)
