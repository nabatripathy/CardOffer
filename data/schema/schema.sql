-- =====================================================================
-- Card Offer AI Assistant — Synthetic Data Schema (DuckDB)
-- All data is synthetic. No real customer information.
-- As-of date for the dataset: 2026-10-31. History window: 24 months.
-- =====================================================================

-- Foreign keys are documented in comments (DuckDB does not support cross-schema FKs).
-- ---------------------------------------------------------------------
-- Schema: core  (card customer and account data)
-- ---------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE IF NOT EXISTS core.customers (
    customer_id        VARCHAR PRIMARY KEY,      -- C0000001
    first_name         VARCHAR,                  -- PII
    last_name          VARCHAR,                  -- PII
    email              VARCHAR,                  -- PII
    phone              VARCHAR,                  -- PII
    street_address     VARCHAR,                  -- PII
    city               VARCHAR,
    state              VARCHAR(2),
    zip5               VARCHAR(5),               -- PII (quasi-identifier)
    date_of_birth      DATE,                     -- PII + PROHIBITED_BASIS (age)
    gender             VARCHAR,                  -- PROHIBITED_BASIS (ECOA/Reg B: sex)
    marital_status     VARCHAR,                  -- PROHIBITED_BASIS (ECOA/Reg B)
    annual_income      DECIMAL(12,2),            -- CONFIDENTIAL
    fico_score         INTEGER,                  -- CONFIDENTIAL (bureau)
    fico_band          VARCHAR,                  -- SUPER_PRIME / PRIME / NEAR_PRIME / SUBPRIME
    customer_since     DATE,
    tenure_months      INTEGER,
    is_employee        BOOLEAN
);

CREATE TABLE IF NOT EXISTS core.card_accounts (
    account_id         VARCHAR PRIMARY KEY,      -- A0000001
    customer_id        VARCHAR,  -- FK -> core.customers(customer_id)
    product_code       VARCHAR,                  -- CASHBACK_STD / REWARDS_PLUS / TRAVEL_ELITE / SECURED
    open_date          DATE,
    credit_limit       DECIMAL(12,2),
    purchase_apr       DECIMAL(5,2),             -- go-to purchase APR (%)
    account_status     VARCHAR,                  -- OPEN / CLOSED / CHARGED_OFF
    close_date         DATE
);

-- One row per account per month (end-of-month snapshot)
CREATE TABLE IF NOT EXISTS core.account_monthly (
    account_id         VARCHAR,  -- FK -> core.card_accounts(account_id)
    snapshot_month     DATE,                     -- first day of month
    statement_balance  DECIMAL(12,2),
    revolving_balance  DECIMAL(12,2),            -- balance carried after payment
    bt_balance         DECIMAL(12,2),            -- balance on promo BT
    purchase_volume    DECIMAL(12,2),
    payment_amount     DECIMAL(12,2),
    utilization_pct    DECIMAL(6,2),
    is_revolver        BOOLEAN,                  -- carried a balance this month
    days_past_due      INTEGER,
    PRIMARY KEY (account_id, snapshot_month)
);

CREATE TABLE IF NOT EXISTS core.balance_transfers (
    bt_id              VARCHAR PRIMARY KEY,
    account_id         VARCHAR,  -- FK -> core.card_accounts(account_id)
    campaign_id        VARCHAR,                  -- NULL if not campaign-driven
    bt_date            DATE,
    bt_amount          DECIMAL(12,2),
    promo_apr          DECIMAL(5,2),
    promo_months       INTEGER,
    bt_fee_pct         DECIMAL(5,2),
    bt_fee_amount      DECIMAL(12,2),
    promo_end_date     DATE
);

-- ---------------------------------------------------------------------
-- Schema: mktg  (offers, campaigns and responses)
-- ---------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS mktg;

CREATE TABLE IF NOT EXISTS mktg.offers (
    offer_id           VARCHAR PRIMARY KEY,
    offer_type         VARCHAR,                  -- BALANCE_TRANSFER / UPGRADE / RETENTION
    promo_apr          DECIMAL(5,2),
    promo_months       INTEGER,
    bt_fee_pct         DECIMAL(5,2),
    bt_fee_min         DECIMAL(8,2),
    bt_window_days     INTEGER,                  -- days from open/offer to qualify
    annual_fee         DECIMAL(8,2),
    headline_copy      VARCHAR,                  -- marketing headline used
    tc_template_id     VARCHAR                   -- links to corpus/templates
);

