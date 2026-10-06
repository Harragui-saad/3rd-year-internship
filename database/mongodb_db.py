from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import os
from .base import DatabaseInterface

class MongoDBDatabase(DatabaseInterface):
    def __init__(self, host: str = "localhost", port: int = 27017, database: str = "warehouse"):
        self.host = host
        self.port = port
        self.database_name = database
        self.client = None
        self.db = None
        
    def connect(self) -> bool:
        try:
            self.client = MongoClient(self.host, self.port)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.close()
            return True
        except Exception as e:
            print(f"Error disconnecting from MongoDB: {e}")
            return False
    
    def create_tables(self) -> bool:
        try:
            # Create collections with validation schemas
            # Products collection
            self.db.create_collection("products", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id", "name", "zone", "location", "quantity", "priority", "price"],
                    "properties": {
                        "id": {"bsonType": "string"},
                        "name": {"bsonType": "string"},
                        "zone": {"bsonType": "string"},
                        "location": {"bsonType": "string"},
                        "quantity": {"bsonType": "int"},
                        "priority": {"enum": ["urgent", "normal", "low"]},
                        "price": {"bsonType": "double"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"}
                    }
                }
            })
            
            # Orders collection
            self.db.create_collection("orders", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id", "customer_name", "status", "priority", "total_amount"],
                    "properties": {
                        "id": {"bsonType": "string"},
                        "customer_name": {"bsonType": "string"},
                        "status": {"enum": ["pending", "processing", "shipped", "delivered", "cancelled"]},
                        "priority": {"enum": ["urgent", "normal", "low"]},
                        "total_amount": {"bsonType": "double"},
                        "items": {"bsonType": "array"},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"}
                    }
                }
            })
            
            # Shipments collection
            self.db.create_collection("shipments", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id", "order_id", "product_id", "quantity", "status"],
                    "properties": {
                        "id": {"bsonType": "string"},
                        "order_id": {"bsonType": "string"},
                        "product_id": {"bsonType": "string"},
                        "quantity": {"bsonType": "int"},
                        "status": {"enum": ["pending", "shipped", "delivered", "cancelled"]},
                        "shipped_at": {"bsonType": "date"},
                        "delivered_at": {"bsonType": "date"}
                    }
                }
            })
            
            # Transactions collection
            self.db.create_collection("transactions", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id", "type", "amount", "description"],
                    "properties": {
                        "id": {"bsonType": "string"},
                        "type": {"enum": ["income", "expense"]},
                        "amount": {"bsonType": "double"},
                        "description": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"}
                    }
                }
            })
            
            # Zones collection
            self.db.create_collection("zones", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["name", "description", "max_capacity"],
                    "properties": {
                        "name": {"bsonType": "string"},
                        "description": {"bsonType": "string"},
                        "max_capacity": {"bsonType": "int"}
                    }
                }
            })
            
            # Insert default zones
            zones = [
                {"name": "Zone1", "description": "Main storage area", "max_capacity": 1000},
                {"name": "Zone2", "description": "Secondary storage", "max_capacity": 800},
                {"name": "Zone3", "description": "Fast-moving items", "max_capacity": 600},
                {"name": "Zone4", "description": "Bulk storage", "max_capacity": 1200},
                {"name": "Zone5", "description": "Special items", "max_capacity": 400}
            ]
            
            for zone in zones:
                self.db.zones.update_one(
                    {"name": zone["name"]}, 
                    {"$setOnInsert": zone}, 
                    upsert=True
                )
            
            # Create indexes for better performance
            self.db.products.create_index("id", unique=True)
            self.db.products.create_index("zone")
            self.db.orders.create_index("id", unique=True)
            self.db.orders.create_index("status")
            self.db.shipments.create_index("id", unique=True)
            self.db.shipments.create_index("product_id")
            
            return True
            
        except Exception as e:
            print(f"Error creating collections: {e}")
            return False
    
    def insert_product(self, product_data: Dict[str, Any]) -> bool:
        try:
            product_data['created_at'] = datetime.now()
            product_data['updated_at'] = datetime.now()
            self.db.products.insert_one(product_data)
            return True
        except Exception as e:
            print(f"Error inserting product: {e}")
            return False
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> bool:
        try:
            product_data['updated_at'] = datetime.now()
            result = self.db.products.update_one(
                {"id": product_id},
                {"$set": product_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        try:
            product = self.db.products.find_one({"id": product_id})
            if product:
                product['_id'] = str(product['_id'])  # Convert ObjectId to string
            return product
        except Exception as e:
            print(f"Error getting product: {e}")
            return None
    
    def get_products_by_zone(self, zone: str) -> List[Dict[str, Any]]:
        try:
            products = list(self.db.products.find({"zone": zone}))
            for product in products:
                product['_id'] = str(product['_id'])
            return products
        except Exception as e:
            print(f"Error getting products by zone: {e}")
            return []
    
    def insert_order(self, order_data: Dict[str, Any]) -> bool:
        try:
            order_data['created_at'] = datetime.now()
            order_data['updated_at'] = datetime.now()
            self.db.orders.insert_one(order_data)
            return True
        except Exception as e:
            print(f"Error inserting order: {e}")
            return False
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        try:
            result = self.db.orders.update_one(
                {"id": order_id},
                {"$set": {"status": status, "updated_at": datetime.now()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
    
    def get_pending_orders(self) -> List[Dict[str, Any]]:
        try:
            orders = list(self.db.orders.find({"status": "pending"}))
            for order in orders:
                order['_id'] = str(order['_id'])
            return orders
        except Exception as e:
            print(f"Error getting pending orders: {e}")
            return []
    
    def insert_shipment(self, shipment_data: Dict[str, Any]) -> bool:
        try:
            shipment_data['shipped_at'] = datetime.now()
            self.db.shipments.insert_one(shipment_data)
            return True
        except Exception as e:
            print(f"Error inserting shipment: {e}")
            return False
    
    def get_shipment_history(self, product_id: str = None) -> List[Dict[str, Any]]:
        try:
            if product_id:
                shipments = list(self.db.shipments.find({"product_id": product_id}).sort("shipped_at", -1))
            else:
                shipments = list(self.db.shipments.find().sort("shipped_at", -1))
            
            for shipment in shipments:
                shipment['_id'] = str(shipment['_id'])
            return shipments
        except Exception as e:
            print(f"Error getting shipment history: {e}")
            return []
    
    def insert_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        try:
            transaction_data['created_at'] = datetime.now()
            self.db.transactions.insert_one(transaction_data)
            return True
        except Exception as e:
            print(f"Error inserting transaction: {e}")
            return False
    
    def get_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        try:
            # Get products stats
            total_products = self.db.products.count_documents({})
            in_stock = self.db.products.count_documents({"quantity": {"$gt": 0}})
            out_of_stock = self.db.products.count_documents({"quantity": 0})
            
            # Get financial data for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            income_pipeline = [
                {"$match": {"type": "income", "created_at": {"$gte": start_date, "$lt": end_date}}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            expense_pipeline = [
                {"$match": {"type": "expense", "created_at": {"$gte": start_date, "$lt": end_date}}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            
            income_result = list(self.db.transactions.aggregate(income_pipeline))
            expense_result = list(self.db.transactions.aggregate(expense_pipeline))
            
            total_income = income_result[0]['total'] if income_result else 0
            total_expenses = expense_result[0]['total'] if expense_result else 0
            
            # Get shipment stats for the month
            shipment_pipeline = [
                {"$match": {"shipped_at": {"$gte": start_date, "$lt": end_date}}},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]
            
            shipment_stats = list(self.db.shipments.aggregate(shipment_pipeline))
            shipment_counts = {stat['_id']: stat['count'] for stat in shipment_stats}
            
            return {
                'year': year,
                'month': month,
                'products': {
                    'total_products': total_products,
                    'in_stock': in_stock,
                    'out_of_stock': out_of_stock
                },
                'financial': {
                    'total_income': total_income,
                    'total_expenses': total_expenses
                },
                'shipments': {
                    'total_shipments': sum(shipment_counts.values()),
                    'delivered': shipment_counts.get('delivered', 0),
                    'pending': shipment_counts.get('pending', 0)
                }
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
            # Remove MongoDB ObjectId fields
            clean_data = []
            for item in data:
                clean_item = item.copy()
                if '_id' in clean_item:
                    del clean_item['_id']
                clean_data.append(clean_item)
            
            df = pd.DataFrame(clean_data)
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
