"""Run a credential-free SQLite reference for the batch notebook transformations.

This reference does not run Spark, Delta Lake, Kafka or Snowflake. It makes the
committed raw data and the batch transformation rules reproducible locally.
"""

import argparse
import csv
import json
import math
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def number(value):
    try:
        result = float(str(value).replace(",", ""))
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def identifier(value):
    parsed = number(value)
    return int(parsed) if parsed is not None else None


def run(raw_dir: Path, output_dir: Path) -> dict:
    customers = json.loads((raw_dir / "customers.json").read_text())
    orders = json.loads((raw_dir / "orders.json").read_text())
    if not isinstance(customers, list) or not isinstance(orders, list):
        raise ValueError("customers.json and orders.json must contain JSON arrays")
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    try:
        db.executescript("""
            CREATE TABLE bronze_customers(customer_id INTEGER, name TEXT, country TEXT);
            CREATE TABLE bronze_orders(source_row INTEGER, order_id INTEGER,
                customer_id INTEGER, amount REAL, status TEXT, order_time TEXT);
        """)
        db.executemany("INSERT INTO bronze_customers VALUES (?,?,?)", [
            (identifier(row.get("customer_id")), row.get("name"), row.get("country"))
            for row in customers
        ])
        db.executemany("INSERT INTO bronze_orders VALUES (?,?,?,?,?,?)", [
            (i, identifier(row.get("order_id")), identifier(row.get("customer_id")),
             number(row.get("amount")), row.get("status"), row.get("order_time"))
            for i, row in enumerate(orders)
        ])
        db.executescript("""
            CREATE TABLE silver_orders AS
            WITH ranked AS (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY order_id ORDER BY source_row
                ) AS row_rank FROM bronze_orders WHERE amount IS NOT NULL
            )
            SELECT order_id, customer_id, amount, status, order_time,
                date(order_time) AS order_date FROM ranked WHERE row_rank=1;
            CREATE TABLE gold_orders AS SELECT * FROM silver_orders
                WHERE status='SUCCESS' AND amount>0 AND customer_id IS NOT NULL;
        """)
        queries = {
            "daily_revenue": "SELECT order_date, ROUND(SUM(amount),2) AS daily_revenue FROM gold_orders GROUP BY order_date ORDER BY order_date",
            "top_customers": "SELECT c.name, ROUND(SUM(o.amount),2) AS total_spent FROM gold_orders o JOIN bronze_customers c USING(customer_id) GROUP BY c.name ORDER BY total_spent DESC, c.name",
            "revenue_by_country": "SELECT c.country, ROUND(SUM(o.amount),2) AS total_revenue FROM gold_orders o JOIN bronze_customers c USING(customer_id) GROUP BY c.country ORDER BY total_revenue DESC, c.country",
        }
        results = {name: [dict(row) for row in db.execute(sql)] for name, sql in queries.items()}
        count = lambda sql: db.execute(sql).fetchone()[0]
        report = {
            "engine": "SQLite local batch reference",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "data/raw/customers.json and data/raw/orders.json",
            "counts": {
                "raw_customers": len(customers),
                "raw_orders": len(orders),
                "null_amount_orders": count("SELECT COUNT(*) FROM bronze_orders WHERE amount IS NULL"),
                "silver_orders": count("SELECT COUNT(*) FROM silver_orders"),
                "duplicate_orders_removed": count("SELECT COUNT(*) FROM bronze_orders WHERE amount IS NOT NULL") - count("SELECT COUNT(*) FROM silver_orders"),
                "eligible_gold_orders": count("SELECT COUNT(*) FROM gold_orders"),
                "unmatched_customer_orders": count("SELECT COUNT(*) FROM gold_orders o WHERE NOT EXISTS (SELECT 1 FROM bronze_customers c WHERE c.customer_id=o.customer_id)"),
            },
            "total_revenue": count("SELECT COALESCE(ROUND(SUM(amount),2),0) FROM gold_orders"),
            **results,
            "scope": "Local batch reference only. No cloud jobs or streaming services are running in this demonstration.",
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, sql in queries.items():
            cursor = db.execute(sql)
            with (output_dir / f"{name}.csv").open("w", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(column[0] for column in cursor.description)
                writer.writerows(cursor.fetchall())
        (output_dir / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        for asset in (ROOT / "demo").iterdir():
            destination = output_dir / asset.name
            if asset.is_dir():
                shutil.copytree(asset, destination, dirs_exist_ok=True)
            else:
                shutil.copyfile(asset, destination)
        return report
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "local-demo")
    args = parser.parse_args()
    report = run(args.raw_dir, args.output_dir)
    print(json.dumps({"output": str(args.output_dir), "counts": report["counts"], "total_revenue": report["total_revenue"]}, indent=2))
