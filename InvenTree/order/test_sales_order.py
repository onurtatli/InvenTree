# -*- coding: utf-8 -*-

from django.test import TestCase

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from company.models import Company
from stock.models import StockItem
from order.models import SalesOrder, SalesOrderLineItem, SalesOrderAllocation
from part.models import Part
from InvenTree import status_codes as status


class SalesOrderTest(TestCase):
    """
    Run tests to ensure that the SalesOrder model is working correctly.

    """

    def setUp(self):

        # Create a Company to ship the goods to
        self.customer = Company.objects.create(name="ABC Co", description="My customer", is_customer=True)

        # Create a Part to ship
        self.part = Part.objects.create(name='Spanner', salable=True, description='A spanner that I sell')

        # Create some stock!
        StockItem.objects.create(part=self.part, quantity=100)
        StockItem.objects.create(part=self.part, quantity=200)

        # Create a SalesOrder to ship against
        self.order = SalesOrder.objects.create(
            customer=self.customer,
            reference='1234',
            customer_reference='ABC 55555'
        )

        # Create a line item
        self.line = SalesOrderLineItem.objects.create(quantity=50, order=self.order, part=self.part)

    def test_empty_order(self):
        self.assertEqual(self.line.quantity, 50)
        self.assertEqual(self.line.allocated_quantity(), 0)
        self.assertEqual(self.line.fulfilled_quantity(), 0)
        self.assertFalse(self.line.is_fully_allocated())
        self.assertFalse(self.line.is_over_allocated())

        self.assertTrue(self.order.is_pending)
        self.assertFalse(self.order.is_fully_allocated())

    def test_add_duplicate_line_item(self):
        # Adding a duplicate line item to a SalesOrder must throw an error
        
        with self.assertRaises(IntegrityError):
            SalesOrderLineItem.objects.create(order=self.order, part=self.part)

    def allocate_stock(self, full=True):
        # Allocate stock to the order
        SalesOrderAllocation.objects.create(
            line=self.line,
            item=StockItem.objects.get(pk=1),
            quantity=25)

        SalesOrderAllocation.objects.create(
            line=self.line,
            item=StockItem.objects.get(pk=2),
            quantity=25 if full else 20
        )

    def test_allocate_partial(self):
        # Partially allocate stock
        self.allocate_stock(False)

        self.assertFalse(self.order.is_fully_allocated())
        self.assertFalse(self.line.is_fully_allocated())
        self.assertEqual(self.line.allocated_quantity(), 45)
        self.assertEqual(self.line.fulfilled_quantity(), 0)

    def test_allocate_full(self):
        # Fully allocate stock
        self.allocate_stock(True)

        self.assertTrue(self.order.is_fully_allocated())
        self.assertTrue(self.line.is_fully_allocated())
        self.assertEqual(self.line.allocated_quantity(), 50)
    
    def test_order_cancel(self):
        # Allocate line items then cancel the order

        self.allocate_stock(True)

        self.assertEqual(SalesOrderAllocation.objects.count(), 2)
        self.assertEqual(self.order.status, status.SalesOrderStatus.PENDING)

        self.order.cancel_order()
        self.assertEqual(SalesOrderAllocation.objects.count(), 0)
        self.assertEqual(self.order.status, status.SalesOrderStatus.CANCELLED)

        # Now try to ship it - should fail
        with self.assertRaises(ValidationError):
            self.order.ship_order(None)

    def test_ship_order(self):
        # Allocate line items, then ship the order

        # Assert some stuff before we run the test
        # Initially there are two stock items
        self.assertEqual(StockItem.objects.count(), 2)

        # Take 25 units from each StockItem
        self.allocate_stock(True)

        self.assertEqual(SalesOrderAllocation.objects.count(), 2)

        self.order.ship_order(None)

        # There should now be 4 stock items
        self.assertEqual(StockItem.objects.count(), 4)

        self.assertEqual(StockItem.objects.get(pk=1).quantity, 75)
        self.assertEqual(StockItem.objects.get(pk=2).quantity, 175)
        self.assertEqual(StockItem.objects.get(pk=3).quantity, 25)
        self.assertEqual(StockItem.objects.get(pk=3).quantity, 25)
    
        self.assertEqual(StockItem.objects.get(pk=1).sales_order, None)
        self.assertEqual(StockItem.objects.get(pk=2).sales_order, None)
        self.assertEqual(StockItem.objects.get(pk=3).sales_order, self.order)
        self.assertEqual(StockItem.objects.get(pk=4).sales_order, self.order)

        # And no allocations
        self.assertEqual(SalesOrderAllocation.objects.count(), 0)

        self.assertEqual(self.order.status, status.SalesOrderStatus.SHIPPED)
        
        self.assertTrue(self.order.is_fully_allocated())
        self.assertTrue(self.line.is_fully_allocated())
        self.assertEqual(self.line.fulfilled_quantity(), 50)
        self.assertEqual(self.line.allocated_quantity(), 0)
