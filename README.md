# Warehouse Management System

A comprehensive warehouse management system built with Python, featuring Q-Learning route optimization, multiple database support, and a modern PyQt5 GUI.

## Features

### 🏗️ Core Functionality
- **Product Management**: Track products across multiple warehouse zones
- **Order Management**: Handle customer orders with priority levels
- **Shipment Tracking**: Monitor product shipments and delivery status
- **Financial Tracking**: Record income, expenses, and generate financial reports
- **Real-time Stock Monitoring**: Track inventory levels across all zones

### 🧠 AI-Powered Optimization
- **Q-Learning Route Optimization**: Intelligent picking route optimization
- **Priority-based Planning**: Consider product urgency and quantity
- **Distance Minimization**: Reduce travel time between warehouse zones
- **Performance Constraints**: Meet 2-second optimization time limit

### 🗄️ Database Support
- **SQLite**: Lightweight, file-based database (default)
- **MongoDB**: NoSQL database for flexible data storage
- **MySQL**: Relational database for enterprise use
- **PostgreSQL**: Advanced relational database
- **Excel Import/Export**: Easy data migration and reporting

### 🖥️ User Interface
- **Modern PyQt5 GUI**: Professional desktop application
- **Tabbed Interface**: Organized workflow management
- **Real-time Updates**: Live data refresh and status monitoring
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd warehouse-management-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Launch GUI
   python main.py --gui
   
   # Or run in command line mode
   python main.py --help
   ```

## Usage

### GUI Mode
Launch the full graphical interface:
```bash
python main.py --gui
```

The GUI provides:
- **Database Tab**: Connect to different database types and import/export data
- **Products Tab**: Manage warehouse inventory and product information
- **Orders Tab**: Handle customer orders and track order status
- **Route Optimization Tab**: Run AI-powered picking route optimization
- **Reports Tab**: Generate monthly reports and analytics

### Command Line Mode
Run specific operations from the command line:

```bash
# Import data from Excel
python main.py --import-excel data.xlsx

# Export data to Excel
python main.py --export-excel export.xlsx

# Run route optimization
python main.py --optimize-route

# Generate monthly report
python main.py --generate-report --year 2024 --month 12

# Use specific database
python main.py --db-type mongodb --optimize-route
```

### Database Configuration
Configure database connections in `config.py` or use environment variables:

```bash
# MongoDB
export MONGO_HOST=localhost
export MONGO_PORT=27017
export MONGO_DB=warehouse

# MySQL
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DB=warehouse
export MYSQL_USER=root
export MYSQL_PASSWORD=0000
```

## System Architecture

### Database Layer
- **Abstract Interface**: Unified API for all database types
- **Factory Pattern**: Easy switching between database implementations
- **Data Validation**: Schema validation and data integrity checks

### Optimization Engine
- **Q-Learning Algorithm**: Reinforcement learning for route optimization
- **State Management**: Efficient warehouse state representation
- **Performance Monitoring**: Real-time optimization metrics

### GUI Framework
- **PyQt5**: Modern, responsive desktop interface
- **Multi-threading**: Background optimization without UI blocking
- **Event-driven**: Real-time updates and user interaction

## Configuration

### Warehouse Settings
Modify `config.py` to customize:
- Warehouse zones and capacities
- Priority levels and weights
- Optimization parameters
- Database connection settings

### Q-Learning Parameters
Adjust optimization behavior:
```python
QL_CONFIG = {
    'learning_rate': 0.1,      # How fast the AI learns
    'discount_factor': 0.9,    # Future reward importance
    'epsilon': 0.1,            # Exploration vs exploitation balance
    'max_iterations': 1000     # Maximum optimization iterations
}
```

## Data Import/Export

### Excel Format
The system expects Excel files with these columns:
- `id` or `ID`: Product identifier
- `name` or `Name`: Product name
- `zone` or `Zone`: Warehouse zone (Zone1, Zone2, etc.)
- `location` or `Location`: Specific location within zone
- `quantity` or `Quantity`: Available quantity
- `priority` or `Priority`: Priority level (urgent, normal, low)
- `price` or `Price`: Product price

### Sample Data
Create sample data for testing:
```python
import pandas as pd

sample_data = {
    'id': ['P001', 'P002', 'P003'],
    'name': ['Laptop', 'Mouse', 'Keyboard'],
    'zone': ['Zone1', 'Zone2', 'Zone1'],
    'location': ['A1', 'B2', 'A3'],
    'quantity': [10, 50, 25],
    'priority': ['urgent', 'normal', 'low'],
    'price': [999.99, 29.99, 79.99]
}

df = pd.DataFrame(sample_data)
df.to_excel('sample_data.xlsx', index=False)
```

## Performance

### Optimization Speed
- **Target**: < 2 seconds for 100 orders
- **Q-Learning**: Intelligent route planning
- **Fallback**: Greedy algorithm for timeouts
- **Caching**: Q-table persistence between runs

### Database Performance
- **Indexing**: Optimized queries for large datasets
- **Connection Pooling**: Efficient database connections
- **Batch Operations**: Bulk import/export operations

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database service is running
   - Verify connection parameters in config.py
   - Ensure proper permissions

2. **Optimization Timeout**
   - Reduce max_iterations in QL_CONFIG
   - Check warehouse zone complexity
   - Monitor system resources

3. **Import/Export Errors**
   - Verify Excel file format
   - Check file permissions
   - Ensure database is connected

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Project Structure
```
warehouse-management-system/
├── config.py              # Configuration settings
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
├── database/            # Database implementations
│   ├── __init__.py
│   ├── base.py         # Abstract interface
│   ├── sqlite_db.py    # SQLite implementation
│   ├── mongodb_db.py   # MongoDB implementation
│   └── factory.py      # Database factory
├── optimization/        # AI optimization
│   ├── __init__.py
│   └── q_learning.py   # Q-Learning algorithm
├── gui/                # User interface
│   ├── __init__.py
│   └── main_window.py  # Main GUI window
└── reports/            # Generated reports
```

### Adding New Features
1. **Database Support**: Implement DatabaseInterface in new file
2. **Optimization Algorithms**: Extend QLearningOptimizer
3. **GUI Components**: Add new tabs to MainWindow
4. **Reports**: Create new report generators

### Testing
```bash
# Run basic tests
python -m pytest tests/

# Test specific components
python -m pytest tests/test_optimization.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting section

## Roadmap

### Future Features
- **Machine Learning**: Enhanced prediction models
- **Mobile App**: iOS/Android companion app
- **Cloud Integration**: Multi-warehouse management
- **API**: RESTful API for external integrations
- **Analytics**: Advanced reporting and dashboards

---

**Built with ❤️ using Python, PyQt5, and AI optimization**



