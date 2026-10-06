import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
                             QFileDialog, QLineEdit, QSpinBox, QTextEdit, QGroupBox,
                             QGridLayout, QHeaderView, QProgressBar, QCheckBox, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon

from database.factory import DatabaseFactory
from optimization.q_learning import QLearningOptimizer
from config import WAREHOUSE_CONFIG

class OptimizationWorker(QThread):
    """Worker thread for route optimization"""
    finished = pyqtSignal(tuple)
    progress = pyqtSignal(int)
    
    def __init__(self, optimizer, products, start_zone, final_dest, algorithm, timeout):
        super().__init__()
        self.optimizer = optimizer
        self.products = products
        self.start_zone = start_zone
        self.final_dest = final_dest
        self.algorithm = algorithm
        self.timeout = timeout
    
    def run(self):
        try:
            if self.algorithm == 'Q-Learning':
                route, distance = self.optimizer.optimize_route(self.products, self.start_zone, self.timeout)
            elif self.algorithm == 'Greedy':
                route, distance = self.optimizer.greedy_route(self.products, self.start_zone)
            else:  # Hybrid
                route, distance = self.optimizer.hybrid_route(self.products, self.start_zone, self.timeout)
            
            # Ensure route ends at final destination
            if route and route[-1] != self.final_dest:
                route.append(self.final_dest)
            
            self.finished.emit((route, distance))
        except Exception as e:
            self.finished.emit(([], 0.0))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database = None
        self.optimizer = QLearningOptimizer()
        self.selected_waypoints = []
        self.init_ui()
        self.init_database()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Warehouse Management System - Advanced Route Optimization")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_database_tab()
        self.create_products_tab()
        self.create_orders_tab()
        self.create_optimization_tab()
        self.create_reports_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready - Advanced Route Optimization System")
        
    def create_database_tab(self):
        """Create database connection tab"""
        db_widget = QWidget()
        layout = QVBoxLayout(db_widget)
        
        # Database selection
        db_group = QGroupBox("Database Connection")
        db_layout = QGridLayout(db_group)
        
        db_layout.addWidget(QLabel("Database Type:"), 0, 0)
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(DatabaseFactory.get_available_types())
        db_layout.addWidget(self.db_type_combo, 0, 1)
        
        # Connection button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_database)
        db_layout.addWidget(self.connect_btn, 0, 2)
        
        # Status label
        self.db_status_label = QLabel("Not connected")
        self.db_status_label.setStyleSheet("color: red;")
        db_layout.addWidget(self.db_status_label, 1, 0, 1, 3)
        
        layout.addWidget(db_group)
        
        # Import/Export section
        import_group = QGroupBox("Data Import/Export")
        import_layout = QHBoxLayout(import_group)
        
        self.import_btn = QPushButton("Import from Excel")
        self.import_btn.clicked.connect(self.import_from_excel)
        import_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("Export to Excel")
        self.export_btn.clicked.connect(self.export_to_excel)
        import_layout.addWidget(self.export_btn)
        
        layout.addWidget(import_group)
        
        self.tab_widget.addTab(db_widget, "Database")
        
    def create_products_tab(self):
        """Create products management tab"""
        products_widget = QWidget()
        layout = QVBoxLayout(products_widget)
        
        # Product controls
        controls_layout = QHBoxLayout()
        
        self.add_product_btn = QPushButton("Add Product")
        self.add_product_btn.clicked.connect(self.add_product)
        controls_layout.addWidget(self.add_product_btn)
        
        self.refresh_products_btn = QPushButton("Refresh")
        self.refresh_products_btn.clicked.connect(self.refresh_products)
        controls_layout.addWidget(self.refresh_products_btn)
        
        layout.addLayout(controls_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Name", "Zone", "Location", "Quantity", "Priority", "Price"
        ])
        
        # Set table properties
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.products_table)
        
        self.tab_widget.addTab(products_widget, "Products")
        
    def create_orders_tab(self):
        """Create orders management tab"""
        orders_widget = QWidget()
        layout = QVBoxLayout(orders_widget)
        
        # Order controls
        controls_layout = QHBoxLayout()
        
        self.add_order_btn = QPushButton("Add Order")
        self.add_order_btn.clicked.connect(self.add_order)
        controls_layout.addWidget(self.add_order_btn)
        
        self.refresh_orders_btn = QPushButton("Refresh")
        self.refresh_orders_btn.clicked.connect(self.refresh_orders)
        controls_layout.addWidget(self.refresh_orders_btn)
        
        layout.addLayout(controls_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels([
            "ID", "Customer", "Status", "Priority", "Total Amount", "Created"
        ])
        
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.orders_table)
        
        self.tab_widget.addTab(orders_widget, "Orders")
        
    def create_optimization_tab(self):
        """Create route optimization tab with full control over route planning"""
        optimization_widget = QWidget()
        layout = QVBoxLayout(optimization_widget)
        
        # Route Planning Controls
        route_group = QGroupBox("Route Planning")
        route_layout = QGridLayout(route_group)
        
        # Start Zone
        route_layout.addWidget(QLabel("Start Zone:"), 0, 0)
        self.start_zone_combo = QComboBox()
        self.start_zone_combo.addItems(WAREHOUSE_CONFIG['zones'])
        route_layout.addWidget(self.start_zone_combo, 0, 1)
        
        # Final Destination
        route_layout.addWidget(QLabel("Final Destination:"), 0, 2)
        self.final_dest_combo = QComboBox()
        self.final_dest_combo.addItems(WAREHOUSE_CONFIG['zones'])
        self.final_dest_combo.setCurrentText('Zone5')  # Default to end zone
        route_layout.addWidget(self.final_dest_combo, 0, 3)
        
        # Waypoints Selection
        route_layout.addWidget(QLabel("Waypoints (Zones to Visit):"), 1, 0)
        waypoints_layout = QHBoxLayout()
        
        self.waypoints_list = []
        for zone in WAREHOUSE_CONFIG['zones']:
            checkbox = QCheckBox(zone)
            checkbox.setChecked(True)  # All zones selected by default
            checkbox.stateChanged.connect(self.update_waypoints)
            self.waypoints_list.append(checkbox)
            waypoints_layout.addWidget(checkbox)
        
        route_layout.addLayout(waypoints_layout, 1, 1, 1, 3)
        
        # Products per Zone Selection
        route_layout.addWidget(QLabel("Products to Pick per Zone:"), 2, 0)
        
        # Create a scrollable area for per-zone product control
        products_control_widget = QWidget()
        products_control_layout = QVBoxLayout(products_control_widget)
        
        # Global products per zone (default)
        global_layout = QHBoxLayout()
        global_layout.addWidget(QLabel("Global (all zones):"))
        self.global_products_spin = QSpinBox()
        self.global_products_spin.setRange(1, 20)
        self.global_products_spin.setValue(3)
        self.global_products_spin.setToolTip("Default number of products for all zones")
        self.global_products_spin.valueChanged.connect(self.update_zone_products)
        global_layout.addWidget(self.global_products_spin)
        global_layout.addStretch()
        products_control_layout.addLayout(global_layout)
        
        # Individual zone control
        products_control_layout.addWidget(QLabel("Individual Zone Control:"))
        self.zone_products_spins = {}
        for zone in WAREHOUSE_CONFIG['zones']:
            zone_layout = QHBoxLayout()
            zone_layout.addWidget(QLabel(f"{zone}:"))
            spin = QSpinBox()
            spin.setRange(0, 50)  # Allow 0 to skip zones
            spin.setValue(3)  # Default value
            spin.setToolTip(f"Number of products to pick from {zone}")
            self.zone_products_spins[zone] = spin
            zone_layout.addWidget(spin)
            zone_layout.addStretch()
            products_control_layout.addLayout(zone_layout)
        
        # Apply global button
        apply_global_btn = QPushButton("Apply Global to All Zones")
        apply_global_btn.clicked.connect(self.apply_global_to_zones)
        products_control_layout.addWidget(apply_global_btn)
        
        route_layout.addWidget(products_control_widget, 2, 1, 1, 3)
        
        # Priority Filter
        route_layout.addWidget(QLabel("Priority Filter:"), 3, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['All', 'urgent', 'normal', 'low'])
        route_layout.addWidget(self.priority_combo, 3, 1)
        
        layout.addWidget(route_group)
        
        # Optimization Controls
        controls_group = QGroupBox("Optimization Settings")
        controls_layout = QGridLayout(controls_group)
        
        # Algorithm Selection
        controls_layout.addWidget(QLabel("Algorithm:"), 0, 0)
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(['Q-Learning', 'Greedy', 'Hybrid'])
        controls_layout.addWidget(self.algorithm_combo, 0, 1)
        
        # Timeout Setting
        controls_layout.addWidget(QLabel("Timeout (seconds):"), 0, 2)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(5)
        controls_layout.addWidget(self.timeout_spin, 0, 3)
        
        # Optimize Button
        self.optimize_btn = QPushButton("🚀 Optimize Route")
        self.optimize_btn.setStyleSheet("QPushButton { font-size: 14px; font-weight: bold; padding: 10px; }")
        self.optimize_btn.clicked.connect(self.optimize_route)
        controls_layout.addWidget(self.optimize_btn, 1, 0, 1, 4)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar, 2, 0, 1, 4)
        
        layout.addWidget(controls_group)
        
        # Results Display
        results_group = QGroupBox("Optimization Results")
        results_layout = QVBoxLayout(results_group)
        
        # Route Summary
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(QLabel("Route Summary:"))
        self.route_summary_label = QLabel("No route calculated yet")
        self.route_summary_label.setStyleSheet("QLabel { font-weight: bold; color: blue; }")
        summary_layout.addWidget(self.route_summary_label)
        summary_layout.addStretch()
        results_layout.addLayout(summary_layout)
        
        # Detailed Results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text)
        
        # Route Visualization
        route_viz_group = QGroupBox("Route Visualization")
        route_viz_layout = QVBoxLayout(route_viz_group)
        
        self.route_visualization = QTextEdit()
        self.route_visualization.setReadOnly(True)
        self.route_visualization.setMaximumHeight(150)
        self.route_visualization.setStyleSheet("QTextEdit { font-family: monospace; font-size: 12px; }")
        route_viz_layout.addWidget(self.route_visualization)
        
        results_layout.addWidget(route_viz_group)
        
        layout.addWidget(results_group)
        
        self.tab_widget.addTab(optimization_widget, "Route Optimization")
        
        # Initialize waypoints and zone products
        self.update_waypoints()
        self.update_zone_products()
        
    def create_reports_tab(self):
        """Create reports tab"""
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)
        
        # Report controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Year:"))
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(2024)
        controls_layout.addWidget(self.year_spin)
        
        controls_layout.addWidget(QLabel("Month:"))
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(12)
        controls_layout.addWidget(self.month_spin)
        
        self.generate_report_btn = QPushButton("Generate Report")
        self.generate_report_btn.clicked.connect(self.generate_report)
        controls_layout.addWidget(self.generate_report_btn)
        
        layout.addLayout(controls_layout)
        
        # Report display
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)
        
        self.tab_widget.addTab(reports_widget, "Reports")
        
    def update_waypoints(self):
        """Update the list of selected waypoints"""
        self.selected_waypoints = [checkbox.text() for checkbox in self.waypoints_list if checkbox.isChecked()]
        if len(self.selected_waypoints) < 2:
            self.optimize_btn.setEnabled(False)
            self.optimize_btn.setToolTip("Select at least 2 zones for optimization")
        else:
            self.optimize_btn.setEnabled(True)
            self.optimize_btn.setToolTip("Click to optimize the selected route")
    
    def update_zone_products(self):
        """Update individual zone product counts when global value changes"""
        global_value = self.global_products_spin.value()
        for zone, spin in self.zone_products_spins.items():
            if spin.value() == 0:  # Don't change zones set to 0
                continue
            spin.setValue(global_value)
    
    def apply_global_to_zones(self):
        """Apply the global product count to all zones"""
        global_value = self.global_products_spin.value()
        for zone, spin in self.zone_products_spins.items():
            spin.setValue(global_value)
    
    def get_route_products(self):
        """Get products for each selected zone based on individual zone settings"""
        products = []
        priority_filter = self.priority_combo.currentText()
        
        for zone in self.selected_waypoints:
            # Get the specific product count for this zone
            products_per_zone = self.zone_products_spins[zone].value()
            
            if products_per_zone == 0:
                continue  # Skip zones with 0 products
            
            zone_products = self.database.get_products_by_zone(zone)
            
            # Apply priority filter
            if priority_filter != 'All':
                zone_products = [p for p in zone_products if p.get('priority') == priority_filter]
            
            # Take the specified number of products from this zone
            selected_products = zone_products[:products_per_zone]
            
            for product in selected_products:
                products.append({
                    'id': product['id'],
                    'name': product['name'],
                    'zone': product['zone'],
                    'location': product.get('location', 'A1'),
                    'priority': product.get('priority', 'normal'),
                    'quantity': product.get('quantity', 1),
                    'price': product.get('price', 0.0)
                })
        
        return products
    
    def create_route_visualization(self, route, products):
        """Create a visual representation of the route"""
        if not route:
            return "No route available"
        
        viz = "ROUTE MAP:\n"
        viz += "=" * 50 + "\n"
        
        for i, zone in enumerate(route):
            # Find products in this zone
            zone_products = [p for p in products if p['zone'] == zone]
            
            viz += f"📍 {zone} (Step {i+1})\n"
            if zone_products:
                viz += "   Products to pick:\n"
                for product in zone_products:
                    viz += f"   • {product['name']} (ID: {product['id']}) - {product['location']}\n"
            else:
                viz += "   (Transit zone - no products)\n"
            viz += "\n"
        
        viz += "=" * 50 + "\n"
        viz += f"Total Zones: {len(route)} | Total Products: {len(products)}"
        
        return viz
        
    def init_database(self):
        """Initialize database connection"""
        try:
            # Default to SQLite for now
            self.database = DatabaseFactory.create_database('sqlite')
            if self.database.connect():
                self.database.create_tables()
                self.db_status_label.setText("Connected to SQLite")
                self.db_status_label.setStyleSheet("color: green;")
                self.statusBar().showMessage("Database connected successfully")
            else:
                self.db_status_label.setText("Connection failed")
                self.statusBar().showMessage("Database connection failed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize database: {e}")
    
    def connect_database(self):
        """Connect to selected database"""
        try:
            db_type = self.db_type_combo.currentText()
            
            if self.database:
                self.database.disconnect()
            
            self.database = DatabaseFactory.create_database(db_type)
            if self.database.connect():
                self.database.create_tables()
                self.db_status_label.setText(f"Connected to {db_type}")
                self.db_status_label.setStyleSheet("color: green;")
                self.statusBar().showMessage(f"Connected to {db_type} successfully")
                
                # Refresh data
                self.refresh_products()
                self.refresh_orders()
            else:
                self.db_status_label.setText("Connection failed")
                self.statusBar().showMessage("Database connection failed")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to database: {e}")
    
    def import_from_excel(self):
        """Import data from Excel file"""
        if not self.database:
            QMessageBox.warning(self, "Warning", "Please connect to a database first")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            try:
                if self.database.import_from_excel(file_path):
                    QMessageBox.information(self, "Success", "Data imported successfully")
                    self.refresh_products()
                else:
                    QMessageBox.warning(self, "Warning", "Failed to import data")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Import failed: {e}")
    
    def export_to_excel(self):
        """Export data to Excel file"""
        if not self.database:
            QMessageBox.warning(self, "Warning", "Please connect to a database first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File", "", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                # Export products data
                products = self.database.get_products_by_zone("Zone1")  # Get all products
                if self.database.export_to_excel(products, file_path):
                    QMessageBox.information(self, "Success", "Data exported successfully")
                else:
                    QMessageBox.warning(self, "Warning", "Failed to export data")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {e}")
    
    def add_product(self):
        """Add a new product"""
        # This would open a dialog for adding products
        QMessageBox.information(self, "Info", "Add Product functionality to be implemented")
    
    def refresh_products(self):
        """Refresh products table"""
        if not self.database:
            return
        
        try:
            # Get products from all zones
            all_products = []
            for zone in WAREHOUSE_CONFIG['zones']:
                zone_products = self.database.get_products_by_zone(zone)
                all_products.extend(zone_products)
            
            self.products_table.setRowCount(len(all_products))
            
            for row, product in enumerate(all_products):
                self.products_table.setItem(row, 0, QTableWidgetItem(product.get('id', '')))
                self.products_table.setItem(row, 1, QTableWidgetItem(product.get('name', '')))
                self.products_table.setItem(row, 2, QTableWidgetItem(product.get('zone', '')))
                self.products_table.setItem(row, 3, QTableWidgetItem(product.get('location', '')))
                self.products_table.setItem(row, 4, QTableWidgetItem(str(product.get('quantity', 0))))
                self.products_table.setItem(row, 5, QTableWidgetItem(product.get('priority', '')))
                self.products_table.setItem(row, 6, QTableWidgetItem(str(product.get('price', 0.0))))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh products: {e}")
    
    def add_order(self):
        """Add a new order"""
        QMessageBox.information(self, "Info", "Add Order functionality to be implemented")
    
    def refresh_orders(self):
        """Refresh orders table"""
        if not self.database:
            return
        
        try:
            orders = self.database.get_pending_orders()
            self.orders_table.setRowCount(len(orders))
            
            for row, order in enumerate(orders):
                self.orders_table.setItem(row, 0, QTableWidgetItem(order.get('id', '')))
                self.orders_table.setItem(row, 1, QTableWidgetItem(order.get('customer_name', '')))
                self.orders_table.setItem(row, 2, QTableWidgetItem(order.get('status', '')))
                self.orders_table.setItem(row, 3, QTableWidgetItem(order.get('priority', '')))
                self.orders_table.setItem(row, 4, QTableWidgetItem(str(order.get('total_amount', 0.0))))
                self.orders_table.setItem(row, 5, QTableWidgetItem(str(order.get('created_at', ''))))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh orders: {e}")
    
    def optimize_route(self):
        """Optimize picking route with full user control"""
        if not self.database:
            QMessageBox.warning(self, "Warning", "Please connect to a database first")
            return
        
        try:
            # Get products based on user selection
            products = self.get_route_products()
            if not products:
                QMessageBox.warning(self, "Warning", "No products found for the selected zones and criteria")
                return
            
            start_zone = self.start_zone_combo.currentText()
            final_dest = self.final_dest_combo.currentText()
            algorithm = self.algorithm_combo.currentText()
            timeout = self.timeout_spin.value()
            
            # Update UI
            self.optimize_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Show optimization info
            self.results_text.setText(f"Starting {algorithm} optimization...\n"
                                    f"Start: {start_zone} → End: {final_dest}\n"
                                    f"Zones: {', '.join(self.selected_waypoints)}\n"
                                    f"Products: {len(products)} items\n"
                                    f"Timeout: {timeout}s")
            
            # Run optimization in background
            self.worker = OptimizationWorker(self.optimizer, products, start_zone, final_dest, algorithm, timeout)
            self.worker.finished.connect(self.optimization_finished)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Optimization failed: {e}")
            self.optimize_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def optimization_finished(self, result):
        """Handle optimization completion"""
        self.progress_bar.setVisible(False)
        self.optimize_btn.setEnabled(True)
        
        route, distance = result
        if route:
            # Update route summary
            self.route_summary_label.setText(f"✅ Route Found: {len(route)} zones, {distance:.2f} units")
            
            # Show detailed results
            results_text = f"🎯 OPTIMIZATION COMPLETED SUCCESSFULLY!\n"
            results_text += "=" * 50 + "\n\n"
            results_text += f"Algorithm: {self.algorithm_combo.currentText()}\n"
            results_text += f"Start Zone: {self.start_zone_combo.currentText()}\n"
            results_text += f"Final Destination: {self.final_dest_combo.currentText()}\n"
            results_text += f"Total Distance: {distance:.2f} units\n"
            results_text += f"Zones Visited: {len(route)}\n\n"
            results_text += f"Optimal Route:\n{' → '.join(route)}\n\n"
            results_text += f"Products to Pick: {len(self.get_route_products())} items"
            
            self.results_text.setText(results_text)
            
            # Create route visualization
            products = self.get_route_products()
            viz_text = self.create_route_visualization(route, products)
            self.route_visualization.setText(viz_text)
            
            self.statusBar().showMessage(f"Route optimization completed - {len(route)} zones, {distance:.2f} units")
        else:
            self.route_summary_label.setText("❌ Optimization Failed")
            self.results_text.setText("Route optimization failed. Please try different parameters or check the database.")
            self.route_visualization.setText("No route available")
            self.statusBar().showMessage("Route optimization failed")
    
    def generate_report(self):
        """Generate monthly report"""
        if not self.database:
            QMessageBox.warning(self, "Warning", "Please connect to a database first")
            return
        
        try:
            year = self.year_spin.value()
            month = self.month_spin.value()
            
            report_data = self.database.get_monthly_report(year, month)
            
            if report_data:
                report_text = f"Monthly Report - {year}/{month:02d}\n"
                report_text += "=" * 40 + "\n\n"
                
                # Products section
                products = report_data.get('products', {})
                report_text += f"Products:\n"
                report_text += f"  Total: {products.get('total_products', 0)}\n"
                report_text += f"  In Stock: {products.get('in_stock', 0)}\n"
                report_text += f"  Out of Stock: {products.get('out_of_stock', 0)}\n\n"
                
                # Financial section
                financial = report_data.get('financial', {})
                report_text += f"Financial:\n"
                report_text += f"  Income: ${financial.get('total_income', 0):.2f}\n"
                report_text += f"  Expenses: ${financial.get('total_expenses', 0):.2f}\n"
                report_text += f"  Net: ${financial.get('total_income', 0) - financial.get('total_expenses', 0):.2f}\n\n"
                
                # Shipments section
                shipments = report_data.get('shipments', {})
                report_text += f"Shipments:\n"
                report_text += f"  Total: {shipments.get('total_shipments', 0)}\n"
                report_text += f"  Delivered: {shipments.get('delivered', 0)}\n"
                report_text += f"  Pending: {shipments.get('pending', 0)}\n"
                
                self.report_text.setText(report_text)
                self.statusBar().showMessage("Report generated successfully")
            else:
                self.report_text.setText("No data available for the selected period")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
