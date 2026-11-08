"""
Synthetic data generator for the Card Offer AI Assistant prototype.

Builds a DuckDB database with fake card customers, 24 months of account
history, five past marketing campaigns, consent preferences and a mock
data catalog (stand-in for Alation/Collibra).

All data is synthetic. Deterministic for a given --seed.

Usage:
    python data/generator/generate.py --customers 20000 --out data/card_offers.duckdb
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from faker import Faker

from catalog import build_catalog

AS_OF = date(2026, 10, 31)
N_MONTHS = 24
MONTHS = pd.date_range("2024-11-01", periods=N_MONTHS, freq="MS")
SCHEMA_SQL = Path(__file__).resolve().parents[1] / "schema" / "schema.sql"


def month_index(d: date) -> int:
    return (d.year - MONTHS[0].year) * 12 + (d.month - MONTHS[0].month)


# ---------------------------------------------------------------------------
# Campaign catalogue — kept consistent with the post-mortems in corpus/
# ---------------------------------------------------------------------------
OFFERS = [
    # offer_id, type, promo_apr, months, fee_pct, fee_min, window, annual_fee, headline, template
    ("OFR-BT-0-12-3", "BALANCE_TRANSFER", 0.0, 12, 3.0, 10.0, 60, 0.0,
     "Consolidate your balances: 0% intro APR for 12 months on balance transfers", "TPL-BT-STD-v3"),
    ("OFR-BT-0-15-3", "BALANCE_TRANSFER", 0.0, 15, 3.0, 5.0, 60, 0.0,
     "0% intro APR for 15 months on balance transfers made in the first 60 days", "TPL-BT-STD-v4"),
    ("OFR-RET-999-12", "RETENTION", 9.99, 12, 0.0, 0.0, 30, 0.0,
     "Your promo is ending - keep a 9.99% APR on your transferred balance for 12 more months", "TPL-RET-v1"),
    ("OFR-BT-0-18-4", "BALANCE_TRANSFER", 0.0, 18, 4.0, 5.0, 60, 0.0,
     "Transfer with no hassle - 0% for 18 months, no fees*", "TPL-BT-STD-v4"),
    ("OFR-UPG-TRAVEL", "UPGRADE", None, None, None, None, 90, 95.0,
     "Upgrade to Travel Elite - first-year annual fee waived, 3x points on travel", "TPL-UPG-v2"),
    ("OFR-BT-STD", "BALANCE_TRANSFER", 0.0, 6, 5.0, 5.0, None, 0.0,
     "Standard balance transfer offer (always-on, in-app)", "TPL-BT-STD-v4"),
]

CAMPAIGNS = [
    # id, name, type, offer, segment, launch, end, channel, prescreen, budget, doc,
    # target treat response rate, control response rate
    ("CMP-24Q4-BT", "Balance Consolidation Offer", "BALANCE_TRANSFER", "OFR-BT-0-12-3",
     "SEG-REVOLVER-BROAD", date(2024, 11, 12), date(2025, 1, 31), "DIRECT_MAIL", False, 410000,
     "PM-24Q4-BT", 0.022, 0.003),
    ("CMP-25Q3-BT", "BT Promo Q3", "BALANCE_TRANSFER", "OFR-BT-0-15-3",
     "SEG-PRIME-REVOLVER-NOBT12", date(2025, 8, 4), date(2025, 9, 30), "EMAIL", False, 95000,
     "PM-25Q3-BT", 0.040, 0.004),
    ("CMP-25Q4-RET", "Promo Expiry Retention", "RETENTION", "OFR-RET-999-12",
     "SEG-PROMO-EXPIRY-90D", date(2025, 10, 6), date(2025, 12, 15), "DIRECT_MAIL", False, 38000,
     "PM-25Q4-RET", 0.36, 0.0),
    ("CMP-26Q1-BT", "Fresh Start BT", "BALANCE_TRANSFER", "OFR-BT-0-18-4",
     "SEG-PRIME-REVOLVER-NOBT12", date(2026, 1, 12), date(2026, 3, 13), "SMS", False, 120000,
     "PM-26Q1-BT", 0.033, 0.004),
    ("CMP-26Q2-UPG", "Travel Rewards Upgrade", "UPGRADE", "OFR-UPG-TRAVEL",
     "SEG-AFFLUENT-SPENDER", date(2026, 4, 6), date(2026, 6, 30), "EMAIL", False, 150000,
     "PM-26Q2-UPG", 0.055, 0.005),
]

APR_BY_BAND = {"SUPER_PRIME": 19.99, "PRIME": 22.99, "NEAR_PRIME": 26.99, "SUBPRIME": 29.99}
REVOLVE_P_BY_BAND = {"SUPER_PRIME": 0.25, "PRIME": 0.45, "NEAR_PRIME": 0.65, "SUBPRIME": 0.75}


def fico_band(score: np.ndarray) -> np.ndarray:
    return np.select(
        [score >= 740, score >= 670, score >= 620],
        ["SUPER_PRIME", "PRIME", "NEAR_PRIME"],
        default="SUBPRIME",
    )


# ---------------------------------------------------------------------------
# Customers and accounts
# ---------------------------------------------------------------------------
def build_customers(n: int, rng: np.random.Generator, fake: Faker) -> pd.DataFrame:
    fico = np.clip(rng.normal(712, 62, n), 520, 850).round().astype(int)
    band = fico_band(fico)
    income = np.round(np.exp(rng.normal(np.log(78000), 0.55, n)) + (fico - 700) * 120, -2)
    income = np.clip(income, 18000, 950000)
    tenure = rng.integers(1, 240, n)
    since = [AS_OF - timedelta(days=int(t * 30.4)) for t in tenure]
    age_years = rng.integers(21, 85, n)
    dob = [AS_OF - timedelta(days=int(a * 365.25 + rng.integers(0, 365))) for a in age_years]
    gender = rng.choice(["F", "M", "X", "U"], n, p=[0.49, 0.48, 0.01, 0.02])
    marital = rng.choice(["MARRIED", "SINGLE", "DIVORCED", "WIDOWED", "UNKNOWN"], n,
                         p=[0.48, 0.33, 0.10, 0.04, 0.05])
    states = rng.choice(["TX", "CA", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "AZ", "WA", "CO"],
                        n, p=[.14, .16, .10, .10, .07, .07, .06, .06, .06, .06, .06, .06])

    rows = []
    for i in range(n):
        st = states[i]
        rows.append({
            "customer_id": f"C{i + 1:07d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": f"user{i + 1:07d}@example.com",
            "phone": f"555-{rng.integers(100, 999)}-{rng.integers(1000, 9999)}",
            "street_address": fake.street_address(),
            "city": fake.city(),
            "state": st,
            "zip5": f"{rng.integers(10000, 99999)}",
            "date_of_birth": dob[i],
            "gender": gender[i],
            "marital_status": marital[i],
            "annual_income": float(income[i]),
            "fico_score": int(fico[i]),
            "fico_band": band[i],
            "customer_since": since[i],
            "tenure_months": int(tenure[i]),
            "is_employee": bool(rng.random() < 0.01),
        })
    return pd.DataFrame(rows)


def build_accounts(cust: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(cust)
    band = cust["fico_band"].to_numpy()
    income = cust["annual_income"].to_numpy()
    product = np.where(
        (band == "SUBPRIME") & (rng.random(n) < 0.4), "SECURED",
        np.where((income > 140000) & (rng.random(n) < 0.35), "TRAVEL_ELITE",
                 np.where(rng.random(n) < 0.45, "REWARDS_PLUS", "CASHBACK_STD")))
    fico_factor = np.interp(cust["fico_score"], [520, 620, 700, 780, 850], [0.3, 0.6, 1.0, 1.4, 1.7])
    limit = np.clip(income * rng.uniform(0.08, 0.22, n) * fico_factor, 500, 50000)
    limit = np.where(product == "SECURED", np.clip(limit, 300, 2500), limit)
    limit = np.round(limit, -2)
    return pd.DataFrame({
        "account_id": [f"A{i + 1:07d}" for i in range(n)],
        "customer_id": cust["customer_id"],
        "product_code": product,
        "open_date": cust["customer_since"],
        "credit_limit": limit,
        "purchase_apr": [APR_BY_BAND[b] for b in band],
        "account_status": "OPEN",
        "close_date": None,
    })


# ---------------------------------------------------------------------------
# Monthly history (matrices N x M)
# ---------------------------------------------------------------------------
class History:
    def __init__(self, cust: pd.DataFrame, acct: pd.DataFrame, rng: np.random.Generator):
        n, m = len(cust), N_MONTHS
        self.rng = rng
        self.n, self.m = n, m
        band = cust["fico_band"].to_numpy()
        self.limit = acct["credit_limit"].to_numpy(dtype=float)
        income = cust["annual_income"].to_numpy(dtype=float)

        habitual = rng.random(n) < np.vectorize(REVOLVE_P_BY_BAND.get)(band)
        p_rev_month = np.where(habitual, 0.88, 0.07)
        self.revolve = rng.random((n, m)) < p_rev_month[:, None]

        u0 = np.where(habitual, rng.beta(2.5, 3.0, n), rng.beta(1.2, 8.0, n))
        drift = np.cumsum(rng.normal(0, 0.025, (n, m)), axis=1)
        util = np.clip(u0[:, None] + drift, 0.0, 1.0)

        spend = (income / 12)[:, None] * rng.uniform(0.04, 0.28, n)[:, None] \
            * rng.lognormal(0, 0.25, (n, m))
        spend = np.minimum(spend, self.limit[:, None] * 0.9)
        self.purchase = np.round(spend, 2)

        stmt_rev = self.limit[:, None] * util
        self.base_balance = np.where(self.revolve, np.maximum(stmt_rev, spend), spend)
        self.bt = np.zeros((n, m))
        self.promo_end_idx = np.full(n, -1)          # month index when active promo ends
        self.last_bt_idx = np.full(n, -999)
        self.closed_idx = np.full(n, m)              # first month with no row
        open_dates = pd.to_datetime(acct["open_date"]).dt.date
        self.open_idx = np.array([max(month_index(d), 0) for d in open_dates])

        dpd_p = np.vectorize({"SUPER_PRIME": .002, "PRIME": .006, "NEAR_PRIME": .02, "SUBPRIME": .06}.get)(band)
        self.dpd = np.where(rng.random((n, m)) < dpd_p[:, None],
                            rng.choice([30, 60, 90], (n, m), p=[.75, .18, .07]), 0)

    def is_revolver(self, mi: int) -> np.ndarray:
        return self.revolve[:, mi] | (self.bt[:, mi] > 0)

    def active(self, mi: int) -> np.ndarray:
        return (self.open_idx <= mi) & (self.closed_idx > mi)

    def revolving_balance(self, mi: int) -> np.ndarray:
        bal = self.base_balance[:, mi] + self.bt[:, mi]
        pay = np.where(self.revolve[:, mi], np.maximum(25, bal * 0.04), self.base_balance[:, mi])
        return np.maximum(bal - pay, 0) + 0.0

    def add_bt(self, idx: np.ndarray, start_mi: int, amount: np.ndarray, promo_months: int):
        """Promo BT balance pays down ~2.5%/month; after promo end it rolls into revolving."""
        for k in range(start_mi, self.m):
            t = k - start_mi
            remaining = amount * (0.975 ** t)
            self.bt[idx, k] += np.where(t < promo_months, remaining, 0)
            # post-promo: balance stays on the card as ordinary revolving debt
            self.base_balance[idx, k] += np.where(t >= promo_months, remaining, 0)
            self.revolve[idx, k] |= t >= promo_months
        self.promo_end_idx[idx] = start_mi + promo_months
        self.last_bt_idx[idx] = start_mi

    def close(self, idx: np.ndarray, mi: int):
        self.closed_idx[idx] = np.minimum(self.closed_idx[idx], mi)


# ---------------------------------------------------------------------------
# Consent
# ---------------------------------------------------------------------------
def build_consent(cust: pd.DataFrame, rng: np.random.Generator):
    n = len(cust)
    ids = cust["customer_id"].to_numpy()
    p_in = {"EMAIL": 0.82, "SMS": 0.34, "PHONE": 0.45, "DIRECT_MAIL": 0.95}
    pref_rows = []
    for ch, p in p_in.items():
        opt = rng.random(n) < p
        src = rng.choice(["ONLINE", "BRANCH", "CALL_CENTER", "DEFAULT"], n, p=[.55, .15, .15, .15])
        eff = [AS_OF - timedelta(days=int(d)) for d in rng.integers(30, 2500, n)]
        pref_rows.append(pd.DataFrame({"customer_id": ids, "channel": ch, "marketing_opt_in": opt,
                                       "consent_source": src, "effective_date": eff}))
    prefs = pd.concat(pref_rows, ignore_index=True)

    sub = (cust["fico_band"] == "SUBPRIME").to_numpy()
    flags = pd.DataFrame({
        "customer_id": ids,
        "do_not_call": rng.random(n) < 0.18,
        "do_not_solicit": rng.random(n) < 0.03,
        "glba_affiliate_opt_out": rng.random(n) < 0.12,
        "prescreen_opt_out": rng.random(n) < 0.08,
        "deceased_flag": rng.random(n) < 0.003,
        "bankruptcy_flag": rng.random(n) < np.where(sub, 0.05, 0.004),
        "military_lending_flag": rng.random(n) < 0.02,
        "updated_at": AS_OF,
    })
    return prefs, flags


# ---------------------------------------------------------------------------
# Campaign simulation
# ---------------------------------------------------------------------------
def run_campaigns(cust, acct, hist: History, prefs, flags, rng):
    n = len(cust)
    fico = cust["fico_score"].to_numpy()
    band = cust["fico_band"].to_numpy()
    income = cust["annual_income"].to_numpy()
    product = acct["product_code"].to_numpy().copy()
    offers = {o[0]: o for o in OFFERS}

    opt = prefs.pivot(index="customer_id", columns="channel", values="marketing_opt_in").loc[cust["customer_id"]]
    hard_suppress = (flags["do_not_solicit"] | flags["deceased_flag"] | flags["bankruptcy_flag"]).to_numpy()

    contacts, bts = [], []
    bt_seq = [0]
    responders: dict[str, np.ndarray] = {}

    def record_bt(idx, start_mi, amount, offer_id, campaign_id, dates):
        o = offers[offer_id]
        hist.add_bt(idx, start_mi, amount, o[3])
        for j, i in enumerate(idx):
            bt_seq[0] += 1
            fee = max(amount[j] * o[4] / 100, o[5])
            bts.append({
                "bt_id": f"BT{bt_seq[0]:08d}", "account_id": acct["account_id"].iat[i],
                "campaign_id": campaign_id, "bt_date": dates[j], "bt_amount": round(float(amount[j]), 2),
                "promo_apr": o[2], "promo_months": o[3], "bt_fee_pct": o[4],
                "bt_fee_amount": round(float(fee), 2),
                "promo_end_date": (pd.Timestamp(dates[j]) + pd.DateOffset(months=o[3])).date(),
            })

    def organic_bts(m_from, m_to):
        for mi in range(m_from, m_to):
            cand = np.where(hist.active(mi) & hist.revolve[:, mi] & (hist.promo_end_idx <= mi)
                            & (rng.random(n) < 0.0018))[0]
            if len(cand) == 0:
                continue
            amt = np.minimum(hist.limit[cand] * rng.uniform(0.1, 0.45, len(cand)), 15000).round(-1)
            dates = [(MONTHS[mi] + pd.Timedelta(days=int(d))).date() for d in rng.integers(0, 27, len(cand))]
            record_bt(cand, mi, amt, "OFR-BT-STD", None, dates)

    cursor = 0
    for (cid, name, ctype, offer_id, seg, launch, end, channel, prescreen, budget, doc,
         p_treat, p_ctrl) in CAMPAIGNS:
        mi = month_index(launch)
        organic_bts(cursor, mi)
        cursor = mi
        snap = max(mi - 1, 0)
        act = hist.active(snap)
        rev_bal = hist.revolving_balance(snap)
        util = (hist.base_balance[:, snap] + hist.bt[:, snap]) / hist.limit
        no_bt_12 = hist.last_bt_idx < snap - 11
        recent_revolver = hist.revolve[:, max(snap - 2, 0):snap + 1].all(axis=1)
        ch_ok = opt[channel if channel != "SMS" else "SMS"].to_numpy()

        # ---- eligibility per certified segment definition ----
        if seg == "SEG-REVOLVER-BROAD":
            elig = act & (fico >= 620) & recent_revolver & (hist.promo_end_idx <= snap)
        elif seg == "SEG-PRIME-REVOLVER-NOBT12":
            elig = act & (fico >= 670) & recent_revolver & no_bt_12 & (hist.promo_end_idx <= snap)
        elif seg == "SEG-PROMO-EXPIRY-90D":
            elig = act & np.isin(np.arange(n), responders.get("CMP-24Q4-BT", np.array([], int))) \
                & (hist.promo_end_idx > snap) & (hist.promo_end_idx <= snap + 3)
        elif seg == "SEG-AFFLUENT-SPENDER":
            avg_spend = hist.purchase[:, max(snap - 5, 0):snap + 1].mean(axis=1)
            elig = act & (income >= 150000) & (avg_spend >= 2500) & (product != "TRAVEL_ELITE") \
                & (fico >= 700)
        else:
            raise ValueError(seg)

        elig &= ~hard_suppress
        if cid == "CMP-26Q1-BT":
            # Known defect (see PM-26Q1-BT): SMS consent was applied after list pull.
            # ~4% of the file went out without SMS opt-in.
            leak = ~ch_ok & (rng.random(n) < 0.06)
            elig &= (ch_ok | leak)
        else:
            elig &= ch_ok

        idx = np.where(elig)[0]
        holdout = 0.20 if ctype == "RETENTION" else 0.10
        is_ctrl = rng.random(len(idx)) < holdout

        # ---- response propensity ----
        if ctype == "BALANCE_TRANSFER":
            band_m = np.vectorize({"SUPER_PRIME": 0.75, "PRIME": 1.25, "NEAR_PRIME": 1.05, "SUBPRIME": 0.6}.get)(band[idx])
            util_m = np.interp(util[idx], [0, 0.3, 0.6, 0.9], [0.5, 0.9, 1.5, 1.8])
            score = band_m * util_m
        elif ctype == "UPGRADE":
            score = np.interp(hist.purchase[idx, snap], [2000, 5000, 10000], [0.7, 1.2, 1.6])
        else:
            score = np.ones(len(idx))
        score = score / score.mean()
        p = np.where(is_ctrl, p_ctrl * score, p_treat * score)
        resp = rng.random(len(idx)) < np.clip(p, 0, 0.95)

        contact_dates = [launch + timedelta(days=int(d)) for d in rng.integers(0, 10, len(idx))]
        resp_dates = [cd + timedelta(days=int(d)) if r else None
                      for cd, d, r in zip(contact_dates, rng.integers(2, 45, len(idx)), resp)]
        amount = np.zeros(len(idx))

        if ctype == "BALANCE_TRANSFER":
            r = np.where(resp)[0]
            base = rev_bal[idx[r]] * rng.uniform(0.5, 1.1, len(r)) + rng.lognormal(7.3, 0.6, len(r))
            amt = np.minimum(base, hist.limit[idx[r]] * 0.85).round(-1)
            amt = np.maximum(amt, 500)
            # near-prime responders in the broad campaign transferred larger, riskier balances
            if cid == "CMP-24Q4-BT":
                amt *= np.where(band[idx[r]] == "NEAR_PRIME", 1.25, 1.0)
            amount[r] = amt
            rmonths = np.array([month_index(resp_dates[j]) for j in r])
            for um in np.unique(rmonths):
                for ctrl_flag in (False, True):
                    sel = r[(rmonths == um) & (is_ctrl[r] == ctrl_flag)]
                    if len(sel) == 0:
                        continue
                    # holdout customers who take a BT do so via the always-on offer, not the campaign
                    record_bt(idx[sel], int(um), amount[sel],
                              "OFR-BT-STD" if ctrl_flag else offer_id,
                              None if ctrl_flag else cid, [resp_dates[j] for j in sel])
        elif ctype == "UPGRADE":
            r = np.where(resp)[0]
            product[idx[r]] = "TRAVEL_ELITE"
            amount[r] = (hist.purchase[idx[r], snap] * rng.uniform(0.12, 0.30, len(r)) * 12).round(2)
            for j in r:
                k = month_index(resp_dates[j])
                hist.purchase[idx[j], k:] *= 1.18
        elif ctype == "RETENTION":
            # Outcome measured as attrition after promo expiry (see post-mortem)
            pe = hist.promo_end_idx[idx]
            close_p = np.where(is_ctrl, 0.23, np.where(resp, 0.06, 0.17))
            closing = rng.random(len(idx)) < close_p
            for j in np.where(closing)[0]:
                hist.close(np.array([idx[j]]), int(min(pe[j] + rng.integers(0, 3), N_MONTHS)))
            amount[resp] = hist.bt[idx[resp], snap].round(2)

        # complaints
        # holdout (CONTROL) customers were not contacted, so their complaint rate is background only
        if cid == "CMP-26Q1-BT":
            cp = np.where(is_ctrl, 0.0002, np.where(resp, 0.035, 0.0045))
        else:
            cp = np.where(is_ctrl, 0.0002, np.where(resp, 0.004, 0.0004))
        complaint = rng.random(len(idx)) < cp

        contacts.append(pd.DataFrame({
            "campaign_id": cid, "customer_id": cust["customer_id"].to_numpy()[idx],
            "cell": np.where(is_ctrl, "CONTROL", "TREATMENT"),
            "channel": channel, "contact_date": contact_dates,
            "responded": resp, "response_date": resp_dates,
            "response_amount": amount.round(2), "complaint_filed": complaint,
        }))
        if ctype in ("BALANCE_TRANSFER",):
            responders[cid] = idx[resp & ~is_ctrl]
        else:
            responders[cid] = idx[resp]
        # control cell gets no mailing: CONTROL rows are holdouts (channel retained for reporting)

    organic_bts(cursor, N_MONTHS)

    # background attrition (~3% over the window)
    bg = np.where(rng.random(n) < 0.03)[0]
    for i in bg:
        hist.close(np.array([i]), int(rng.integers(hist.open_idx[i] + 1, N_MONTHS + 6)))

    return pd.concat(contacts, ignore_index=True), pd.DataFrame(bts), product


def assemble_monthly(acct: pd.DataFrame, hist: History) -> pd.DataFrame:
    frames = []
    for mi, mstart in enumerate(MONTHS):
        act = hist.active(mi)
        idx = np.where(act)[0]
        stmt = hist.base_balance[idx, mi] + hist.bt[idx, mi]
        rev = hist.revolve[idx, mi] | (hist.bt[idx, mi] > 0)
        pay = np.where(hist.revolve[idx, mi], np.maximum(25, stmt * hist.rng.uniform(0.02, 0.12, len(idx))),
                       stmt)
        pay = np.minimum(pay, stmt)
        revolving = np.where(rev, stmt - pay, 0)
        frames.append(pd.DataFrame({
            "account_id": acct["account_id"].to_numpy()[idx],
            "snapshot_month": mstart.date(),
            "statement_balance": stmt.round(2),
            "revolving_balance": revolving.round(2),
            "bt_balance": hist.bt[idx, mi].round(2),
            "purchase_volume": hist.purchase[idx, mi].round(2),
            "payment_amount": pay.round(2),
            "utilization_pct": (100 * stmt / hist.limit[idx]).round(2),
            "is_revolver": rev,
            "days_past_due": hist.dpd[idx, mi],
        }))
    return pd.concat(frames, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--customers", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/card_offers.duckdb")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    fake = Faker("en_US")
    Faker.seed(args.seed)

    cust = build_customers(args.customers, rng, fake)
    acct = build_accounts(cust, rng)
    hist = History(cust, acct, rng)
    prefs, flags = build_consent(cust, rng)
    contacts, bts, product = run_campaigns(cust, acct, hist, prefs, flags, rng)

    acct["product_code"] = product
    closed = hist.closed_idx < N_MONTHS
    acct.loc[closed, "account_status"] = "CLOSED"
    acct["close_date"] = [MONTHS[i].date() if i < N_MONTHS else None for i in hist.closed_idx]
    monthly = assemble_monthly(acct, hist)

    offers = pd.DataFrame(OFFERS, columns=["offer_id", "offer_type", "promo_apr", "promo_months",
                                           "bt_fee_pct", "bt_fee_min", "bt_window_days", "annual_fee",
                                           "headline_copy", "tc_template_id"])
    camps = pd.DataFrame([c[:11] for c in CAMPAIGNS],
                         columns=["campaign_id", "campaign_name", "campaign_type", "offer_id", "segment_id",
                                  "launch_date", "end_date", "primary_channel", "is_prescreened",
                                  "budget_usd", "post_mortem_doc_id"])
    camps.insert(10, "status", "COMPLETED")
    camps = camps[["campaign_id", "campaign_name", "campaign_type", "offer_id", "segment_id", "launch_date",
                   "end_date", "primary_channel", "is_prescreened", "budget_usd", "status",
                   "post_mortem_doc_id"]]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    con = duckdb.connect(str(out))
    con.execute(SCHEMA_SQL.read_text())
    for table, df in [("core.customers", cust), ("core.card_accounts", acct),
                      ("core.account_monthly", monthly), ("core.balance_transfers", bts),
                      ("mktg.offers", offers), ("mktg.campaigns", camps),
                      ("mktg.campaign_contacts", contacts),
                      ("consent.channel_preferences", prefs), ("consent.privacy_flags", flags)]:
        con.register("df_tmp", df)
        cols = ", ".join(df.columns)
        con.execute(f"INSERT INTO {table} ({cols}) SELECT {cols} FROM df_tmp")
        con.unregister("df_tmp")
    build_catalog(con)
    con.close()
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
