@echo off
cd /d "%~dp0"
echo Starting Python Backend Server...
py -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8088
pause
