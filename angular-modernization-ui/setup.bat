@echo off
echo ============================================
echo Legacy Code Modernization Platform Setup
echo ============================================
echo.

echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js found!
node --version
echo.

echo [2/4] Installing Angular dependencies...
cd angular-modernization-ui
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo [3/4] Updating backend agents...
if exist updated-agents (
    echo Copying updated agent files...
    copy /Y updated-agents\*.py ..\agents\
    echo Backend agents updated!
) else (
    echo Warning: updated-agents directory not found, skipping...
)
echo.

echo [4/4] Setup complete!
echo.
echo ============================================
echo Next Steps:
echo ============================================
echo 1. Start the backend:
echo    cd backend
echo    uvicorn main:app --reload
echo.
echo 2. Start the Angular app (in a new terminal):
echo    cd angular-modernization-ui
echo    npm start
echo.
echo 3. Open http://localhost:4200 in your browser
echo ============================================
echo.
pause
