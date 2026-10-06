#!/usr/bin/env python3
"""
Test script for Warehouse Management System
Tests basic functionality without requiring external dependencies
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from config import DATABASE_CONFIG, WAREHOUSE_CONFIG, QL_CONFIG
        print("✓ Configuration imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from database.base import DatabaseInterface
        print("✓ Database interface imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import database interface: {e}")
        return False
    
    try:
        from database.factory import DatabaseFactory
        print("✓ Database factory imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import database factory: {e}")
        return False
    
    try:
        from optimization.q_learning import QLearningOptimizer
        print("✓ Q-Learning optimizer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Q-Learning optimizer: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration values"""
    print("\nTesting configuration...")
    
    from config import DATABASE_CONFIG, WAREHOUSE_CONFIG, QL_CONFIG
    
    # Test database config
    print(f"✓ Available database types: {list(DATABASE_CONFIG.keys())}")
    print(f"✓ Warehouse zones: {WAREHOUSE_CONFIG['zones']}")
    print(f"✓ Priority levels: {WAREHOUSE_CONFIG['priority_levels']}")
    print(f"✓ Q-Learning parameters: {list(QL_CONFIG.keys())}")
    
    return True

def test_database_factory():
    """Test database factory functionality"""
    print("\nTesting database factory...")
    
    from database.factory import DatabaseFactory
    
    # Test available types
    available_types = DatabaseFactory.get_available_types()
    print(f"✓ Available database types: {available_types}")
    
    # Test SQLite creation
    try:
        sqlite_db = DatabaseFactory.create_database('sqlite')
        print("✓ SQLite database created successfully")
    except Exception as e:
        print(f"✗ Failed to create SQLite database: {e}")
        return False
    
    # Test MongoDB creation
    try:
        mongo_db = DatabaseFactory.create_database('mongodb')
        print("✓ MongoDB database created successfully")
    except Exception as e:
        print(f"✗ Failed to create MongoDB database: {e}")
        return False
    
    return True

def test_q_learning():
    """Test Q-Learning optimizer"""
    print("\nTesting Q-Learning optimizer...")
    
    from optimization.q_learning import QLearningOptimizer
    
    try:
        optimizer = QLearningOptimizer()
        print("✓ Q-Learning optimizer created successfully")
        
        # Test optimization stats
        stats = optimizer.get_optimization_stats()
        print(f"✓ Optimization stats: {stats}")
        
        # Test with sample data
        sample_products = [
            {'id': 'P1', 'zone': 'Zone1', 'priority': 'urgent', 'quantity': 5},
            {'id': 'P2', 'zone': 'Zone2', 'priority': 'normal', 'quantity': 10},
            {'id': 'P3', 'zone': 'Zone3', 'priority': 'low', 'quantity': 3}
        ]
        
        route, distance = optimizer.optimize_route(sample_products, 'Zone1')
        print(f"✓ Route optimization completed: {route}")
        print(f"✓ Total distance: {distance:.2f}")
        
    except Exception as e:
        print(f"✗ Q-Learning test failed: {e}")
        return False
    
    return True

def test_sample_data_creation():
    """Test sample data creation"""
    print("\nTesting sample data creation...")
    
    try:
        # Import pandas to check if it's available
        import pandas as pd
        print("✓ Pandas available for Excel operations")
        
        # Test if we can create sample data
        from create_sample_data import create_sample_products
        
        products = create_sample_products()
        print(f"✓ Sample products created: {len(products)} products")
        
        # Test first product structure
        first_product = products[0]
        required_fields = ['id', 'name', 'zone', 'location', 'quantity', 'priority', 'price']
        for field in required_fields:
            if field not in first_product:
                print(f"✗ Missing field in product: {field}")
                return False
        
        print("✓ Product structure is correct")
        
    except ImportError as e:
        print(f"⚠ Pandas not available: {e}")
        print("  Excel import/export functionality will not work")
        return True  # Not a critical failure
    
    except Exception as e:
        print(f"✗ Sample data creation failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Warehouse Management System - System Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database Factory", test_database_factory),
        ("Q-Learning", test_q_learning),
        ("Sample Data", test_sample_data_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "="*50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create sample data: python create_sample_data.py")
        print("3. Launch GUI: python main.py --gui")
        print("4. Or run command line: python main.py --help")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())



