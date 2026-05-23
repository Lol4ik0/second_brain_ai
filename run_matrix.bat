@echo off
title Second Brain Global Startup Matrix
cls

echo =====================================================================
echo INITIALIZING SECOND BRAIN CORE INFRASTRUCTURE MATRIX
echo =====================================================================
echo.

:: 1. Launch Tailwind CSS Watcher Engine
echo Sector 1: Powering up Tailwind CSS Compilation Grid...
start cmd /k "cd ai_manager && npm run dev"

:: 2. Launch Django Server Engine
echo Sector 2: Activating Django Secure Data Layer...
start cmd /k "venv\Scripts\activate && cd ai_manager && python manage.py runserver"

:: 3. Launch Cloudflare Tunnel Network
echo Sector 3: Establishing Cloudflare Security Tunnel Portal...
start cmd /k "cd ai_manager && cloudflared tunnel --url http://127.0.0.1:8000"

echo.
echo =====================================================================
echo ALL SYSTEMS OPERATIONAL! PROCEED TO LINK MATRIX IN YOUR MOBILE TERMINAL.
echo [Close the individual terminal windows to terminate server nodes]
echo =====================================================================
echo.
pause