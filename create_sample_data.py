#!/usr/bin/env python3
"""
Sample Data Generator for Warehouse Management System
Creates sample Excel files with warehouse data for testing
"""

import pandas as pd
import random
from datetime import datetime, timedelta

def create_sample_products():
    """Create sample product data"""
    products = []
    
    # Sample product names
    product_names = [
        "Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Webcam",
        "USB Drive", "External HDD", "Printer", "Scanner", "Tablet", "Phone",
        "Charger", "Cable", "Adapter", "Speaker", "Microphone", "Camera",
        "Router", "Switch", "Server", "Workstation", "Notebook", "Pen",
        "Paper", "Stapler", "Tape", "Glue", "Scissors", "Ruler"
    ]
    
    # Zones and locations
    zones = ["Zone1", "Zone2", "Zone3", "Zone4", "Zone5"]
    locations = ["A", "B", "C", "D", "E"]
    
    for i in range(100):  # Create 100 sample products
        product = {
            'id': f"P{i+1:03d}",
            'name': random.choice(product_names),
            'zone': random.choice(zones),
            'location': f"{random.choice(locations)}{random.randint(1, 20)}",
            'quantity': random.randint(0, 100),
            'priority': random.choice(['urgent', 'normal', 'low']),
            'price': round(random.uniform(10.0, 1000.0), 2)
        }
        products.append(product)
    
    return products

def create_sample_orders():
    """Create sample order data"""
    orders = []
    
    # Sample customer names
    customer_names = [
        "Acme Corp", "Tech Solutions", "Global Industries", "Local Business",
        "Startup Inc", "Enterprise Ltd", "Small Company", "Medium Corp",
        "Big Business", "Online Store", "Retail Chain", "Wholesale Co",
        "Distribution Inc", "Logistics Ltd", "Supply Chain", "Procurement Co"
    ]
    
    # Sample order statuses
    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    
    for i in range(50):  # Create 50 sample orders
        order = {
            'id': f"O{i+1:03d}",
            'customer_name': random.choice(customer_names),
            'status': random.choice(statuses),
            'priority': random.choice(['urgent', 'normal', 'low']),
            'total_amount': round(random.uniform(100.0, 5000.0), 2),
            'created_at': datetime.now() - timedelta(days=random.randint(0, 30))
        }
        orders.append(order)
    
    return orders

def create_sample_transactions():
    """Create sample transaction data"""
    transactions = []
    
    # Sample transaction descriptions
    descriptions = [
        "Product sale", "Shipping cost", "Tax payment", "Insurance",
        "Maintenance", "Utilities", "Rent", "Salary", "Equipment purchase",
        "Software license", "Training", "Marketing", "Advertising"
    ]
    
    for i in range(100):  # Create 100 sample transactions
        transaction = {
            'id': f"T{i+1:03d}",
            'type': random.choice(['income', 'expense']),
            'amount': round(random.uniform(50.0, 2000.0), 2),
            'description': random.choice(descriptions),
            'created_at': datetime.now() - timedelta(days=random.randint(0, 90))
        }
        transactions.append(transaction)
    
    return transactions

def create_sample_shipments():
    """Create sample shipment data"""
    shipments = []
    
    # Sample shipment statuses
    statuses = ["pending", "shipped", "delivered", "cancelled"]
    
    for i in range(75):  # Create 75 sample shipments
        shipment = {
            'id': f"S{i+1:03d}",
            'order_id': f"O{random.randint(1, 50):03d}",
            'product_id': f"P{random.randint(1, 100):03d}",
            'quantity': random.randint(1, 10),
            'status': random.choice(statuses),
            'shipped_at': datetime.now() - timedelta(days=random.randint(0, 30)),
            'delivered_at': datetime.now() - timedelta(days=random.randint(0, 15)) if random.random() > 0.3 else None
        }
        shipments.append(shipment)
    
    return shipments

def main():
    """Main function to create all sample data files"""
    print("Creating sample data for Warehouse Management System...")
    
    # Create products data
    print("Generating sample products...")
    products = create_sample_products()
    products_df = pd.DataFrame(products)
    products_df.to_excel('sample_products.xlsx', index=False)
    print(f"Created sample_products.xlsx with {len(products)} products")
    
    # Create orders data
    print("Generating sample orders...")
    orders = create_sample_orders()
    orders_df = pd.DataFrame(orders)
    orders_df.to_excel('sample_orders.xlsx', index=False)
    print(f"Created sample_orders.xlsx with {len(orders)} orders")
    
    # Create transactions data
    print("Generating sample transactions...")
    transactions = create_sample_transactions()
    transactions_df = pd.DataFrame(transactions)
    transactions_df.to_excel('sample_transactions.xlsx', index=False)
    print(f"Created sample_transactions.xlsx with {len(transactions)} transactions")
    
    # Create shipments data
    print("Generating sample shipments...")
    shipments = create_sample_shipments()
    shipments_df = pd.DataFrame(shipments)
    shipments_df.to_excel('sample_shipments.xlsx', index=False)
    print(f"Created sample_shipments.xlsx with {len(shipments)} shipments")
    
    # Create comprehensive data file
    print("Creating comprehensive sample data...")
    comprehensive_data = {
        'id': [p['id'] for p in products],
        'name': [p['name'] for p in products],
        'zone': [p['zone'] for p in products],
        'location': [p['location'] for p in products],
        'quantity': [p['quantity'] for p in products],
        'priority': [p['priority'] for p in products],
        'price': [p['price'] for p in products]
    }
    
    comprehensive_df = pd.DataFrame(comprehensive_data)
    comprehensive_df.to_excel('sample_data.xlsx', index=False)
    print(f"Created sample_data.xlsx with {len(products)} products")
    
    print("\nSample data files created successfully!")
    print("\nFiles created:")
    print("- sample_products.xlsx: Product inventory data")
    print("- sample_orders.xlsx: Customer order data")
    print("- sample_transactions.xlsx: Financial transaction data")
    print("- sample_shipments.xlsx: Shipment tracking data")
    print("- sample_data.xlsx: Comprehensive product data (for import testing)")
    
    print("\nYou can now use these files to test the warehouse management system:")
    print("1. Import data: python main.py --import-excel sample_data.xlsx")
    print("2. Launch GUI: python main.py --gui")
    print("3. Run optimization: python main.py --optimize-route")

if __name__ == '__main__':
    main()
