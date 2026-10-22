import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_local_demo import run


class BatchReferenceTests(unittest.TestCase):
    def test_filtering_deduplication_and_export_reconcile(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw"
            raw.mkdir()
            customers = [{"customer_id": 1, "name": "A", "country": "India"},
                         {"customer_id": 2, "name": "B", "country": "Japan"}]
            base = {"order_time": "2026-01-01 10:00:00", "status": "SUCCESS"}
            orders = [
                {**base, "order_id": 1, "customer_id": 1, "amount": "20.25"},
                {**base, "order_id": 1, "customer_id": 1, "amount": "20.25"},
                {**base, "order_id": 2, "customer_id": 2, "amount": "9.75"},
                {**base, "order_id": 3, "customer_id": 1, "amount": -5},
                {**base, "order_id": 4, "customer_id": 1, "amount": 7, "status": "FAILED"},
                {**base, "order_id": 5, "customer_id": None, "amount": 8},
                {**base, "order_id": 6, "customer_id": 1, "amount": None},
            ]
            (raw / "customers.json").write_text(json.dumps(customers))
            source = json.dumps(orders)
            (raw / "orders.json").write_text(source)
            output = root / "output"
            report = run(raw, output)
            self.assertEqual(report["counts"]["raw_orders"], 7)
            self.assertEqual(report["counts"]["silver_orders"], 5)
            self.assertEqual(report["counts"]["eligible_gold_orders"], 2)
            self.assertEqual(report["counts"]["duplicate_orders_removed"], 1)
            self.assertEqual(report["counts"]["null_amount_orders"], 1)
            self.assertEqual(report["total_revenue"], 30)
            self.assertEqual(sum(row["total_revenue"] for row in report["revenue_by_country"]), 30)
            with (output / "daily_revenue.csv").open() as handle:
                exported = list(csv.DictReader(handle))
            self.assertEqual(exported, [{"order_date": "2026-01-01", "daily_revenue": "30.0"}])
            self.assertEqual((raw / "orders.json").read_text(), source)
            self.assertTrue((output / "index.html").is_file())

    def test_unmatched_customer_is_visible_in_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "customers.json").write_text("[]")
            (root / "orders.json").write_text(json.dumps([
                {"order_id": 1, "customer_id": 99, "amount": 10,
                 "status": "SUCCESS", "order_time": "2026-01-01"}
            ]))
            report = run(root, root / "output")
            self.assertEqual(report["counts"]["unmatched_customer_orders"], 1)
            self.assertEqual(report["total_revenue"], 10)
            self.assertEqual(report["revenue_by_country"], [])


if __name__ == "__main__":
    unittest.main()
