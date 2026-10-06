@echo off
echo Warehouse Management System
echo ===========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Dependencies installed successfully!
echo.
echo Choose an option:
echo 1. Launch GUI Application
echo 2. Run System Test
echo 3. Create Sample Data
echo 4. Command Line Mode
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Launching GUI...
    python main.py --gui
) else if "%choice%"=="2" (
    echo Running system test...
    python test_system.py
) else if "%choice%"=="3" (
    echo Creating sample data...
    python create_sample_data.py
) else if "%choice%"=="4" (
    echo Command line mode...
    python main.py --help
    echo.
    echo Use 'python main.py --help' for more options
) else if "%choice%"=="5" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
)

echo.
pause



