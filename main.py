#!/usr/bin/env python3
"""
Warehouse Management System
Main entry point for the application
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for the warehouse management system"""
    parser = argparse.ArgumentParser(description='Warehouse Management System')
    parser.add_argument('--gui', action='store_true', help='Launch GUI application')
    parser.add_argument('--db-type', choices=['sqlite', 'mongodb', 'mysql', 'postgresql'], 
                       default='sqlite', help='Database type to use')
    parser.add_argument('--import-excel', type=str, help='Import data from Excel file')
    parser.add_argument('--export-excel', type=str, help='Export data to Excel file')
    parser.add_argument('--optimize-route', action='store_true', help='Run route optimization')
    parser.add_argument('--generate-report', action='store_true', help='Generate monthly report')
    parser.add_argument('--year', type=int, default=2024, help='Year for report generation')
    parser.add_argument('--month', type=int, default=12, help='Month for report generation')
    
    args = parser.parse_args()
    
    try:
        if args.gui:
            # Launch GUI application
            from gui.main_window import main as gui_main
            gui_main()
        else:
            # Command line mode
            run_command_line(args)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def run_command_line(args):
    """Run the application in command line mode"""
    print("Warehouse Management System - Command Line Mode")
    print("=" * 50)
    
    # Initialize database
    from database.factory import DatabaseFactory
    from optimization.q_learning import QLearningOptimizer
    
    try:
        print(f"Connecting to {args.db_type} database...")
        database = DatabaseFactory.create_database(args.db_type)
        
        if not database.connect():
            print(f"Failed to connect to {args.db_type} database")
            return
        
        print("Database connected successfully")
        database.create_tables()
        
        # Import data if specified
        if args.import_excel:
            print(f"Importing data from {args.import_excel}...")
            if database.import_from_excel(args.import_excel):
                print("Data imported successfully")
            else:
                print("Failed to import data")
        
        # Export data if specified
        if args.export_excel:
            print(f"Exporting data to {args.export_excel}...")
            # Get sample data for export
            products = database.get_products_by_zone("Zone1")
            if database.export_to_excel(products, args.export_excel):
                print("Data exported successfully")
            else:
                print("Failed to export data")
        
        # Route optimization if specified
        if args.optimize_route:
            print("Running route optimization...")
            optimizer = QLearningOptimizer()
            
            # Get sample products for optimization
            products = []
            for zone in ['Zone1', 'Zone2', 'Zone3']:
                zone_products = database.get_products_by_zone(zone)
                for product in zone_products[:3]:  # Limit to 3 products per zone
                    products.append({
                        'id': product['id'],
                        'zone': product['zone'],
                        'priority': product.get('priority', 'normal'),
                        'quantity': product.get('quantity', 1)
                    })
            
            if products:
                route, distance = optimizer.optimize_route(products, "Zone1")
                print(f"Optimized route: {' -> '.join(route)}")
                print(f"Total distance: {distance:.2f} units")
            else:
                print("No products available for optimization")
        
        # Generate report if specified
        if args.generate_report:
            print(f"Generating monthly report for {args.year}/{args.month:02d}...")
            report_data = database.get_monthly_report(args.year, args.month)
            
            if report_data:
                print("\nMonthly Report:")
                print(f"Year: {report_data['year']}")
                print(f"Month: {report_data['month']}")
                
                products = report_data.get('products', {})
                print(f"\nProducts:")
                print(f"  Total: {products.get('total_products', 0)}")
                print(f"  In Stock: {products.get('in_stock', 0)}")
                print(f"  Out of Stock: {products.get('out_of_stock', 0)}")
                
                financial = report_data.get('financial', {})
                print(f"\nFinancial:")
                print(f"  Income: ${financial.get('total_income', 0):.2f}")
                print(f"  Expenses: ${financial.get('total_expenses', 0):.2f}")
                net = financial.get('total_income', 0) - financial.get('total_expenses', 0)
                print(f"  Net: ${net:.2f}")
                
                shipments = report_data.get('shipments', {})
                print(f"\nShipments:")
                print(f"  Total: {shipments.get('total_shipments', 0)}")
                print(f"  Delivered: {shipments.get('delivered', 0)}")
                print(f"  Pending: {shipments.get('pending', 0)}")
            else:
                print("No data available for the specified period")
        
        # If no specific action specified, show available options
        if not any([args.import_excel, args.export_excel, args.optimize_route, args.generate_report]):
            print("\nAvailable operations:")
            print("  --import-excel <file>  : Import data from Excel file")
            print("  --export-excel <file>  : Export data to Excel file")
            print("  --optimize-route       : Run route optimization")
            print("  --generate-report      : Generate monthly report")
            print("  --gui                  : Launch GUI application")
            print("\nUse --help for more information")
        
        # Cleanup
        database.disconnect()
        print("\nDatabase disconnected")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()