CREATE TABLE IF NOT EXISTS mktg.campaigns (
    campaign_id        VARCHAR PRIMARY KEY,      -- CMP-25Q3-BT
    campaign_name      VARCHAR,
    campaign_type      VARCHAR,
    offer_id           VARCHAR,  -- FK -> mktg.offers(offer_id)
    segment_id         VARCHAR,                  -- links to gov.segment_definitions
    launch_date        DATE,
    end_date           DATE,
    primary_channel    VARCHAR,                  -- EMAIL / DIRECT_MAIL / SMS / OUTBOUND_CALL
    is_prescreened     BOOLEAN,                  -- FCRA prescreen (firm offer) used
    budget_usd         DECIMAL(12,2),
    status             VARCHAR,                  -- COMPLETED / ACTIVE / PLANNED
    post_mortem_doc_id VARCHAR                   -- links to corpus/campaigns
);

CREATE TABLE IF NOT EXISTS mktg.campaign_contacts (
    campaign_id        VARCHAR,  -- FK -> mktg.campaigns(campaign_id)
    customer_id        VARCHAR,  -- FK -> core.customers(customer_id)
    cell               VARCHAR,                  -- TREATMENT / CONTROL (holdout)
    channel            VARCHAR,
    contact_date       DATE,
    responded          BOOLEAN,
    response_date      DATE,
    response_amount    DECIMAL(12,2),            -- BT amount or spend lift
    complaint_filed    BOOLEAN,
    PRIMARY KEY (campaign_id, customer_id)
);

-- ---------------------------------------------------------------------
-- Schema: consent  (consent hub — marketing and privacy preferences)
-- ---------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS consent;

CREATE TABLE IF NOT EXISTS consent.channel_preferences (
    customer_id        VARCHAR,  -- FK -> core.customers(customer_id)
    channel            VARCHAR,                  -- EMAIL / SMS / PHONE / DIRECT_MAIL
    marketing_opt_in   BOOLEAN,
    consent_source     VARCHAR,                  -- ONLINE / BRANCH / CALL_CENTER / DEFAULT
    effective_date     DATE,
    PRIMARY KEY (customer_id, channel)
);

CREATE TABLE IF NOT EXISTS consent.privacy_flags (
    customer_id             VARCHAR PRIMARY KEY,  -- FK -> core.customers(customer_id)
    do_not_call             BOOLEAN,             -- internal DNC + national DNC registry match (TCPA)
    do_not_solicit          BOOLEAN,             -- global marketing suppression
    glba_affiliate_opt_out  BOOLEAN,             -- GLBA / FCRA affiliate-marketing opt-out
    prescreen_opt_out       BOOLEAN,             -- FCRA prescreen opt-out (OptOutPrescreen)
    deceased_flag           BOOLEAN,
    bankruptcy_flag         BOOLEAN,
    military_lending_flag   BOOLEAN,             -- MLA / SCRA covered borrower
    updated_at              DATE
);

-- ---------------------------------------------------------------------
-- Schema: gov  (mock data catalog — stands in for Alation/Collibra)
-- ---------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS gov;

CREATE TABLE IF NOT EXISTS gov.data_products (
    data_product_id      VARCHAR PRIMARY KEY,    -- DP-REVOLVER-SEG
    name                 VARCHAR,
    description          VARCHAR,
    business_owner       VARCHAR,
    data_steward         VARCHAR,
    certification_status VARCHAR,                -- CERTIFIED / DRAFT / DEPRECATED
    certified_date       DATE,
    dq_score             DECIMAL(5,2),           -- 0–100
    refresh_frequency    VARCHAR,
    source_tables        VARCHAR,                -- comma-separated lineage
    approved_use_cases   VARCHAR,                -- comma-separated
    prohibited_use_cases VARCHAR
);

CREATE TABLE IF NOT EXISTS gov.column_classifications (
    table_name           VARCHAR,                -- schema.table
    column_name          VARCHAR,
    classification       VARCHAR,                -- PUBLIC / INTERNAL / CONFIDENTIAL / PII / PROHIBITED_BASIS
    glossary_term        VARCHAR,
    masking_policy       VARCHAR,                -- NONE / PARTIAL / FULL / HASH
    allowed_for_targeting BOOLEAN,
    PRIMARY KEY (table_name, column_name)
);

CREATE TABLE IF NOT EXISTS gov.segment_definitions (
    segment_id           VARCHAR PRIMARY KEY,    -- SEG-PRIME-REVOLVER-NOBT12
    segment_name         VARCHAR,
    business_definition  VARCHAR,
    sql_definition       VARCHAR,
    data_product_id      VARCHAR,  -- FK -> gov.data_products(data_product_id)
    owner                VARCHAR,
    certification_status VARCHAR,
    version              VARCHAR,
    last_reviewed        DATE
);

CREATE TABLE IF NOT EXISTS gov.glossary_terms (
    term                 VARCHAR PRIMARY KEY,
    definition           VARCHAR,
    steward              VARCHAR,
    status               VARCHAR                 -- APPROVED / DRAFT
);
