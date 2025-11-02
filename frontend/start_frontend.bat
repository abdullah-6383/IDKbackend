@echo off
REM Frontend startup script for Information Trust Analysis System (Windows)

echo 🎨 Starting Information Trust Analysis Frontend
echo ================================================

REM Check if we're in the frontend directory
if not exist "index.html" (
    echo ❌ Error: Please run this script from the frontend directory
    echo    cd frontend && start_frontend.bat
    exit /b 1
)

if not exist "package.json" (
    echo ❌ Error: Please run this script from the frontend directory
    echo    cd frontend && start_frontend.bat
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    echo    Visit: https://nodejs.org/
    pause
    exit /b 1
)

echo 🔧 Installing dependencies...
npm install

echo.
echo 🚀 Starting frontend server on port 3000...
echo 📝 Make sure backend is running on port 8000
echo    Backend: cd ..\backend ^&^& python start_backend.py
echo.
echo 🌐 Frontend will be available at:
echo    http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

npm start