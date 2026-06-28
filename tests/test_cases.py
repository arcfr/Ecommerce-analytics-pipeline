import unittest
import pandas as pd
from datetime import datetime

class TestEdgeCaseScenarios(unittest.TestCase):
    
    def setUp(self):
        # Establish localized verification states
        self.orders_path = "data/cleaned/orders.csv"
        self.items_path = "data/cleaned/order_items.csv"
        
    def test_referential_integrity_orphans(self):
        """Verify what happens when order_items has an order_id not in orders"""
        orders = pd.read_csv(self.orders_path)
        items = pd.read_csv(self.items_path)
        
        # All item keys must exist within master dataset boundaries
        orphan_count = (~items["order_id"].isin(orders["order_id"])).sum()
        self.assertEqual(orphan_count, 0, "Orphan links found in transaction logs!")

    def test_discount_upper_bounds(self):
        """Verify what happens when discount_percent > 100"""
        items = pd.read_csv(self.items_path)
        out_of_bounds_discounts = (items["discount_percent"] > 100).sum()
        self.assertEqual(out_of_bounds_discounts, 0, "Found items with a discount greater than 100%!")

    def test_quantity_non_zero_boundaries(self):
        """Verify what happens when quantity is 0"""
        items = pd.read_csv(self.items_path)
        zero_qty_count = (items["quantity"] == 0).sum()
        self.assertEqual(zero_qty_count, 0, "Found items with a quantity of zero!")

    def test_future_dated_records(self):
        """Verify what happens when order_date is in the future"""
        orders = pd.read_csv(self.orders_path)
        parsed_dates = pd.to_datetime(orders["order_date"])
        
        future_orders = (parsed_dates > datetime.now()).sum()
        # Note: If your synthetically generated dates exceed today's calendar date, this will fail.
        self.assertEqual(future_orders, 0, "Found orders with a future date!")

def run_test_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEdgeCaseScenarios)
    unittest.TextTestRunner(verbosity=2).run(suite)