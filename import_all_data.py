#!/usr/bin/env python3
"""
Comprehensive Data Import Script for Warehouse Management System
Imports all sample data (products, orders, transactions, shipments) into the database
"""

import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.factory import DatabaseFactory

def import_orders(database, file_path: str):
    """Import orders from Excel file"""
    try:
        if not os.path.exists(file_path):
            print(f"Orders file {file_path} not found")
            return False
        
        df = pd.read_excel(file_path)
        print(f"Importing {len(df)} orders...")
        
        for _, row in df.iterrows():
            order_data = {
                'id': str(row.get('id', row.get('ID', ''))),
                'customer_name': str(row.get('customer_name', row.get('Customer', 'Unknown'))),
                'status': str(row.get('status', row.get('Status', 'pending'))),
                'priority': str(row.get('priority', row.get('Priority', 'normal'))),
                'total_amount': float(row.get('total_amount', row.get('Total', 0.0))),
                'items': [{'product_id': f"P{row.get('id', '001')}", 'quantity': 1, 'unit_price': float(row.get('total_amount', 0.0))}],
                'created_at': row.get('created_at', datetime.now()),
                'updated_at': datetime.now()
            }
            
            # Insert order
            if not database.insert_order(order_data):
                print(f"Failed to insert order {order_data['id']}")
        
        print("Orders imported successfully!")
        return True
        
    except Exception as e:
        print(f"Error importing orders: {e}")
        return False

def import_transactions(database, file_path: str):
    """Import transactions from Excel file"""
    try:
        if not os.path.exists(file_path):
            print(f"Transactions file {file_path} not found")
            return False
        
        df = pd.read_excel(file_path)
        print(f"Importing {len(df)} transactions...")
        
        for _, row in df.iterrows():
            transaction_data = {
                'id': str(row.get('id', row.get('ID', ''))),
                'type': str(row.get('type', row.get('Type', 'income'))),
                'amount': float(row.get('amount', row.get('Amount', 0.0))),
                'description': str(row.get('description', row.get('Description', 'Transaction'))),
                'created_at': row.get('created_at', datetime.now())
            }
            
            # Insert transaction
            if not database.insert_transaction(transaction_data):
                print(f"Failed to insert transaction {transaction_data['id']}")
        
        print("Transactions imported successfully!")
        return True
        
    except Exception as e:
        print(f"Error importing transactions: {e}")
        return False

def import_shipments(database, file_path: str):
    """Import shipments from Excel file"""
    try:
        if not os.path.exists(file_path):
            print(f"Shipments file {file_path} not found")
            return False
        
        df = pd.read_excel(file_path)
        print(f"Importing {len(df)} shipments...")
        
        for _, row in df.iterrows():
            shipment_data = {
                'id': str(row.get('id', row.get('ID', ''))),
                'order_id': str(row.get('order_id', row.get('OrderID', ''))),
                'product_id': str(row.get('product_id', row.get('ProductID', ''))),
                'quantity': int(row.get('quantity', row.get('Quantity', 1))),
                'status': str(row.get('status', row.get('Status', 'pending'))),
                'shipped_at': row.get('shipped_at', datetime.now()),
                'delivered_at': row.get('delivered_at')
            }
            
            # Insert shipment
            if not database.insert_shipment(shipment_data):
                print(f"Failed to insert shipment {shipment_data['id']}")
        
        print("Shipments imported successfully!")
        return True
        
    except Exception as e:
        print(f"Error importing shipments: {e}")
        return False

def main():
    """Main function to import all data"""
    print("Warehouse Management System - Comprehensive Data Import")
    print("=" * 60)
    
    try:
        # Initialize database
        print("Connecting to SQLite database...")
        database = DatabaseFactory.create_database('sqlite')
        
        if not database.connect():
            print("Failed to connect to database")
            return
        
        print("Database connected successfully")
        database.create_tables()
        
        # Import products (already done, but let's verify)
        print("\n1. Importing products...")
        if os.path.exists('sample_data.xlsx'):
            if database.import_from_excel('sample_data.xlsx'):
                print("Products imported successfully")
            else:
                print("Failed to import products")
        
        # Import orders
        print("\n2. Importing orders...")
        if os.path.exists('sample_orders.xlsx'):
            import_orders(database, 'sample_orders.xlsx')
        
        # Import transactions
        print("\n3. Importing transactions...")
        if os.path.exists('sample_transactions.xlsx'):
            import_transactions(database, 'sample_transactions.xlsx')
        
        # Import shipments
        print("\n4. Importing shipments...")
        if os.path.exists('sample_shipments.xlsx'):
            import_shipments(database, 'sample_shipments.xlsx')
        
        print("\n" + "=" * 60)
        print("All data imported successfully!")
        print("\nYou can now:")
        print("1. Launch GUI: python main.py --gui")
        print("2. Run optimization: python main.py --optimize-route")
        print("3. Generate reports: python main.py --generate-report")
        
        # Cleanup
        database.disconnect()
        print("\nDatabase disconnected")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())



