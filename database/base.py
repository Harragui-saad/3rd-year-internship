from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd

class DatabaseInterface(ABC):
    """Abstract base class for database operations"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the database"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the database"""
        pass
    
    @abstractmethod
    def create_tables(self) -> bool:
        """Create necessary tables if they don't exist"""
        pass
    
    @abstractmethod
    def insert_product(self, product_data: Dict[str, Any]) -> bool:
        """Insert a new product"""
        pass
    
    @abstractmethod
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> bool:
        """Update an existing product"""
        pass
    
    @abstractmethod
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get a product by ID"""
        pass
    
    @abstractmethod
    def get_products_by_zone(self, zone: str) -> List[Dict[str, Any]]:
        """Get all products in a specific zone"""
        pass
    
    @abstractmethod
    def insert_order(self, order_data: Dict[str, Any]) -> bool:
        """Insert a new order"""
        pass
    
    @abstractmethod
    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        pass
    
    @abstractmethod
    def get_pending_orders(self) -> List[Dict[str, Any]]:
        """Get all pending orders"""
        pass
    
    @abstractmethod
    def insert_shipment(self, shipment_data: Dict[str, Any]) -> bool:
        """Insert a new shipment"""
        pass
    
    @abstractmethod
    def get_shipment_history(self, product_id: str = None) -> List[Dict[str, Any]]:
        """Get shipment history"""
        pass
    
    @abstractmethod
    def insert_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """Insert a financial transaction"""
        pass
    
    @abstractmethod
    def get_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """Generate monthly report data"""
        pass
    
    @abstractmethod
    def import_from_excel(self, file_path: str) -> bool:
        """Import data from Excel file"""
        pass
    
    @abstractmethod
    def export_to_excel(self, data: List[Dict[str, Any]], file_path: str) -> bool:
        """Export data to Excel file"""
        pass



