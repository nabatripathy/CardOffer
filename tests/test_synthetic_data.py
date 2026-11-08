"""Invariant checks on a small synthetic build. Run: pytest -q"""
import subprocess
import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def con(tmp_path_factory):
    db = tmp_path_factory.mktemp("db") / "test.duckdb"
    subprocess.run([sys.executable, str(ROOT / "data/generator/generate.py"),
                    "--customers", "5000", "--out", str(db)], check=True, cwd=ROOT / "data/generator")
    c = duckdb.connect(str(db), read_only=True)
    yield c
    c.close()


def scalar(con, sql):
    return con.execute(sql).fetchone()[0]


def test_row_counts(con):
    assert scalar(con, "select count(*) from core.customers") == 5000
    assert scalar(con, "select count(*) from core.card_accounts") == 5000
    assert scalar(con, "select count(*) from mktg.campaigns") == 5
    assert scalar(con, "select count(*) from consent.channel_preferences") == 20000


def test_no_suppressed_customers_contacted(con):
    n = scalar(con, """select count(*) from mktg.campaign_contacts k join consent.privacy_flags f using(customer_id)
                       where f.do_not_solicit or f.deceased_flag or f.bankruptcy_flag""")
    assert n == 0


def test_consent_respected_except_known_incident(con):
    n = scalar(con, """select count(*) from mktg.campaign_contacts k
                       join consent.channel_preferences p on p.customer_id=k.customer_id and p.channel=k.channel
                       where not p.marketing_opt_in and k.campaign_id <> 'CMP-26Q1-BT'""")
    assert n == 0


def test_prime_segment_campaigns_are_prime(con):
    assert scalar(con, """select min(c.fico_score) from mktg.campaign_contacts k join core.customers c using(customer_id)
                          where campaign_id in ('CMP-25Q3-BT','CMP-26Q1-BT')""") >= 670


def test_treatment_beats_control(con):
    rows = con.execute("""select campaign_id,
        avg(case when cell='TREATMENT' then responded::int end) t,
        avg(case when cell='CONTROL' then responded::int end) c
        from mktg.campaign_contacts where campaign_id like '%BT' group by 1""").fetchall()
    for cid, t, c in rows:
        assert t > c, cid


def test_prohibited_attributes_flagged(con):
    rows = con.execute("""select column_name from gov.column_classifications
                          where classification='PROHIBITED_BASIS' and not allowed_for_targeting""").fetchall()
    assert {r[0] for r in rows} == {"date_of_birth", "gender", "marital_status"}


def test_certified_segment_sql_runs(con):
    sql = scalar(con, "select sql_definition from gov.segment_definitions where segment_id='SEG-PRIME-REVOLVER-NOBT12'")
    n = scalar(con, f"select count(*) from ({sql.replace('{as_of_month}', '2026-10-01')})")
    assert n > 0
