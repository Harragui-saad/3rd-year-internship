import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from .base import DatabaseInterface

class SQLiteDatabase(DatabaseInterface):
    def __init__(self, db_path: str = "warehouse.db"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self) -> bool:
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            return False
    
    def disconnect(self) -> bool:
        try:
            if self.connection:
                self.connection.close()
            return True
        except Exception as e:
            print(f"Error disconnecting from SQLite: {e}")
            return False
    
    def create_tables(self) -> bool:
        try:
            cursor = self.connection.cursor()
            
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    location TEXT NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    priority TEXT DEFAULT 'normal',
                    price REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'normal',
                    total_amount REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Order items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Shipments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shipments (
                    id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    shipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivered_at TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Zones table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS zones (
                    name TEXT PRIMARY KEY,
                    description TEXT,
                    max_capacity INTEGER DEFAULT 1000
                )
            ''')
            
            # Insert default zones
            zones = [('Zone1', 'Main storage area', 1000),
                    ('Zone2', 'Secondary storage', 800),
                    ('Zone3', 'Fast-moving items', 600),
                    ('Zone4', 'Bulk storage', 1200),
                    ('Zone5', 'Special items', 400)]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO zones (name, description, max_capacity)
                VALUES (?, ?, ?)
            ''', zones)
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
    
    def insert_product(self, product_data: Dict[str, Any]) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO products (id, name, zone, location, quantity, priority, price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data['id'],
                product_data['name'],
                product_data['zone'],
                product_data['location'],
                product_data['quantity'],
                product_data['priority'],
                product_data['price']
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error inserting product: {e}")
            return False
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE products 
                SET name=?, zone=?, location=?, quantity=?, priority=?, price=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                product_data['name'],
                product_data['zone'],
                product_data['location'],
                product_data['quantity'],
                product_data['priority'],
                product_data['price'],
                product_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error getting product: {e}")
            return None
    
    def get_products_by_zone(self, zone: str) -> List[Dict[str, Any]]:
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM products WHERE zone = ?', (zone,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting products by zone: {e}")
            return []
    
    def insert_order(self, order_data: Dict[str, Any]) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO orders (id, customer_name, priority, total_amount)
                VALUES (?, ?, ?, ?)
            ''', (
                order_data['id'],
                order_data['customer_name'],
                order_data['priority'],
                order_data['total_amount']
            ))
            
            # Insert order items
            for item in order_data['items']:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (?, ?, ?, ?)
                ''', (
                    order_data['id'],
                    item['product_id'],
                    item['quantity'],
                    item['unit_price']
                ))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error inserting order: {e}")
            return False
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
            ''', (status, order_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
    
    def get_pending_orders(self) -> List[Dict[str, Any]]:
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT o.*, GROUP_CONCAT(oi.product_id || ':' || oi.quantity) as items
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.status = 'pending'
                GROUP BY o.id
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting pending orders: {e}")
            return []
    
    def insert_shipment(self, shipment_data: Dict[str, Any]) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO shipments (id, order_id, product_id, quantity, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                shipment_data['id'],
                shipment_data['order_id'],
                shipment_data['product_id'],
                shipment_data['quantity'],
                shipment_data['status']
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error inserting shipment: {e}")
            return False
    
    def get_shipment_history(self, product_id: str = None) -> List[Dict[str, Any]]:
        try:
            cursor = self.connection.cursor()
            if product_id:
                cursor.execute('SELECT * FROM shipments WHERE product_id = ?', (product_id,))
            else:
                cursor.execute('SELECT * FROM shipments ORDER BY shipped_at DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting shipment history: {e}")
            return []
    
    def insert_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO transactions (id, type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (
                transaction_data['id'],
                transaction_data['type'],
                transaction_data['amount'],
                transaction_data['description']
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error inserting transaction: {e}")
            return False
    
    def get_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        try:
            cursor = self.connection.cursor()
            
            # Get products in/out
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_products,
                    SUM(CASE WHEN quantity > 0 THEN 1 ELSE 0 END) as in_stock,
                    SUM(CASE WHEN quantity = 0 THEN 1 ELSE 0 END) as out_of_stock
                FROM products
            ''')
            products_result = cursor.fetchone()
            products_stats = dict(products_result) if products_result else {'total_products': 0, 'in_stock': 0, 'out_of_stock': 0}
            
            # Get financial data
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expenses
                FROM transactions
                WHERE strftime('%Y-%m', created_at) = ?
            ''', (f"{year:04d}-{month:02d}",))
            financial_result = cursor.fetchone()
            financial_stats = dict(financial_result) if financial_result else {'total_income': 0, 'total_expenses': 0}
            
            # Get shipment stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_shipments,
                    SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
                FROM shipments
                WHERE strftime('%Y-%m', shipped_at) = ?
            ''', (f"{year:04d}-{month:02d}",))
            shipment_result = cursor.fetchone()
            shipment_stats = dict(shipment_result) if shipment_result else {'total_shipments': 0, 'delivered': 0, 'pending': 0}
            
            return {
                'year': year,
                'month': month,
                'products': products_stats,
                'financial': financial_stats,
                'shipments': shipment_stats
            }
            
        except Exception as e:
            print(f"Error generating monthly report: {e}")
            return {}
    
    def import_from_excel(self, file_path: str) -> bool:
        try:
            if not os.path.exists(file_path):
                print(f"File {file_path} not found")
                return False
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Insert products
            for _, row in df.iterrows():
                product_data = {
                    'id': str(row.get('id', row.get('ID', ''))),
                    'name': str(row.get('name', row.get('Name', ''))),
                    'zone': str(row.get('zone', row.get('Zone', 'Zone1'))),
                    'location': str(row.get('location', row.get('Location', 'A1'))),
                    'quantity': int(row.get('quantity', row.get('Quantity', 0))),
                    'priority': str(row.get('priority', row.get('Priority', 'normal'))),
                    'price': float(row.get('price', row.get('Price', 0.0)))
                }
                self.insert_product(product_data)
            
            return True
            
        except Exception as e:
            print(f"Error importing from Excel: {e}")
            return False
    
    def export_to_excel(self, data: List[Dict[str, Any]], file_path: str) -> bool:
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
